from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

from src.schemas.chat import ChatRequest, ChatResponse
from src.services.conversation_service import ConversationService

router = APIRouter()

# HTTP эндпоинт для простого текстового чата
conversation = ConversationService()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Простой текстовый чат через HTTP."""
    response = await conversation.chat(request.message, speaker=request.speaker)
    return ChatResponse(response=response, session_id=conversation.current_session_id)


@router.post("/chat/new-session")
async def new_session():
    """Начинает новую сессию."""
    session_id = await conversation.start_session()
    return {"session_id": session_id}


# WebSocket для реального времени (голос, стриминг)
@router.websocket("/ws")
async def websocket_chat(ws: WebSocket):
    """WebSocket для реалтайм общения.

    Формат сообщений:
    -> {"type": "chat", "message": "привет", "speaker": "User"}
    <- {"type": "response", "message": "...", "session_id": "..."}
    """
    await ws.accept()
    ws_conversation = ConversationService()
    await ws_conversation.start_session()

    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)

            if msg["type"] == "chat":
                response = await ws_conversation.chat(
                    msg["message"],
                    speaker=msg.get("speaker"),
                )
                await ws.send_json({
                    "type": "response",
                    "message": response,
                    "session_id": ws_conversation.current_session_id,
                })

    except WebSocketDisconnect:
        await ws_conversation.end_session()
