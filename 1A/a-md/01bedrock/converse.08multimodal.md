# converse Multimodal Content Blocks

> Images, documents, and video go into a user message as typed content blocks.

## Index

- [1. Image Blocks](#1-image-blocks)
- [2. Document Blocks](#2-document-blocks)
  - [2.1 Fields](#21-fields)
  - [2.2 Name Sanitizing](#22-name-sanitizing)
- [3. Video And Simple Storage Service (S3) Sources](#3-video-and-simple-storage-service-s3-sources)
- [4. Limits And Cost](#4-limits-and-cost)
- [5. Image Generation](#5-image-generation)

Back to [00index](converse.00index.md).

---

## 1. Image Blocks

An image block is a format plus raw bytes.

- `image`: `format` + `source.bytes`
  - Formats: `png`, `jpeg`, `gif`, `webp`
  - Raw bytes in boto3; base64 on the wire
    - Never pre-encode
- Image first, question after

```python
# app/infra/_01bedrock_01converse.py
def converse_image(self, image: bytes, image_format: str, question: str) -> ConverseResult:
    if image_format not in {"png", "jpeg", "gif", "webp"}:
        raise ConverseError(f"unsupported image format {image_format}")
    resp = self.runtime.converse(
        modelId=self.settings.text_model(),
        messages=[{
            "role": "user",
            "content": [
                {"image": {"format": image_format, "source": {"bytes": image}}},  # raw bytes, boto3 encodes
                # {"image": {"format": ..., "source": {"s3Location": {"uri": "s3://..."}}}}  # some models only (Nova)
                {"text": question},
            ],
        }],
        inferenceConfig=self.inference_config(),
    )
    return parse_converse_response(resp)
```

- Catch: images cost input tokens by pixel count; resize first.

## 2. Document Blocks

A document block adds a name, and the name reaches the model.

### 2.1 Fields

- `document`: `format` + `name` + `source.bytes`
  - Formats: `pdf`, `csv`, `doc`, `docx`, `xls`, `xlsx`, `html`, `txt`, `md`
- Optional `citations: {enabled: true}`
  - For models that return citation blocks
- A text block is required alongside a document
- Use for one-off document Question and Answer (Q&A)
  - Use Retrieval-Augmented Generation (RAG) ([knowledge-bases](../02rag/knowledge-bases.00index.md)) for corpora

```python
# app/infra/_01bedrock_01converse.py
def converse_document(self, document: bytes, doc_format: str, filename: str, question: str) -> ConverseResult:
    resp = self.runtime.converse(
        modelId=self.settings.text_model(),
        messages=[{
            "role": "user",
            "content": [
                {"document": {
                    "format": doc_format,
                    "name": safe_document_name(filename),  # restricted chars; also part of the prompt
                    "source": {"bytes": document},
                    # "citations": {"enabled": True},  # models that support citation blocks
                }},
                {"text": question},  # a text block is required alongside a document
            ],
        }],
        inferenceConfig=self.inference_config(),
    )
    return parse_converse_response(resp)
```

### 2.2 Name Sanitizing

- `name` allows only:
  - letters, digits
  - single spaces
  - hyphens
  - parentheses, square brackets

⇒ sanitize file names  
⇒ the name is also part of the prompt (injection surface)

```python
# app/domain/_01bedrock_01converse.py
_DOC_NAME_BAD = re.compile(r"[^A-Za-z0-9\s\-\(\)\[\]]")
_SPACES = re.compile(r"\s+")

def safe_document_name(filename: str) -> str:
    """The name is shown to the model ⇒ treat it as untrusted text (prompt-injection surface)."""
    stem = filename.rsplit(".", 1)[0]  # drop the extension; format carries it
    cleaned = _SPACES.sub(" ", _DOC_NAME_BAD.sub("-", stem)).strip()  # bad chars -> "-", collapse spaces
    return (cleaned or "document")[:200]
```

- Catch: sanitizing fixes the Application Programming Interface (API) error, not the injection risk.
  - The name is still untrusted text to the model.

## 3. Video And Simple Storage Service (S3) Sources

- `video` (Nova models): bytes or `s3Location`
- `s3Location` instead of bytes: only some models (Nova)
  - Claude takes bytes
- Not coded here (see [00index gaps](converse.00index.md#5-gaps))

## 4. Limits And Cost

- Limits per request are per model
  - Count, Megabytes (MB), pixel size
  - Order of magnitude: a handful of documents of a few MB
  - A few dozen images
  - Source: ImageBlock / DocumentBlock API reference; check per model
- Images and Portable Document Format files (PDFs) cost input tokens
  - Image tokens scale with pixels

  ⇒ resize before sending

## 5. Image Generation

- Lecture 22 also covers image generation
  - Nova Canvas, Titan Image
- `InvokeModel` only, not Converse
  - See [03 InvokeModel vs Converse](converse.03invoke-vs-converse.md)
