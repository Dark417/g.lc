"""Agent tools. Closures over the container's services; plain async functions to ADK.

ADK builds each tool's schema from the signature and the docstring's Args section. A
`tool_context` parameter is injected by ADK and hidden from the model.
"""

from collections.abc import Callable

from google.adk.tools import ToolContext

from app.domain.models import RuleIn, RuleStatus, RuleUpdate, Severity
from app.rag.parsers import UnsupportedFormat, parse
from app.rag.retriever import source_label

MAX_ATTACHMENT_CHARS = 20_000


def _rule_brief(r) -> dict:
    return {"code": r.code, "title": r.title, "severity": r.severity, "category": r.category}


def _rule_full(r) -> dict:
    return {
        **_rule_brief(r),
        "statement": r.statement,
        "rationale": r.rationale,
        "exception_process": r.exception_process,
        "status": r.status,
        "version": r.version,
        "source_document_id": r.source_document_id,
        "source_ref": r.source_ref,
    }


async def _load_attachment(tool_context: ToolContext, filename: str):
    part = await tool_context.load_artifact(filename)
    if part is None or part.inline_data is None:
        names = await tool_context.list_artifacts()
        return None, {
            "status": "not_found",
            "message": f"no attachment {filename!r}",
            "available": names,
        }
    return part.inline_data, None


