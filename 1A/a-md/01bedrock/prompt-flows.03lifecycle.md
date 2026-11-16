# prompt-flows Lifecycle: Draft, Prepare, Version, Alias

> Edit the DRAFT, prepare it, snapshot a version, and deploy by moving an alias.

## Index

- [1. The Lifecycle](#1-the-lifecycle)
- [2. DRAFT And PrepareFlow](#2-draft-and-prepareflow)
- [3. Versions](#3-versions)
- [4. Aliases](#4-aliases)
  - [4.1 Create An Alias](#41-create-an-alias)
  - [4.2 Deploy And Rollback](#42-deploy-and-rollback)
- [5. One Release Call](#5-one-release-call)
- [6. The Test Alias](#6-the-test-alias)

Back to [00index](prompt-flows.00index.md).

---

## 1. The Lifecycle

A flow ships like a deployable artifact.

→ DRAFT (`UpdateFlow`)  
→ `PrepareFlow` (async)  
→ `CreateFlowVersion` (immutable snapshot)  
→ `CreateFlowAlias` / `UpdateFlowAlias` (what callers invoke)

## 2. DRAFT And PrepareFlow

- **DRAFT**: editable (`UpdateFlow`)
  - Must be prepared after each change
- **`PrepareFlow`**: async
  - Poll `GetFlow` until `Prepared`
  - Use after every create/update

```python
# app/infra/_01bedrock_04prompt_flows.py
def prepare_flow(self, flow_id: str | None = None) -> str:
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
            raise FlowError(f"prepare failed: {flow.get('validations', [])}")  # reason is in validations
        time.sleep(max(0.5, backoff(attempt, base=0.5, cap=5.0)))  # poll with backoff
        attempt += 1
    raise FlowError(f"flow {fid} not prepared after {self.settings.prepare_timeout_s}s")
```

```python
# app/config/_01bedrock_04prompt_flows.py
prepare_timeout_s: int = 120
```

- Catch: invoking after `UpdateFlow` without `PrepareFlow` fails or runs old behavior.

## 3. Versions

- **Version**: `CreateFlowVersion` = immutable snapshot (`1`, `2`, ...)
- Snapshot what was prepared.

```python
# app/infra/_01bedrock_04prompt_flows.py
def create_flow_version(self, flow_id: str | None = None, release_id: str = "") -> str:
    fid = flow_id or self.settings.flow_id
    kwargs: dict[str, Any] = {"flowIdentifier": fid, "description": f"release {release_id or 'manual'}"}
    if release_id:
        # clientToken from release_id: a retried release does not create a duplicate version
        kwargs["clientToken"] = str(uuid.uuid5(uuid.NAMESPACE_URL, f"flow-version/{fid}/{release_id}"))
    return self.agent.create_flow_version(**kwargs)["version"]

def list_flow_versions(self, flow_id: str | None = None) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for page in self.agent.get_paginator("list_flow_versions").paginate(flowIdentifier=flow_id or self.settings.flow_id):
        out += [{"version": v["version"], "status": v["status"]} for v in page.get("flowVersionSummaries", [])]
    return out  # DRAFT appears as a version entry too
```

## 4. Aliases

An alias is the stable name callers invoke.

### 4.1 Create An Alias

- `CreateFlowAlias` with `routingConfiguration = [{flowVersion: "1"}]`
- Callers invoke the alias Identifier (ID)
- **`concurrencyConfiguration`** caps parallel node execution
  - `Automatic`
  - or `Manual` + `maxConcurrency`

```python
# app/infra/_01bedrock_04prompt_flows.py
def create_flow_alias(self, version: str, name: str = "live", flow_id: str | None = None) -> dict[str, str]:
    fid = flow_id or self.settings.flow_id
    resp = self.agent.create_flow_alias(
        flowIdentifier=fid,
        name=name,
        routingConfiguration=[{"flowVersion": version}],  # exactly one version: no weighted split
        # Manual caps parallel node executions per invocation (protects model TPM / Lambda concurrency).
        concurrencyConfiguration={"type": "Manual", "maxConcurrency": 2},  # or {"type": "Automatic"}
        clientToken=str(uuid.uuid5(uuid.NAMESPACE_URL, f"flow-alias/{fid}/{name}")),
    )
    return {"alias_id": resp["id"], "alias_arn": resp["arn"]}
```

- Catch: `routingConfiguration` takes exactly one version.
  - Canary needs two aliases, or a traffic split in the caller.

### 4.2 Deploy And Rollback

- Deploy = `UpdateFlowAlias` to a new version
- Rollback = point back
- Callers keep the same alias ID

```python
# app/infra/_01bedrock_04prompt_flows.py
def point_alias(self, alias_id: str, version: str, name: str = "live", flow_id: str | None = None) -> None:
    self.agent.update_flow_alias(
        flowIdentifier=flow_id or self.settings.flow_id,
        aliasIdentifier=alias_id,
        name=name,  # required again: UpdateFlowAlias replaces the routing config
        routingConfiguration=[{"flowVersion": version}],
    )
```

- Catch: `UpdateFlowAlias` replaces the whole routing config.

## 5. One Release Call

The Representational State Transfer (REST) adapter runs prepare → version → alias as one deploy.

```python
# app/api/_01bedrock_04prompt_flows.py
@router.post("/{flow_id}/release")
def release(flow_id: str, body: ReleaseRequest, showcase: Showcase) -> dict[str, str]:
    try:
        showcase.prepare_flow(flow_id)
    except FlowError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    version = showcase.create_flow_version(flow_id, body.release_id)
    if body.alias_id:  # move an existing alias = deploy
        showcase.point_alias(body.alias_id, version, flow_id=flow_id)
        return {"version": version, "alias_id": body.alias_id}
    return {"version": version, **showcase.create_flow_alias(version, flow_id=flow_id)}  # first release: "live"
```

## 6. The Test Alias

- The DRAFT can be invoked through the built-in test alias in the console
  - `TSTALIASID`
- Never in production

⇒ behavior changes without a release

```python
# app/config/_01bedrock_04prompt_flows.py
flow_alias_id: str = "ALIAS_ID"  # from create_flow_alias ("live"); invoke aliases, never the DRAFT
```
