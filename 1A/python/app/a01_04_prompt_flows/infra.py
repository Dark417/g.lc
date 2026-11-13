"""Bedrock Flows showcase (boto3): build on "bedrock-agent", run on "bedrock-agent-runtime".

- Order follows docs/01.04.prompt-flows.md: validate -> create -> prepare -> version -> alias -> invoke.
- Terraform owns a-flow; create_flow here shows the same definition as code.
- No AWS call at import time.
"""

import time
import uuid
from typing import Any

from botocore.exceptions import ClientError

from app.a01_04_prompt_flows.config import FlowsSettings, get_flows_settings
from app.a01_04_prompt_flows.domain import INPUT_NODE, INPUT_OUTPUT_NAME, FlowRun, build_summary_flow
from app.shared import aws
from app.shared.retry import backoff

STREAM_ERRORS = (
    "throttlingException",
    "validationException",
    "accessDeniedException",
    "resourceNotFoundException",
    "serviceQuotaExceededException",
    "conflictException",
    "dependencyFailedException",  # a node's dependency (model, Lambda, KB) failed
    "badGatewayException",
    "internalServerException",
)


class FlowError(Exception):
    pass


class FlowsShowcase:
    def __init__(self, settings: FlowsSettings | None = None) -> None:
        self.settings = settings or get_flows_settings()

    @property
    def agent(self) -> Any:
        return aws.client("bedrock-agent")

    @property
    def agent_runtime(self) -> Any:
        return aws.client("bedrock-agent-runtime")

    # ================================================================ 1.3 definition

    def validate_definition(self, definition: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Shows: ValidateFlowDefinition before create/update (run it in CI). Empty list = valid.
        Catch: validation checks wiring and types, not whether prompts produce good output.
        """
        resp = self.agent.validate_flow_definition(definition=definition or build_summary_flow(self.settings.model()))
        return resp.get("validations", [])  # [{"message", "severity": Error|Warning, "type", "details"}]

    def create_flow(self, name: str) -> dict[str, str]:
        """Shows: CreateFlow with executionRoleArn + definition (DRAFT). Same graph as Terraform's a-flow.
        Catch: the caller needs iam:PassRole on the execution role; the DRAFT must be prepared before use.
        """
        kwargs: dict[str, Any] = {
            "name": name,
            "description": "Input -> Prompt -> Output (created from Python)",
            "executionRoleArn": self.settings.execution_role_arn,
            "definition": build_summary_flow(self.settings.model()),
            "clientToken": str(uuid.uuid5(uuid.NAMESPACE_URL, f"flow/{name}")),  # idempotent create
            "tags": {"Component": "01.04"},
        }
        if self.settings.kms_key_arn:
            kwargs["customerEncryptionKeyArn"] = self.settings.kms_key_arn
        resp = self.agent.create_flow(**kwargs)
        return {"id": resp["id"], "arn": resp["arn"], "status": resp["status"]}  # status NotPrepared

    # ================================================================ 1.4 lifecycle

    def prepare_flow(self, flow_id: str | None = None) -> str:
        """Shows: PrepareFlow is async ⇒ poll GetFlow with backoff until Prepared or Failed.
        Use after every create/update. Catch: Failed carries "validations" with the reason.
        """
        fid = flow_id or self.settings.flow_id
        self.agent.prepare_flow(flowIdentifier=fid)
        deadline = time.monotonic() + self.settings.prepare_timeout_s
        attempt = 0
        while time.monotonic() < deadline:
            flow = self.agent.get_flow(flowIdentifier=fid)
            status = flow["status"]  # NotPrepared | Preparing | Prepared | Failed
            if status == "Prepared":
                return status
            if status == "Failed":
                raise FlowError(f"prepare failed: {flow.get('validations', [])}")
            time.sleep(max(0.5, backoff(attempt, base=0.5, cap=5.0)))
            attempt += 1
        raise FlowError(f"flow {fid} not prepared after {self.settings.prepare_timeout_s}s")

    def create_flow_version(self, flow_id: str | None = None, release_id: str = "") -> str:
        """Shows: CreateFlowVersion = immutable snapshot of the prepared DRAFT. Returns "1", "2", ...
        Catch: snapshot what was prepared; clientToken (from release_id) avoids duplicate versions on retry.
        """
        fid = flow_id or self.settings.flow_id
        kwargs: dict[str, Any] = {"flowIdentifier": fid, "description": f"release {release_id or 'manual'}"}
        if release_id:
            kwargs["clientToken"] = str(uuid.uuid5(uuid.NAMESPACE_URL, f"flow-version/{fid}/{release_id}"))
        return self.agent.create_flow_version(**kwargs)["version"]

    def create_flow_alias(self, version: str, name: str = "live", flow_id: str | None = None) -> dict[str, str]:
        """Shows: CreateFlowAlias pointing at one version, with optional concurrency control.
        Callers invoke the alias ID. Catch: routingConfiguration takes exactly one version (no weighted split).
        """
        fid = flow_id or self.settings.flow_id
        resp = self.agent.create_flow_alias(
            flowIdentifier=fid,
            name=name,
            routingConfiguration=[{"flowVersion": version}],
            # Manual caps parallel node executions per invocation (protects model TPM / Lambda concurrency).
            concurrencyConfiguration={"type": "Manual", "maxConcurrency": 2},  # or {"type": "Automatic"}
            clientToken=str(uuid.uuid5(uuid.NAMESPACE_URL, f"flow-alias/{fid}/{name}")),
        )
        return {"alias_id": resp["id"], "alias_arn": resp["arn"]}

    def point_alias(self, alias_id: str, version: str, name: str = "live", flow_id: str | None = None) -> None:
        """Shows: deploy and rollback = UpdateFlowAlias to another version; callers keep the same alias ID.
        Catch: UpdateFlowAlias replaces the routing config; name is required again.
        """
        self.agent.update_flow_alias(
            flowIdentifier=flow_id or self.settings.flow_id,
            aliasIdentifier=alias_id,
            name=name,
            routingConfiguration=[{"flowVersion": version}],
        )

    def list_flow_versions(self, flow_id: str | None = None) -> list[dict[str, str]]:
        """Shows: ListFlowVersions with the paginator (DRAFT appears as a version entry too)."""
        out: list[dict[str, str]] = []
        for page in self.agent.get_paginator("list_flow_versions").paginate(flowIdentifier=flow_id or self.settings.flow_id):
            out += [{"version": v["version"], "status": v["status"]} for v in page.get("flowVersionSummaries", [])]
        return out

    # ================================================================ 1.5 invoke

    def invoke_flow(self, document: str, alias_id: str | None = None, flow_id: str | None = None) -> FlowRun:
        """Shows: InvokeFlow on an alias; parses the event stream: flowOutputEvent (one per Output node),
        flowCompletionEvent (SUCCESS | INPUT_REQUIRED), flowMultiTurnInputRequestEvent, flowTraceEvent, errors.
        Catch: errors arrive inside the stream after HTTP 200; outputs seen before an error are partial.
        """
        try:
            resp = self.agent_runtime.invoke_flow(
                flowIdentifier=flow_id or self.settings.flow_id,
                flowAliasIdentifier=alias_id or self.settings.flow_alias_id,
                inputs=[
                    {
                        "nodeName": INPUT_NODE,
                        "nodeOutputName": INPUT_OUTPUT_NAME,  # the Input node's output
                        "content": {"document": document},  # must match the Input node's declared type
                    }
                ],
                enableTrace=self.settings.enable_trace,
                # executionId="...",  # continue a multi-turn execution after INPUT_REQUIRED
            )
        except ClientError as e:
            raise FlowError(f"{e.response['Error']['Code']}: {e.response['Error'].get('Message', '')}") from e

        run = FlowRun(execution_id=resp.get("executionId", ""))
        for event in resp["responseStream"]:
            if "flowOutputEvent" in event:
                out = event["flowOutputEvent"]
                run.outputs[out["nodeName"]] = out["content"]["document"]
            elif "flowCompletionEvent" in event:
                run.completion_reason = event["flowCompletionEvent"]["completionReason"]
            elif "flowMultiTurnInputRequestEvent" in event:
                req = event["flowMultiTurnInputRequestEvent"]
                run.input_request = {"node": req["nodeName"], "content": req["content"].get("document")}
            elif "flowTraceEvent" in event:
                run.traces.append(event["flowTraceEvent"]["trace"])
            else:
                for err in STREAM_ERRORS:
                    if err in event:
                        raise FlowError(f"{err}: {event[err].get('message', '')} (partial outputs: {list(run.outputs)})")
        return run
