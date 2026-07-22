from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import io
from services.conversation_service import ConversationService
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

router = APIRouter(prefix="/ai/history", tags=["History"])
conversation_service = ConversationService()

@router.get("/{user_id}/{session_id}/export.pdf")
async def export_conversation_pdf(user_id: str, session_id: str):
    history = conversation_service.get_history(user_id, session_id)
    if not history:
        raise HTTPException(status_code=404, detail="Conversation history not found")

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    y = 750
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, f"VigilX Conversation History - {session_id}")
    y -= 30
    
    p.setFont("Helvetica", 12)
    for msg in history:
        # Simple text wrapping could be implemented here; keeping it simple for the export feature
        prefix = "User: " if msg.role == "user" else "VigilX AI: "
        
        # Split multiline messages
        lines = str(msg.content).split('\n')
        for line in lines:
            if y < 50:
                p.showPage()
                y = 750
                p.setFont("Helvetica", 12)
            
            p.drawString(50, y, prefix + line[:90])  # naive truncation
            y -= 20
            prefix = "      "
        
        y -= 10 # space between messages

    p.showPage()
    p.save()
    
    buffer.seek(0)
    return StreamingResponse(
        buffer, 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"attachment; filename=conversation_{session_id}.pdf"}
    )