def build_tools(c) -> tuple[list[Callable], list[Callable]]:
    """Returns (tools for everyone, admin-only tools)."""

    # ---------------------------------------------------------------- read tools (all roles)
    async def list_rules(category: str = "", severity: str = "") -> dict:
        """List active compliance rules, optionally filtered.

        Args:
            category: e.g. "privacy", "marketing", "security"; "" for all.
            severity: "hard", "flexible", or "" for both.
        """
        rules = await c.rules.list(category=category or None, severity=severity or None)
        return {"status": "ok", "count": len(rules), "rules": [_rule_brief(r) for r in rules]}

    async def search_rules(query: str) -> dict:
        """Find rules relevant to a topic by meaning, e.g. "children's data" or "email marketing".

        Args:
            query: A short natural-language description of the topic.
        """
        hits = await c.retriever.search_rules(query, k=8)
        found = await c.rules.get_many([h.ref_id for h in hits])
        rules = [
            found[h.ref_id]
            for h in hits
            if h.ref_id in found and found[h.ref_id].status == "active"
        ]
        return {"status": "ok", "rules": [_rule_full(r) for r in rules]}

    async def get_rule(code: str) -> dict:
        """Get one rule with its full statement, rationale, and exception process.

        Args:
            code: The rule code, e.g. "PRIV-003".
        """
        r = await c.rules.get(code)
        return (
            {"status": "ok", "rule": _rule_full(r)} if r else {"status": "not_found", "code": code}
        )

    async def list_documents(category: str = "") -> dict:
        """List the compliance documents in the knowledge base.

        Args:
            category: Filter by category, or "" for all.
        """
        docs = await c.docs.list(category=category or None)
        return {
            "status": "ok",
            "documents": [
                {
                    "id": d.id,
                    "title": d.title,
                    "category": d.category,
                    "format": d.format,
                    "status": d.status,
                }
                for d in docs
            ],
        }

    async def get_document_summary(document: str) -> dict:
        """Get a document's summary, key points, and outline.

        Args:
            document: The document id (doc_...) or its title (partial titles work).
        """
        d = await c.ingestion.find(document)
        if d is None:
            return {"status": "not_found", "message": f"no document matching {document!r}"}
        return {
            "status": "ok",
            "document": {
                "id": d.id,
                "title": d.title,
                "category": d.category,
                "summary": d.summary,
                "key_points": d.key_points,
                "outline": d.outline,
                "extracted_rule_codes": d.extracted_rule_codes,
            },
        }

    async def search_documents(query: str) -> dict:
        """Search the text of all compliance documents for relevant passages.

        Args:
            query: What to look for, in natural language.
        """
        hits = await c.retriever.search_documents(query, k=6)
        return {
            "status": "ok",
            "passages": [
                {
                    "source": source_label(h.metadata),
                    "document_id": h.ref_id,
                    "score": round(h.score, 3),
                    "text": h.text,
                }
                for h in hits
            ],
        }

    async def assess_proposal(proposal: str, tool_context: ToolContext, context: str = "") -> dict:
        """Decide whether a proposal complies with the rules. Returns the verdict, per-rule
        findings with evidence, conditions, and missing information. The verdict is final.

        Args:
            proposal: The full proposal, restated with every relevant fact from the conversation.
            context: Optional extra context, e.g. text of an attached proposal document.
        """
        verdict = await c.assessment.assess(
            proposal,
            context=context,
            user_id=tool_context.user_id,
            session_id=tool_context.session.id,
        )
        return verdict.model_dump(mode="json")

    async def list_attachments(tool_context: ToolContext) -> dict:
        """List files attached in this conversation."""
        return {"status": "ok", "attachments": await tool_context.list_artifacts()}

    async def read_attachment(filename: str, tool_context: ToolContext) -> dict:
        """Read the text of a file attached in this conversation (pdf, docx, md, html, txt).

        Args:
            filename: The attachment name exactly as shown in the conversation.
        """
        blob, err = await _load_attachment(tool_context, filename)
        if err:
            return err
        try:
            text = parse(blob.data, filename).full_text()
        except UnsupportedFormat as e:
            return {"status": "error", "message": str(e)}
        return {
            "status": "ok",
            "filename": filename,
            "text": text[:MAX_ATTACHMENT_CHARS],
            "truncated": len(text) > MAX_ATTACHMENT_CHARS,
        }

    # ---------------------------------------------------------------- admin tools
    async def add_rule(
        title: str,
        statement: str,
        severity: str,
        category: str,
        tool_context: ToolContext,
        rationale: str = "",
        exception_process: str = "",
        code: str = "",
        source_document_id: str = "",
    ) -> dict:
        """Create a new compliance rule. Confirm the wording with the admin first.

        Args:
            title: Short name, under 12 words.
            statement: The rule itself, using "must" / "must not".
            severity: "hard" (no exceptions) or "flexible" (allowed with conditions or approval).
            category: e.g. "privacy", "marketing", "security", "product-launch".
            rationale: Why the rule exists.
            exception_process: For flexible rules, who can approve a deviation.
            code: Optional code like "PRIV-010"; generated if empty.
            source_document_id: The document the rule came from, if any.
        """
        try:
            data = RuleIn(
                code=code or None,
                title=title,
                statement=statement,
                severity=Severity(severity.lower()),
                category=category,
                rationale=rationale,
                exception_process=exception_process,
                source_document_id=source_document_id,
            )
            rule = await c.rule_service.create(data, tool_context.user_id, on_conflict="renumber")
        except ValueError as e:
            return {"status": "error", "message": str(e)}
        if source_document_id and (doc := await c.docs.get(source_document_id)):
            doc.extracted_rule_codes = sorted({*doc.extracted_rule_codes, rule.code})
            await c.docs.upsert(doc)
        return {"status": "created", "rule": _rule_full(rule)}

    async def update_rule(
        code: str,
        tool_context: ToolContext,
        statement: str = "",
        title: str = "",
        severity: str = "",
        exception_process: str = "",
        change_note: str = "",
    ) -> dict:
        """Edit an existing rule. Only non-empty fields change. The version number increases.

        Args:
            code: The rule code, e.g. "MKT-002".
            statement: New statement, or "" to keep.
            title: New title, or "" to keep.
            severity: "hard" or "flexible", or "" to keep.
            exception_process: New exception process, or "" to keep.
            change_note: Why the rule changed (kept in the audit trail).
        """
        try:
            patch = RuleUpdate(
                statement=statement or None,
                title=title or None,
                severity=Severity(severity.lower()) if severity else None,
                exception_process=exception_process or None,
                change_note=change_note,
            )
        except ValueError as e:
            return {"status": "error", "message": str(e)}
        rule = await c.rule_service.update(code, patch, tool_context.user_id)
        return (
            {"status": "updated", "rule": _rule_full(rule)}
            if rule
            else {"status": "not_found", "code": code}
        )

    async def retire_rule(code: str, reason: str, tool_context: ToolContext) -> dict:
        """Retire a rule so it no longer applies. History is kept.

        Args:
            code: The rule code.
            reason: Why it is retired.
        """
        rule = await c.rule_service.retire(code, tool_context.user_id, reason)
        if rule is None:
            return {"status": "not_found", "code": code}
        return {"status": "retired", "code": rule.code, "status_now": RuleStatus.RETIRED}

    async def ingest_attachment(
        filename: str, tool_context: ToolContext, title: str = "", category: str = ""
    ) -> dict:
        """Add an attached file to the knowledge base as a compliance document (parse, index,
        summarise). Supported: pdf, docx, md, html, txt.

        Args:
            filename: The attachment name exactly as shown in the conversation.
            title: Optional document title.
            category: Optional category, e.g. "privacy".
        """
        blob, err = await _load_attachment(tool_context, filename)
        if err:
            return err
        try:
            doc = await c.ingestion.ingest(
                blob.data, filename, actor=tool_context.user_id, title=title, category=category
            )
        except UnsupportedFormat as e:
            return {"status": "error", "message": str(e)}
        return {
            "status": doc.status,
            "document": {
                "id": doc.id,
                "title": doc.title,
                "category": doc.category,
                "chunks": doc.chunk_count,
                "summary": doc.summary,
            },
        }

    async def propose_rules_from_attachment(filename: str, tool_context: ToolContext) -> dict:
        """Extract candidate rules from an attached file. Nothing is saved; show them to the admin
        and call add_rule for the ones they approve.

        Args:
            filename: The attachment name exactly as shown in the conversation.
        """
        blob, err = await _load_attachment(tool_context, filename)
        if err:
            return err
        try:
            text = parse(blob.data, filename).full_text()
        except UnsupportedFormat as e:
            return {"status": "error", "message": str(e)}
        from app.services.rule_extraction import propose_rules

        rules = await propose_rules(c.llm, text, source_hint=filename)
        return {"status": "proposed", "rules": [r.model_dump(mode="json") for r in rules]}

    async def propose_rules_from_document(document: str) -> dict:
        """Extract candidate rules from an ingested document. Nothing is saved; show them to the
        admin and call add_rule (with source_document_id) for the ones they approve.

        Args:
            document: Document id or title.
        """
        d = await c.ingestion.find(document)
        if d is None:
            return {"status": "not_found", "message": f"no document matching {document!r}"}
        rules = await c.ingestion.propose_rules(d)
        return {
            "status": "proposed",
            "document_id": d.id,
            "rules": [r.model_dump(mode="json") for r in rules],
        }

    user_tools = [
        list_rules,
        search_rules,
        get_rule,
        list_documents,
        get_document_summary,
        search_documents,
        assess_proposal,
        list_attachments,
        read_attachment,
    ]
    admin_tools = [
        add_rule,
        update_rule,
        retire_rule,
        ingest_attachment,
        propose_rules_from_attachment,
        propose_rules_from_document,
    ]
    return user_tools, admin_tools
