"""The real ADK agent loop (Runner, callbacks, role-gated toolset, artifacts plugin, sessions,
memory) driven by a scripted model. No network."""

import base64

import pytest
from google.adk.runners import Runner

from app.agents.builder import build_app
from app.agents.callbacks import make_before_tool
from app.services.chat import ChatService, ConversationNotFound
from tests.conftest import HARD_OK, SAMPLES, ScriptedModel, call, findings_from, say, seed_rules

ALICE, ADMIN = "alice@example.com", "admin@example.com"


def make_chat(container, model) -> ChatService:
    runner = Runner(
        app=build_app(container, model=model),
        session_service=container.sessions,
        memory_service=container.memory,
        artifact_service=container.artifacts,
    )
    return ChatService(
        runner=runner,
        sessions=container.sessions,
        app_name=container.settings.app_name,
        memory=container.memory,
    )


def attachment(path, name=None):
    return {
        "filename": name or path.name,
        "mime_type": "text/markdown",
        "data_base64": base64.b64encode(path.read_bytes()).decode(),
    }


async def test_admin_tools_are_invisible_to_users_and_visible_to_admins(container):
    model = ScriptedModel(script=[say("hi"), say("hi")])
    chat = make_chat(container, model)

    await chat.chat(user_id=ALICE, session_id=None, message="hello")
    user_tools = model.offered_tools(0)
    assert {"assess_proposal", "search_rules", "read_attachment"} <= user_tools
    assert not user_tools & {"add_rule", "update_rule", "retire_rule", "ingest_attachment"}

    await chat.chat(user_id=ADMIN, session_id=None, message="hello")
    assert {"add_rule", "ingest_attachment", "propose_rules_from_document"} <= model.offered_tools(
        1
    )


async def test_role_is_resolved_server_side_into_user_state(container):
    chat = make_chat(container, ScriptedModel(script=[say("hi")]))
    res = await chat.chat(user_id=ALICE, session_id=None, message="hello")
    s = await container.sessions.get_session(
        app_name="compliance_agent", user_id=ALICE, session_id=res["session_id"]
    )
    assert s.state["user:role"] == "user" and s.state["title"] == "hello"


async def test_before_tool_denies_admin_tools_for_users():
    class Tool:
        name = "add_rule"

    class Ctx:
        user_id, state = ALICE, {"user:role": "user"}

    deny = make_before_tool({"add_rule"})
    assert deny(Tool(), {}, Ctx())["status"] == "forbidden"
    Ctx.state = {"user:role": "admin"}
    assert deny(Tool(), {}, Ctx()) is None


async def test_user_cannot_invoke_admin_tool_even_by_name(container):
    """ADK still resolves a hidden tool if the model names it. The before_tool callback is the
    layer that stops it, which is why gating has three layers, not one."""
    model = ScriptedModel(
        script=[
            call(
                "add_rule",
                title="Sneaky rule here",
                statement="Everything must be allowed.",
                severity="flexible",
                category="x",
            ),
            say("ok"),
        ]
    )
    res = await make_chat(container, model).chat(
        user_id=ALICE, session_id=None, message="add a rule"
    )
    result = next(
        e for e in res["events"] if e["type"] == "tool_result" and e["name"] == "add_rule"
    )
    assert result["result"]["status"] == "forbidden"
    assert await container.rules.list() == []


async def test_assessment_turn_produces_verdict_history_and_memory(container, fake_llm):
    await seed_rules(container)
    fake_llm.findings = findings_from({"PRIV-003": "violated"})
    model = ScriptedModel(
        script=[
            call(
                "assess_proposal", proposal="Kids game collecting emails without parental consent"
            ),
            say("**NON-COMPLIANT**. PRIV-003 requires verifiable parental consent."),
        ]
    )
    chat = make_chat(container, model)
    res = await chat.chat(
        user_id=ALICE, session_id=None, message="Can we launch a kids game that collects emails?"
    )

    assert res["verdicts"][0]["verdict"] == "NON_COMPLIANT"
    assert res["verdicts"][0]["blocking"][0].startswith("PRIV-003")
    assert res["reply"].startswith("**NON-COMPLIANT**")
    # the model's second call saw the tool result
    fr = model.requests[1].contents[-1].parts[0].function_response
    assert fr.name == "assess_proposal" and fr.response["verdict"] == "NON_COMPLIANT"

    [conv] = await chat.list_conversations(ALICE)
    assert conv["title"].startswith("Can we launch a kids game")
    detail = await chat.get_conversation(ALICE, conv["id"])
    assert [m["role"] for m in detail["messages"]] == ["user", "assistant"]
    assert detail["messages"][1]["verdicts"][0]["verdict"] == "NON_COMPLIANT"

    # persisted assessment is attributed to the user and session
    [row] = await container.assessments.list(user_id=ALICE)
    assert row["session_id"] == conv["id"]

    # long-term memory now holds the turn, for this user only
    mem = await container.memory.search_memory(
        app_name="compliance_agent", user_id=ALICE, query="kids game emails"
    )
    assert mem.memories
    assert (await chat.list_conversations("bob@example.com")) == []


