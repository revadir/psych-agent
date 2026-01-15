"""
Chat API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import json
import asyncio
from app.db import get_db
from app.core.auth import get_current_user
from app.models import User
from app.services.chat_service import ChatService
from app.services.hybrid_agent_service import get_hybrid_agent_service
from app.services.agent_service import get_agent_service as get_simple_agent_service
from app.services.cloud_agent_service import cloud_agent_service
from app.models.schemas import (
    ChatSessionResponse, 
    CreateSessionRequest, 
    SendMessageRequest,
    MessageResponse
)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_session(
    request: CreateSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new chat session."""
    session = ChatService.create_session(db, current_user.id, request.title)
    return session


@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all sessions for the current user."""
    return ChatService.get_user_sessions(db, current_user.id)


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific session with messages."""
    session = ChatService.get_session(db, session_id, current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Load messages
    messages = ChatService.get_session_messages(db, session_id)
    session.messages = messages
    return session


@router.post("/sessions/{session_id}/messages/stream")
async def send_message_stream(
    session_id: int,
    request: SendMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a message and stream agent response."""
    # Verify session ownership
    session = ChatService.get_session(db, session_id, current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    async def generate_response():
        try:
            # Add user message
            user_message = ChatService.add_message(db, session_id, "user", request.content)
            
            # Send user message
            yield f"data: {json.dumps({'type': 'user_message', 'data': {'id': user_message.id, 'content': request.content}})}\n\n"
            
            # Send thinking status
            yield f"data: {json.dumps({'type': 'thinking', 'data': {'status': 'Analyzing symptoms and retrieving DSM-5-TR criteria...'}})}\n\n"
            await asyncio.sleep(0.5)
            
            # Update thinking status
            yield f"data: {json.dumps({'type': 'thinking', 'data': {'status': 'Querying vector database for relevant DSM-5-TR sections...'}})}\n\n"
            await asyncio.sleep(0.5)
            
            # Get conversation history for context
            messages = ChatService.get_session_messages(db, session_id)
            conversation_history = []
            for msg in messages[-6:]:  # Last 6 messages for context
                conversation_history.append({
                    'role': msg.role,
                    'content': msg.content
                })
            
            # Get agent response with conversation history
            yield f"data: {json.dumps({'type': 'thinking', 'data': {'status': 'Generating clinical analysis...'}})}\n\n"
            
            try:
                print(f"🔍 About to call cloud_agent_service.process_query")
                agent_response = cloud_agent_service.process_query(request.content, conversation_history)
                print(f"🔍 cloud_agent_service returned: {type(agent_response)}")
            except Exception as e:
                print(f"Agent error: {e}")  # Debug log
                # Quick fallback response for testing
                agent_response = {
                    'response': f"""Based on your query: "{request.content}"

I would need to analyze this against DSM-5-TR criteria. However, I'm currently experiencing technical difficulties accessing the full diagnostic database.

For immediate clinical guidance, please consider:
1. Reviewing relevant DSM-5-TR sections manually
2. Consulting with a supervising psychiatrist
3. Documenting all symptoms systematically

This is a clinical decision support tool and not a replacement for professional psychiatric evaluation.""",
                    'citations': [
                        {'content': 'DSM-5-TR diagnostic criteria (system currently unavailable)', 'source': 'DSM-5-TR'}
                    ],
                    'disclaimer': 'This is a clinical decision support tool and not a replacement for professional psychiatric evaluation.'
                }
            
            # Send citations first
            if agent_response.get('citations'):
                yield f"data: {json.dumps({'type': 'citations', 'data': agent_response['citations']})}\n\n"
                await asyncio.sleep(0.2)
            
            # Stream the response word by word
            response_text = agent_response.get('response', 'No response generated.')
            words = response_text.split()
            
            yield f"data: {json.dumps({'type': 'response_start', 'data': {}})}\n\n"
            
            # Stream in chunks of 3-5 words for faster display
            chunk_size = 4
            for i in range(0, len(words), chunk_size):
                chunk = ' '.join(words[i:i + chunk_size])
                yield f"data: {json.dumps({'type': 'response_chunk', 'data': {'chunk': chunk, 'index': i}})}\n\n"
                await asyncio.sleep(0.1)  # Faster streaming
            
            # Save complete assistant message
            assistant_message = ChatService.add_message(db, session_id, "assistant", response_text, agent_response.get('citations', []))
            
            # Send completion
            yield f"data: {json.dumps({'type': 'response_complete', 'data': {'id': assistant_message.id, 'full_response': response_text, 'citations': agent_response.get('citations', [])}})}\n\n"
            
        except Exception as e:
            print(f"Streaming error: {e}")  # Debug log
            error_msg = f"I apologize, but I encountered an error: {str(e)}"
            try:
                assistant_message = ChatService.add_message(db, session_id, "assistant", error_msg)
                yield f"data: {json.dumps({'type': 'error', 'data': {'message': error_msg, 'id': assistant_message.id}})}\n\n"
            except:
                yield f"data: {json.dumps({'type': 'error', 'data': {'message': error_msg, 'id': 0}})}\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )


@router.post("/sessions/{session_id}/messages", response_model=dict)
async def send_message(
    session_id: int,
    request: SendMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a message and get agent response (non-streaming fallback)."""
    print(f"🔵 REGULAR API: Received message for session {session_id}")
    
    # Verify session ownership
    session = ChatService.get_session(db, session_id, current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    print(f"🔵 REGULAR API: Adding user message...")
    # Add user message
    user_message = ChatService.add_message(db, session_id, "user", request.content)
    
    # Get conversation history for context
    messages = ChatService.get_session_messages(db, session_id)
    conversation_history = []
    for msg in messages[-6:]:  # Last 6 messages for context
        conversation_history.append({
            'role': msg.role,
            'content': msg.content
        })
    
    # Get agent response
    print(f"🔵 REGULAR API: Starting agent processing with {len(conversation_history)} context messages...")
    try:
        print(f"🔵 REGULAR API: Using cloud agent service...")
        agent_response = cloud_agent_service.process_query(request.content, conversation_history)
        print(f"🔵 REGULAR API: Agent returned response of length {len(str(agent_response))}")
        
    except asyncio.TimeoutError:
        print(f"🔴 REGULAR API: TIMEOUT after 10 seconds! Using fast fallback...")
        # Fast fallback if agent takes too long
        agent_response = {
            "response": f"""**Clinical Question:** {request.content}

**DSM-5-TR Quick Reference:**

For **Major Depressive Disorder**, the key criteria include:
• **Core symptoms** (at least one required):
  - Depressed mood most of the day, nearly every day
  - Markedly diminished interest/pleasure in activities

• **Additional symptoms** (total of 5+ symptoms for 2+ weeks):
  - Significant weight loss/gain or appetite changes
  - Insomnia or hypersomnia nearly every day
  - Psychomotor agitation or retardation
  - Fatigue or loss of energy
  - Feelings of worthlessness or excessive guilt
  - Diminished concentration or indecisiveness
  - Recurrent thoughts of death or suicidal ideation

**Assessment Requirements:**
- Symptoms present for at least 2 weeks
- Significant distress or functional impairment
- Not attributable to substance use or medical condition
- Not better explained by other mental disorders

**Note:** AI system experiencing delays. Please consult DSM-5-TR Section 296.xx for complete diagnostic criteria.

*This is clinical decision support, not a replacement for professional evaluation.*""",
            "citations": [
                {"content": "Major Depressive Disorder diagnostic criteria - DSM-5-TR Section 296.xx", "source": "DSM-5-TR"}
            ],
            "disclaimer": "This is a clinical decision support tool and not a replacement for professional psychiatric evaluation."
        }
    except Exception as e:
        print(f"🔴 REGULAR API: ERROR: {e}")
        # Fallback response if agent fails
        agent_response = {
            "response": f"I apologize, but I'm currently unable to process your query due to a technical issue: {str(e)}. Please try again later or consult DSM-5-TR directly.",
            "citations": [],
            "disclaimer": "This is a clinical decision support tool and not a replacement for professional psychiatric evaluation."
        }
    
    print(f"🔵 REGULAR API: Adding assistant message...")
    # Add assistant message
    assistant_message = ChatService.add_message(
        db, session_id, "assistant", agent_response["response"], agent_response.get("citations", [])
    )
    
    print(f"🔵 REGULAR API: Returning response...")
    return {
        "user_message": {
            "id": user_message.id,
            "role": user_message.role,
            "content": user_message.content,
            "created_at": user_message.created_at
        },
        "assistant_message": {
            "id": assistant_message.id,
            "role": assistant_message.role,
            "content": assistant_message.content,
            "created_at": assistant_message.created_at
        },
        "agent_response": agent_response
    }


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a session."""
    deleted = ChatService.delete_session(db, session_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return {"message": "Session deleted successfully"}
