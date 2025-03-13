from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llm_bot import get_ai_response, init_db, sync_chat_history
import uvicorn
from typing import List, Dict, Any

app = FastAPI(title="WhatsApp AI Bot API")

class MessageRequest(BaseModel):
    phone: str
    message: str

class MessageResponse(BaseModel):
    response: str

class ChatHistoryRequest(BaseModel):
    phone: str
    messages: List[Dict[str, Any]]

@app.on_event("startup")
async def startup_event():
    init_db()

@app.post("/chat", response_model=MessageResponse)
async def chat(request: MessageRequest):
    try:
        response = get_ai_response(request.phone, request.message)
        return MessageResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sync_history")
async def sync_history(request: ChatHistoryRequest):
    try:
        sync_chat_history(request.phone, request.messages)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True) 