# 01bedrock.01converse Model Access And Model Identifiers (IDs)

> Who may call which model, how Identifiers (IDs) and inference profiles route, and how models age out.

## Index

- [1. Model Access](#1-model-access)
- [2. Model ID](#2-model-id)
  - [2.1 Listing Models](#21-listing-models)
- [3. Inference Profiles](#3-inference-profiles)
  - [3.1 System Cross-Region Profiles](#31-system-cross-region-profiles)
  - [3.2 Application Inference Profiles](#32-application-inference-profiles)
- [4. Model Lifecycle](#4-model-lifecycle)
- [5. Model IDs As Config](#5-model-ids-as-config)

Back to [00index](01bedrock.01converse.00index.md).

---

## 1. Model Access

Access rules changed over time; Identity and Access Management (IAM) always has the final say.

- Historically each model was enabled per account in the console ("Model access")
- Today most serverless models are available by default
  - To IAM principals with permission (Amazon Web Services (AWS), 2025)
- Some providers still need a one-time step
  - Use-case form or Marketplace subscription (Anthropic first use)
- IAM still decides
  - No `bedrock:InvokeModel` on the model Amazon Resource Name (ARN) ⇒ `AccessDeniedException`
- Limit: rules change
  - Check the "Access Amazon Bedrock foundation models" page

## 2. Model ID

A model ID names one model in one Region.

- Format `provider.model-name-version`
  - e.g. `anthropic.claude-haiku-4-5-20251001-v1:0`
- ARN `arn:aws:bedrock:<region>::foundation-model/<id>`
  - No account in the ARN: AWS owns it

### 2.1 Listing Models

- `ListFoundationModels` takes optional filters.
  - `byProvider`, `byOutputModality`, `byInferenceType`, `byCustomizationType`
- Use it to validate config at startup or alarm on `LEGACY`.

```python
# app/infra/_01bedrock_01converse.py
def list_foundation_models(self, provider=None, output_modality=None,
                           inference_type=None, customization=None) -> list[ModelInfo]:
    kwargs: dict[str, str] = {}
    if provider:
        kwargs["byProvider"] = provider            # "Anthropic", "Amazon", "Meta", ...
    if output_modality:
        kwargs["byOutputModality"] = output_modality  # TEXT | IMAGE | EMBEDDING
    if inference_type:
        kwargs["byInferenceType"] = inference_type    # ON_DEMAND | PROVISIONED
    if customization:
        kwargs["byCustomizationType"] = customization # FINE_TUNING | CONTINUED_PRE_TRAINING | DISTILLATION
    resp = self.control.list_foundation_models(**kwargs)  # not paginated; this Region only
    return [
        ModelInfo(
            model_id=m["modelId"],
            provider=m.get("providerName", ""),
            inference_types=m.get("inferenceTypesSupported", []),
            lifecycle=m.get("modelLifecycle", {}).get("status", ""),  # ACTIVE | LEGACY
            # ... modalities, streaming
        )
        for m in resp["modelSummaries"]
    ]
```

- Catch: not paginated, and lists models in this Region only.
- Catch: a profile-only model shows `inferenceTypesSupported=["INFERENCE_PROFILE"]`.

## 3. Inference Profiles

An inference profile is a routing alias over one model in several Regions.

### 3.1 System Cross-Region Profiles

- System-defined, cross-Region
  - `us.`, `eu.`, `apac.` prefix
  - `global.` for some models
- Bedrock picks a Region in the set with capacity

  ⇒ fewer throttles, same price as on-demand

- Some newer models are only offered through an inference profile
  - Calling the bare ID fails with `ValidationException`
- Catch: data may be processed in any Region of the set
  - Check data-residency rules (lecture 136 covers it)

```python
# app/infra/_01bedrock_01converse.py
def list_inference_profiles(self, type_equals: str = "SYSTEM_DEFINED") -> list[dict[str, str]]:
    profiles: list[dict[str, str]] = []
    token: str | None = None
    while True:
        kwargs: dict[str, Any] = {"typeEquals": type_equals, "maxResults": 100}  # or APPLICATION
        if token:
            kwargs["nextToken"] = token
        resp = self.control.list_inference_profiles(**kwargs)
        for p in resp.get("inferenceProfileSummaries", []):
            profiles.append({
                "id": p["inferenceProfileId"],
                "arn": p["inferenceProfileArn"],
                # Regions the profile routes to; IAM must allow the model in each of them
                "regions": ",".join(m["modelArn"].split(":")[3] for m in p.get("models", [])),
            })
        token = resp.get("nextToken")
        if not token:  # only a missing nextToken means the last page
            return profiles
```

- Catch: the profile's model list shows its Regions.
  - IAM must allow the foundation model in each of them.

### 3.2 Application Inference Profiles

- Your own profile copied from a model or system profile
- Carries your tags

  ⇒ cost allocation per app or tenant

- Called by ARN
- Created in Terraform here (`a-app-profile`)

```python
# app/infra/_01bedrock_01converse.py
def converse_via_app_profile(self, prompt: str) -> ConverseResult:
    arn = self.settings.app_profile_arn  # terraform output converse_app_profile_arn
    if not arn:
        raise ConverseError("A_CONVERSE_APP_PROFILE_ARN is not set (terraform output converse_app_profile_arn)")
    return self.converse_basic(prompt, model_id=arn)  # modelId = the profile ARN
```

- Catch: `modelId` is the profile ARN.
  - IAM must allow that ARN (the component Terraform does).

## 4. Model Lifecycle

Models move through states and eventually disappear.

→ `ACTIVE`  
→ `LEGACY`  
→ end of life

- `ListFoundationModels` returns `modelLifecycle.status`
- Alarm on `LEGACY` models you still call

## 5. Model IDs As Config

- Every model value is config, never code.
  - Switching models is an env change, not a redeploy.
- Empty slice values fall back to the shared IDs.
  - The shared default is a `us.` cross-Region inference profile.

```python
# app/config/_01bedrock_01converse.py
class ConverseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="A_CONVERSE_", env_file=".env", extra="ignore")

    model_id: str = ""         # empty -> shared text_model_id (us. cross-Region inference profile)
    fast_model_id: str = ""    # empty -> shared fast_model_id
    app_profile_arn: str = ""  # terraform output converse_app_profile_arn; empty -> skip that demo

    def text_model(self) -> str:
        return self.model_id or get_settings().text_model_id
```

- Catch: a slice override is for experiments only.
  - Production traffic should use the shared profile ID.