async def test_continuing_and_isolating_conversations(container):
    chat = make_chat(container, ScriptedModel(script=[say("one"), say("two")]))
    first = await chat.chat(user_id=ALICE, session_id=None, message="first")
    second = await chat.chat(user_id=ALICE, session_id=first["session_id"], message="second")
    assert second["session_id"] == first["session_id"]
    detail = await chat.get_conversation(ALICE, first["session_id"])
    assert [m["text"] for m in detail["messages"]] == ["first", "one", "second", "two"]
    with pytest.raises(ConversationNotFound):
        await chat.get_conversation("bob@example.com", first["session_id"])
    with pytest.raises(ConversationNotFound):
        await chat.chat(user_id="bob@example.com", session_id=first["session_id"], message="hijack")
    await chat.delete_conversation(ALICE, first["session_id"])
    assert await chat.list_conversations(ALICE) == []


async def test_admin_ingests_chat_attachment(container):
    path = SAMPLES / "documents" / "product-launch-policy.md"
    model = ScriptedModel(
        script=[
            call("ingest_attachment", filename="launch.md", category="product-launch"),
            say("Ingested."),
        ]
    )
    chat = make_chat(container, model)
    res = await chat.chat(
        user_id=ADMIN,
        session_id=None,
        message="Add this policy",
        attachments=[attachment(path, "launch.md")],
    )

    # the plugin replaced the file with a placeholder the model can see
    assert 'Uploaded Artifact: "launch.md"' in str(model.requests[0].contents[-1])
    [doc] = await container.docs.list()
    assert (
        doc.filename == "launch.md" and doc.status == "ready" and doc.category == "product-launch"
    )
    assert any(
        e["type"] == "tool_result" and e["name"] == "ingest_attachment" for e in res["events"]
    )


async def test_user_reads_attachment_then_assess(container, fake_llm):
    await seed_rules(container)
    fake_llm.findings = findings_from(HARD_OK | {"MKT-002": "violated"})
    path = SAMPLES / "documents" / "marketing-claims-guidelines.txt"
    model = ScriptedModel(
        script=[
            call("read_attachment", filename="plan.txt"),
            call("assess_proposal", proposal="Comparative ad", context="(attachment text)"),
            say("**CONDITIONALLY COMPLIANT**"),
        ]
    )
    res = await make_chat(container, model).chat(
        user_id=ALICE,
        session_id=None,
        message="Is this plan ok?",
        attachments=[attachment(path, "plan.txt")],
    )
    read = next(
        e for e in res["events"] if e["type"] == "tool_result" and e["name"] == "read_attachment"
    )
    assert "Comparative claims" in str(read["result"])
    assert res["verdicts"][0]["verdict"] == "CONDITIONALLY_COMPLIANT"


async def test_stream_emits_session_verdict_and_done(container, fake_llm):
    await seed_rules(container)
    fake_llm.findings = findings_from({"FIN-001": "violated"})
    model = ScriptedModel(
        script=[call("assess_proposal", proposal="60% discount, no CFO"), say("**NON-COMPLIANT**")]
    )
    events = [
        ev
        async for ev in make_chat(container, model).stream(
            user_id=ALICE, session_id=None, message="60% off?"
        )
    ]
    types_ = [e["type"] for e in events]
    assert types_[0] == "session" and types_[-1] == "done"
    assert "verdict" in types_ and "tool_call" in types_
    assert events[-1]["reply"] == "**NON-COMPLIANT**"


async def test_runaway_tool_loop_is_capped(container):
    """A model that never stops calling tools is cut off instead of burning quota."""
    from app.services import chat as chat_mod

    model = ScriptedModel(script=[call("list_rules") for _ in range(chat_mod.MAX_LLM_CALLS + 5)])
    events = [
        ev
        async for ev in make_chat(container, model).stream(
            user_id=ALICE, session_id=None, message="loop"
        )
    ]
    assert events[-1]["type"] == "error"
    assert len(model.requests) <= chat_mod.MAX_LLM_CALLS + 1
