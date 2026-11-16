# prompt-engineering Templates

> Fixed text plus variables, rendered strictly, versioned, and chained into steps.

## Index

- [1. Template Basics](#1-template-basics)
- [2. Strict Rendering](#2-strict-rendering)
- [3. Storing And Chaining](#3-storing-and-chaining)

Back to [00index](prompt-engineering.00index.md).

---

## 1. Template Basics

- **Template**: fixed text + `{{variables}}` filled per request
- Escape or fence variable values that come from users or documents

## 2. Strict Rendering

Missing or unknown variables fail loudly.

- Same `{{variable}}` syntax as Bedrock Prompt Management
- A silently empty `{{context}}` is a classic prompt bug

```python
# app/domain/_01bedrock_05prompt_engineering.py
_VAR = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")

def render_template(template: str, variables: dict[str, str]) -> str:
    names = set(_VAR.findall(template))
    missing = names - variables.keys()   # placeholder with no value
    unused = variables.keys() - names    # value with no placeholder (typo in a name)
    if missing or unused:
        raise TemplateError(f"missing={sorted(missing)} unused={sorted(unused)}")
    return _VAR.sub(lambda m: variables[m.group(1)], template)
```

- Catch: values are inserted verbatim.
  - Untrusted values must be fenced first (`fence_untrusted`, [07 prompt misuse](prompt-engineering.07prompt-misuse.md)).
- The Representational State Transfer (REST) adapter exposes `/render` with no Amazon Web Services (AWS) call.
  - Inspect a prompt before spending tokens.

## 3. Storing And Chaining

- Store templates as versioned artifacts
  - git, or Bedrock Prompt Management ([prompt-management](prompt-management.00index.md))
- **Prompt chaining**: split a big task into steps
  - Each step has its own template
  - See [prompt-flows](prompt-flows.00index.md)
