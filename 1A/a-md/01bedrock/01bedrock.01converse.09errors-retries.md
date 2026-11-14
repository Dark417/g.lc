# 01bedrock.01converse Throttling, Errors, Retries

> Which Identity and Access Management (IAM) actions authorize a call, which errors to retry, and how quotas throttle you.

## Index

- [1. IAM](#1-iam)
- [2. Errors](#2-errors)
  - [2.1 Error Table](#21-error-table)
  - [2.2 Classifying In Code](#22-classifying-in-code)
- [3. Two Retry Layers](#3-two-retry-layers)
- [4. Quotas](#4-quotas)

Back to [00index](01bedrock.01converse.00index.md).

---

## 1. IAM

Converse reuses the InvokeModel IAM actions.

- `Converse` is authorized by `bedrock:InvokeModel`
- `ConverseStream` by `bedrock:InvokeModelWithResponseStream`
- Resource = one of
  - foundation-model Amazon Resource Name (ARN)
  - inference-profile ARN
  - provisioned-model ARN
- A cross-Region profile needs two kinds of ARN
  - The profile ARN
  - The foundation-model ARN in every Region it routes to

## 2. Errors

Retry capacity and transient errors; fix request errors.

### 2.1 Error Table

| Error | Hypertext Transfer Protocol (HTTP) | Meaning | Retry? |
|---|---|---|---|
| `ThrottlingException` | 429 | Requests Per Minute (RPM) or Tokens Per Minute (TPM) quota hit | Yes, backoff + jitter |
| `ServiceUnavailableException` | 503 | Capacity issue | Yes |
| `InternalServerException` | 500 | Service error | Yes, a few times |
| `ModelTimeoutException` | 408 | Generation took too long | Maybe: smaller `maxTokens`, or stream |

| Error | HTTP | Meaning | Retry? |
|---|---|---|---|
| `ModelNotReadyException` | 429 | Model (often imported/custom) not loaded yet | Yes, with longer waits |
| `ModelErrorException` | 424 | Model returned an error | Rarely; log and fail |
| `ValidationException` | 400 | Bad request: role order, schema, unsupported field, bad model Identifier (ID) | No: fix the request |
| `AccessDeniedException` | 403 | IAM, or model not available to the account | No |

### 2.2 Classifying In Code

- One retryable set, one non-retryable set.
- A mid-stream `EventStreamError` subclasses `ClientError`.
  - Both land in the same classifier.

```python
# app/infra/_01bedrock_01converse.py
# ModelTimeoutException is retryable only if the cause is transient;
# a prompt that always needs > timeout must shrink (maxTokens) or stream instead.
RETRYABLE_CODES = {
    "ThrottlingException",          # 429: RPM/TPM quota for this model in this Region
    "ServiceUnavailableException",  # 503: capacity
    "InternalServerException",      # 500
    "ModelNotReadyException",       # 429: model (often custom/imported) still loading
    "ModelTimeoutException",        # 408: generation too slow
}
NON_RETRYABLE_CODES = {"ValidationException", "AccessDeniedException", "ResourceNotFoundException"}

def error_code(e: Exception) -> str:
    # EventStreamError (mid-stream error event) subclasses ClientError, so both land here.
    if isinstance(e, (ClientError, EventStreamError)):
        return e.response.get("Error", {}).get("Code", "")
    return ""

def is_retryable(e: Exception) -> bool:
    if isinstance(e, ReadTimeoutError):
        return True
    return error_code(e) in RETRYABLE_CODES
```

```python
# app/domain/_01bedrock_01converse.py
class ConverseError(Exception):
    """Non-retryable request problem (ValidationException, AccessDenied): fix the request, don't retry."""
```

## 3. Two Retry Layers

The Software Development Kit (SDK) retries single requests; the app retries whole calls.

- SDK layer
  - Adaptive retry mode (`app.shared.aws`)
  - Retries 429/5xx and slows the client after throttles
- App layer
  - `app.shared.retry.call_with_retry` around a whole call
  - With a retryable predicate
- Catch: retries multiply under load (SDK 5 × app 3)

  ⇒ cap total attempts and fall back (smaller model, profile, queue)

```python
# app/infra/_01bedrock_01converse.py
def converse_with_retry(self, prompt: str) -> ConverseResult:
    try:
        return call_with_retry(
            lambda: self.converse_basic(prompt),
            retryable=is_retryable,
            max_attempts=self.settings.app_retry_attempts,  # 3, on top of the SDK's adaptive retries
            base=0.5,
            cap=8.0,  # full jitter between base and cap
        )
    except ClientError as e:
        code = error_code(e)
        if code in NON_RETRYABLE_CODES:
            # e.g. roles not alternating, unsupported field for this model, bare ID of a profile-only model
            raise ConverseError(f"{code}: {e.response['Error'].get('Message', '')}") from e
        raise  # retryable but exhausted: let the caller shed load / fall back to the fast model
```

```python
# app/api/_01bedrock_01converse.py
@router.post("/chat/retry")
def chat_with_retry(body: PromptRequest, showcase: Showcase) -> dict[str, Any]:
    try:
        return _json(showcase.converse_with_retry(body.prompt))
    except ConverseError as e:  # ValidationException / AccessDenied: the request is wrong, not the service
        raise HTTPException(status_code=400, detail=str(e)) from e
```

- Catch: an exhausted retryable error is re-raised, not wrapped.
  - The caller decides: shed load or fall back to the fast model.

## 4. Quotas

On-demand capacity is metered per model, per Region.

- Requests per minute and tokens per minute (on-demand)
- Tokens/min counts `maxTokens` reserved up front for some models
  - Order of magnitude; check the quotas page

  ⇒ an oversized `maxTokens` throttles you sooner

- Values differ per account
  - See Service Quotas → Amazon Bedrock
