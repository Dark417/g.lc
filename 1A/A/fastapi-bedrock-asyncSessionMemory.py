import os
import uuid
import asyncio
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import boto3
from botocore.config import Config

app = FastAPI(title="Async Bedrock Agent Service")

# Initialize AWS Bedrock Asynchronous Client
# Configured with an adaptive retry strategy for production resilience
aws_config = Config(
    retries={"max_attempts": 3, "mode": "adaptive"},
    region_name=os.getenv("AWS_REGION", "us-east-1")
)
bedrock_runtime = boto3.client("bedrock-runtime", config=aws_config)

# --- MEMORY LAYER ARCHITECTURE ---
# Mocking an external Cache/DB store. In production, swap this dictionary 
# with an async Redis client (like redis-py) or DynamoDB client.
# Key: session_id (UUID string) -> Value: Dict containing context history and state
MOCK_REDIS_CACHE: Dict[str, Dict[str, Any]] = {}

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    session_id: str
    response: str

# --- MOCK TOOL DEFINITION (The "ADK" or Harness Layer) ---
async def fetch_rds_database_data(query_param: str) -> str:
    """Simulates a call to an RDS Database or an external structured query source."""
    await asyncio.sleep(0.5) # Simulating I/O call
    return f"Database result for '{query_param}': Status is Active, Balance is $5,400."

# --- CHAT ENDPOINT (FastAPI Async Event Loop) ---
@app.post("/chat/{session_id}", response_model=ChatResponse)
async def handle_agent_chat(session_id: str, request: ChatRequest):
    # 1. Thread/Context Isolation: Retrieve session context from the cache store
    if session_id == "new" or session_id not in MOCK_REDIS_CACHE:
        session_id = str(uuid.uuid4())
        MOCK_REDIS_CACHE[session_id] = {
            "history": [{"role": "system", "content": "You are a helpful cloud engineer assistant."}],
            "graph_state": "idle"
        }
    
    session_data = MOCK_REDIS_CACHE[session_id]
    
    # Check session lock to prevent concurrent modifications on the same thread
    if session_data["graph_state"] == "running":
        raise HTTPException(status_code=409, detail="Agent is currently processing a prior request on this session.")
        
    session_data["graph_state"] = "running"
    
    try:
        # Append incoming message to the isolated session history
        session_data["history"].append({"role": "user", "content": request.message})
        
        # 2. Dynamic Tool Routing Execution Logic (Orchestrator Layer)
        # If the user asks for database numbers, we explicitly orchestrate the data fetch in code
        if "database" in request.message.lower() or "balance" in request.message.lower():
            # Code-first retrieval instead of relying on native Bedrock generative queries for SQL
            db_context = await fetch_rds_database_data("user_profile_data")
            session_data["history"].append({
                "role": "system", 
                "content": f"Context from Postgres Database: {db_context}"
            })

        # 3. Compile Prompt Payload
        # We pass the completely assembled history & contextual information down to Bedrock
        # This payload construction is handled natively in your compute environment (ECS/EKS)
        prompt_content = "\n".join([f"{msg['role']}: {msg['content']}" for msg in session_data["history"]]) + "\nassistant:"

        # Format input for Amazon Nova or Anthropic Claude models on Bedrock
        body_payload = {
            "inferenceConfig": {"maxTokens": 500, "temperature": 0.7},
            "messages": [{"role": "user", "content": [{"text": prompt_content}]}]
        }

        # 4. Offloading to Bedrock (Non-blocking I/O)
        # Using a thread pool executor because standard boto3 client calls are synchronous
        loop = asyncio.get_running_loop()
        
        # Target model ID: Amazon Nova Pro or Anthropic Claude 3.5 Sonnet
        model_id = "us.amazon.nova-pro-v1:0" 
        
        # The thread yields control back to the FastAPI event loop while waiting for Bedrock to compute
        response = await loop.run_in_executor(
            None,
            lambda: bedrock_runtime.converse(
                modelId=model_id,
                messages=body_payload["messages"]
            )
        )
        
        # 5. Extract and Commit Response to State
        ai_response_text = response["output"]["message"]["content"][0]["text"]
        session_data["history"].append({"role": "assistant", "content": ai_response_text})
        
        return ChatResponse(session_id=session_id, response=ai_response_text)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Agent Error: {str(e)}")
        
    finally:
        # Release the session lock so the conversation can accept the next turn
        session_data["graph_state"] = "idle"
