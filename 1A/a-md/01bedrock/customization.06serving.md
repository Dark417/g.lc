# customization Serving A Custom Model

> A trained model is not callable until you provision or deploy it; that step owns the bill.

## Index

- [1. Serving Options](#1-serving-options)
- [2. Provisioned Throughput](#2-provisioned-throughput)
  - [2.1 Create](#21-create)
  - [2.2 Wait And Delete](#22-wait-and-delete)
- [3. On-Demand Deployment](#3-on-demand-deployment)
- [4. Custom Model Import](#4-custom-model-import)
- [5. Calling The Custom Model](#5-calling-the-custom-model)
- [6. Cost](#6-cost)

Back to [00index](customization.00index.md).

---

## 1. Serving Options

| Option | Billing | Applies to |
|---|---|---|
| Provisioned throughput | Per model unit per hour | Most custom models |
| On-demand deployment | Per token | Supported custom models |
| Custom Model Import | On demand | Your open-weight models |

## 2. Provisioned Throughput

Buy model units; pay per hour while it exists, used or not.

- Buy model units (MUs)
- Terms
  - no commitment (hourly)
  - 1-month
  - 6-month
- Required for most custom models
- Billed per hour while it exists, used or not
- Call with `modelId = provisioned model ARN`

### 2.1 Create

```python
# app/infra/_01bedrock_02customization.py
def create_provisioned_throughput(self, custom_model_arn: str, name: str) -> str:
    # !!! COST WARNING: hourly billing starts now and runs until delete, with or without traffic.
    return self.control.create_provisioned_model_throughput(
        provisionedModelName=name,
        modelId=custom_model_arn,
        modelUnits=1,  # throughput scales with units; size from measured tokens/min
        # commitmentDuration="OneMonth",  # omit = no commitment (hourly, deletable any time)
        clientRequestToken=str(uuid.uuid5(uuid.NAMESPACE_URL, f"pt/{name}")),
        tags=[{"key": "Component", "value": "01.02"}, {"key": "DeleteAfterTest", "value": "true"}],
    )["provisionedModelArn"]
```

- Catch: `OneMonth` | `SixMonths` is cheaper per hour.
  - But it cannot be cancelled.

### 2.2 Wait And Delete

- Status: `Creating` | `InService` | `Updating` | `Failed`
- Provisioning takes minutes.
- Delete is the call that stops the bill.

```python
# app/infra/_01bedrock_02customization.py
def wait_for_provisioned(self, provisioned_arn: str, timeout_s: int = 3600) -> str:
    deadline = time.monotonic() + timeout_s
    attempt = 0
    while time.monotonic() < deadline:
        pt = self.control.get_provisioned_model_throughput(provisionedModelId=provisioned_arn)
        if pt["status"] == "InService":
            return pt["status"]
        if pt["status"] == "Failed":
            raise CustomizationError(pt.get("failureMessage", "provisioning failed"))
        time.sleep(max(15.0, backoff(attempt, base=15.0, cap=120.0)))
        attempt += 1
    raise CustomizationError("provisioned throughput not InService in time")

def delete_provisioned_throughput(self, provisioned_arn: str) -> None:
    self.control.delete_provisioned_model_throughput(provisionedModelId=provisioned_arn)  # stops the bill
```

- Catch: delete right after tests.
  - Not possible during a commitment term.

## 3. On-Demand Deployment

- `CreateCustomModelDeployment`
- Pay per token for supported custom models
  - Check model support

```python
# app/infra/_01bedrock_02customization.py
def create_on_demand_deployment(self, custom_model_arn: str, name: str) -> str:
    return self.control.create_custom_model_deployment(
        modelDeploymentName=name,
        modelArn=custom_model_arn,
        clientRequestToken=str(uuid.uuid5(uuid.NAMESPACE_URL, f"deploy/{name}")),
        tags=[{"key": "Component", "value": "01.02"}],
    )["customModelDeploymentArn"]
```

- Catch: unsupported models still need provisioned throughput.

## 4. Custom Model Import

- Bring your own open-weight model (Llama, Mistral, ...)
- Serve it on demand
- Not coded here

## 5. Calling The Custom Model

- Same Converse call as [converse](converse.00index.md).
- `modelId` = provisioned model Amazon Resource Name (ARN) or deployment ARN.

```python
# app/infra/_01bedrock_02customization.py
def converse_custom(self, prompt: str, model_arn: str | None = None) -> dict[str, Any]:
    arn = model_arn or self.settings.provisioned_model_arn  # set by hand after a deliberate, paid PT create
    if not arn:
        raise CustomizationError("no provisioned/deployment ARN configured (A_CUSTOMIZATION_PROVISIONED_MODEL_ARN)")
    resp = self.runtime.converse(
        modelId=arn,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 512, "temperature": 0.0},
    )
    return {
        "text": "".join(b.get("text", "") for b in resp["output"]["message"]["content"]),
        "stop_reason": resp["stopReason"],
        "usage": resp.get("usage", {}),
    }
```

- Catch: the tuned model expects prompts shaped like its training data.
  - Same system text, same format.
- The Representational State Transfer (REST) Application Programming Interface (API) exposes only read/validate routes and this call.
  - Starting jobs or buying throughput is never one Hypertext Transfer Protocol (HTTP) click away.

## 6. Cost

- Order of magnitude: one model unit costs tens of dollars per hour for larger models
  - Pricing page; verify

⇒ delete it when idle  
⇒ tag it  
⇒ alarm on it ([base_billing_alarm](../../terraform/modules/base_billing_alarm/main.tf))
