# 04safety.02pii-redaction.06pseudonymization Masking vs Reversible Tokenization

> Pick by whether anyone must ever get the value back; if so, use keyed tokens and a guarded vault.

## Index

- [1. Techniques Compared](#1-techniques-compared)
- [2. Salted HMAC Pseudonym](#2-salted-hmac-pseudonym)
  - [2.1 Code: Vault Adapter](#21-code-vault-adapter)
- [3. Vault](#3-vault)
  - [3.1 Code: Port and Detokenize](#31-code-port-and-detokenize)

Back to [00index](04safety.02pii-redaction.00index.md).

## 1. Techniques Compared

Masking forgets; pseudonymization remembers.

| Technique | Reversible | Linkable across records | Use |
|---|---|---|---|
| Mask (`*****`) | no | no | logs, analytics, model input that never needs the value |
| Replace with type (`[EMAIL]`) | no | no | model input; keeps sentence meaning |
| Deterministic pseudonym (salted Hash-Based Message Authentication Code (HMAC)) + vault | yes, via vault | yes (same value → same token) | prompt in, real value back in the answer; joins |
| Random token + vault | yes, via vault | no | strongest privacy; no joins |
| Format-preserving encryption | yes, with key | yes | systems that validate formats (card length) |

- Deterministic tokens enable joins but are linkable; random tokens are not

## 2. Salted HMAC Pseudonym

Lecture 210, key salting.

- `token = TYPE + "_" + HMAC-SHA256(secret_key, type + ":" + value)[:n]`
- Secret key = the "salt"
  - without it, tokens cannot be brute-forced from known values (e.g. all phone numbers)
- Plain unsalted Secure Hash Algorithm 256-bit (SHA-256) of a Social Security Number (SSN) is reversible by enumeration (10⁹ values)
  - never hash without a key
- Rotate the key ⇒ new tokens
  - old mappings stay in the vault
  - rotation breaks joins

### 2.1 Code: Vault Adapter

```python
# app/infra/_04safety_02pii_redaction.py
class InMemoryPseudonymVault:
    """token = <<TYPE_hmac_sha256(key, type:value)[:16]>>. Prod: DynamoDB + KMS, audited detokenize."""

    def __init__(self, key: bytes, digest_chars: int = 16) -> None:
        if len(key) < 16:
            raise ValueError("HMAC key must be at least 16 bytes")
        self._key = key
        self._chars = digest_chars
        self._by_token: dict[str, str] = {}
        self._lock = threading.Lock()

    def tokenize(self, entity_type: str, value: str) -> str:
        digest = hmac.new(self._key, f"{entity_type}:{value}".encode(), hashlib.sha256).hexdigest()
        token = f"<<{entity_type}_{digest[: self._chars]}>>"  # deterministic per (type, value, key)
        with self._lock:
            self._by_token[token] = value
        return token

    def detokenize(self, token: str) -> str | None:
        with self._lock:
            return self._by_token.get(token)


def vault_from_settings() -> InMemoryPseudonymVault:
    key = get_pii_settings().hmac_key.encode() or os.urandom(32)  # random = tokens die with the process
    return InMemoryPseudonymVault(key)
```

- Catch
  - `hmac_key` default is demo only
  - in prod load it from Secrets Manager / KMS-encrypted config

## 3. Vault

The vault is now the crown jewel.

- Port
  - `tokenize(type, value) → token`
  - `detokenize(token) → value`
- Adapter
  - in-memory here
  - DynamoDB + Key Management Service (KMS) or a tokenization service in prod
- Protect it
  - separate account / role
  - audit every detokenize
  - rate limits
- Re-identification happens only at the edge
  - for an authorized user
  - after the output guardrail

### 3.1 Code: Port and Detokenize

```python
# app/domain/_04safety_02pii_redaction.py
TOKEN_RE = re.compile(r"<<([A-Z_]+)_([0-9a-f]{8,32})>>")


class PseudonymVault(Protocol):
    """Reversible tokenization. tokenize must be deterministic per (type, value) within one key epoch."""

    def tokenize(self, entity_type: str, value: str) -> str: ...

    def detokenize(self, token: str) -> str | None: ...


def detokenize_text(text: str, vault: PseudonymVault) -> str:
    """Replace <<TYPE_hash>> tokens with original values. Only for an authorized caller, after output checks."""

    def sub(m: re.Match[str]) -> str:
        value = vault.detokenize(m.group(0))
        return value if value is not None else m.group(0)  # unknown token stays as-is

    return TOKEN_RE.sub(sub, text)
```
