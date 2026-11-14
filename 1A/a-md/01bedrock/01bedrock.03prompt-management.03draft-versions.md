# 01bedrock.03prompt-management Draft And Versions

> DRAFT is the editable working copy; versions are immutable snapshots that act as the deploy unit.

## Index

- [1. DRAFT](#1-draft)
- [2. Versions](#2-versions)
- [3. Version ARN As Deploy Unit](#3-version-arn-as-deploy-unit)
- [4. Reading And Listing](#4-reading-and-listing)
- [5. Review Process](#5-review-process)

Back to [00index](01bedrock.03prompt-management.00index.md).

---

## 1. DRAFT

DRAFT is the only editable state of a prompt.

- **DRAFT**: the working copy
- `UpdatePrompt` edits it
  - Versions are immutable
- `UpdatePrompt` is a full replace
  - Send every variant, or the omitted ones are deleted
  - Resend description and Key Management Service (KMS) key too, or they are dropped

```python
# app/infra/_01bedrock_03prompt_management.py
def update_prompt_draft(self, prompt_id: str, new_text: str) -> ManagedPrompt:
    current = self.agent.get_prompt(promptIdentifier=prompt_id)  # DRAFT
    variants = current["variants"]
    for v in variants:
        if v["name"] == current["defaultVariant"] and v["templateType"] == "TEXT":
            v["templateConfiguration"]["text"]["text"] = new_text
    optional = {k: current[k] for k in ("description", "customerEncryptionKeyArn") if current.get(k)}
    resp = self.agent.update_prompt(
        promptIdentifier=prompt_id,
        name=current["name"],
        defaultVariant=current["defaultVariant"],
        variants=variants,  # full replace: every variant
        **optional,         # full replace: resend description and the KMS key too, or they are dropped
    )
    return self._to_prompt(resp)
```

- Catch: read-modify-write without a version check.

  ⇒ last writer wins

## 2. Versions

A version freezes DRAFT into a numbered, immutable snapshot.

- `CreatePromptVersion` snapshots DRAFT into `:1`, `:2`, ...
  - Amazon Resource Name (ARN) = `<prompt_arn>:<n>`
- Immutable
  - To change it, edit DRAFT and create a new version
  - Versions are never edited, only superseded
- `clientToken` makes version creation idempotent on retries
- Create at release time, after evals pass

```python
# app/infra/_01bedrock_03prompt_management.py
def create_prompt_version(self, prompt_id: str, description: str, release_id: str) -> ManagedPrompt:
    resp = self.agent.create_prompt_version(
        promptIdentifier=prompt_id,
        **({"description": description} if description else {}),
        # release_id -> clientToken: a retried release does not mint a second version
        clientToken=str(uuid.uuid5(uuid.NAMESPACE_URL, f"prompt-version/{prompt_id}/{release_id}")),
        tags={"Component": "01.03", "Release": release_id},
    )
    return self._to_prompt(resp)
```

- Catch: a random `clientToken` per attempt defeats idempotency.
  - Derive it from a stable release Identifier (ID).

## 3. Version ARN As Deploy Unit

- Config points at a version ARN
- Rollback = change config back
  - No code deploy

→ edit DRAFT  
→ test  
→ create version `:N`  
→ set config to the `:N` ARN  
→ roll back by restoring the old ARN

## 4. Reading And Listing

- `GetPrompt` without a version returns DRAFT.
- With `promptVersion` it returns an immutable version.
  - Versions can be cached forever.
- `ListPrompts` lists DRAFT entries; with `promptIdentifier` it lists one prompt's versions.

```python
# app/infra/_01bedrock_03prompt_management.py
def get_prompt(self, prompt_id: str, version: str | None = None) -> ManagedPrompt:
    kwargs: dict[str, str] = {"promptIdentifier": prompt_id}
    if version:
        kwargs["promptVersion"] = version  # omit -> DRAFT
    return self._to_prompt(self.agent.get_prompt(**kwargs))

def list_prompts(self) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    # boto3 paginator handles nextToken; returns the DRAFT entry per prompt
    for page in self.agent.get_paginator("list_prompts").paginate(PaginationConfig={"PageSize": 50}):
        for p in page.get("promptSummaries", []):
            out.append({"id": p["id"], "name": p["name"], "arn": p["arn"], "version": p["version"]})
    return out

def list_versions(self, prompt_id: str) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    token: str | None = None
    while True:  # manual nextToken loop
        kwargs: dict[str, Any] = {"promptIdentifier": prompt_id, "maxResults": 50}
        if token:
            kwargs["nextToken"] = token
        resp = self.agent.list_prompts(**kwargs)  # promptIdentifier -> versions of one prompt
        out += [{"version": p["version"], "arn": p["arn"]} for p in resp.get("promptSummaries", [])]
        token = resp.get("nextToken")
        if not token:
            return out
```

- Catch: only a missing `nextToken` means the last page.

## 5. Review Process

Review is your process, not the service's.

- Prompt text also lives in git (Terraform here)

  ⇒ pull-request review

- Eval gate before promoting a version
  - See [04safety.03evaluations](../04safety/04safety.03evaluations.00index.md)
