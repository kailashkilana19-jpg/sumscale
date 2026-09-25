"""
OmniAid — RAG Chatbot Router
============================
POST /chat — Endpoint for grounded conversational Q&A over the user's case history.

Security Rules:
- Rate limited separately (10 attempts per minute per IP).
- RAG context is strictly filtered by user_id == current_user.id.
- User input wrapped in <user_data> delimiters.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from app.schemas.chat import ChatRequest, ChatResponse
from app.dependencies.auth import get_current_user
from app.models.user import UserInDB
from app.utils.limiter import limiter
from app.services.chat_service import generate_grounded_chat_response

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post(
    "",
    response_model=ChatResponse,
    summary="Grounded AI Assistant Q&A over user case history",
)
@limiter.limit("10/minute")
async def chat_with_assistant(
    request: Request,
    body: ChatRequest,
    current_user: UserInDB = Depends(get_current_user),
):
    from app.routers.case import get_case_record, list_case_records, save_case_record

    db = getattr(request.app.state, "db", None)

    # SECURITY RULE: Fetch cases owned by current_user.id, scoped strictly to case_id if provided
    user_cases = []
    if body.case_id:
        c_doc = await get_case_record(db, body.case_id, current_user.id)
        if c_doc:
            user_cases = [c_doc]

    if not user_cases:
        user_cases = await list_case_records(db, current_user.id)

    if not user_cases:
        user_cases = [{
            "_id": body.case_id or "default_case",
            "department": "health",
            "title": "Uploaded Document Analysis",
            "evidence": [],
            "findings": {
                "summary": "Document records processed and available for analysis.",
                "remediation_checklist": ["Review document details", "Ask any follow-up questions"]
            }
        }]

    # Auto-correct case department if evidence or query contains fraud/scam/invoice indicators
    fraud_keywords = [
        "fraud", "scam", "bank", "otp", "phishing", "sms", "link",
        "whatsapp", "transaction", "money", "account", "police", "card",
        "cyber", "verify", "paytm", "upi", "lottery", "prize", "urgent",
        "invoice", "payment", "due date", "transfer", "shipment", "suspension",
        "login", "claim", "winner", "security", "unusual activity", "wire",
        "credit card", "debit card", "pin", "password", "tax", "customs",
        "fee", "forfeited", "logistics", "accounts department", "warehouse"
    ]
    # Auto-re-extract OCR text for evidence items that have placeholder strings or missing text
    from pathlib import Path
    from app.services.speech_service import extract_text_from_file

    for c in user_cases:
        updated_ev_flag = False
        evidence_list = c.get("evidence", [])
        for ev in evidence_list:
            cur_txt = (ev.get("extracted_text") or "").strip()
            stored_path = ev.get("meta", {}).get("stored_path")
            mime_type = ev.get("file_type") or "image/png"

            if (not cur_txt or "uploaded document:" in cur_txt.lower() or "preserved for ai" in cur_txt.lower() or len(cur_txt) < 80) and stored_path:
                p = Path(stored_path)
                if p.exists():
                    try:
                        fresh_text = await extract_text_from_file(p, mime_type)
                        if fresh_text and "uploaded document:" not in fresh_text.lower():
                            ev["extracted_text"] = fresh_text
                            updated_ev_flag = True
                    except Exception as ocr_err:
                        pass

        if updated_ev_flag:
            await save_case_record(db, c, current_user.id)

        # Auto-correct case department if evidence or query contains fraud/scam/invoice indicators
        ev_text = " ".join([e.get("extracted_text", "") for e in evidence_list]).lower()
        if c.get("department") != "fraud" and any(k in ev_text for k in fraud_keywords):
            c["department"] = "fraud"
            await save_case_record(db, c, current_user.id)

    result = await generate_grounded_chat_response(
        user_message=body.message.strip(),
        user_cases=user_cases,
        language=body.language or "en",
        chat_history=body.chat_history or [],
        db=db,
    )

    return ChatResponse(
        answer=result["answer"],
        cited_cases=result["cited_cases"],
        suggested_next_questions=result.get("suggested_next_questions", []),
        auto_generated_title=result.get("auto_generated_title", None),
    )


@router.get(
    "/tts",
    summary="Proxy Text-to-Speech audio bytes server-to-server",
)
async def get_tts_audio(text: str, lang: str = "en"):
    """
    Proxy Google TTS API server-to-server to stream audio/mpeg
    directly to the frontend without browser CORS or origin restrictions.
    """
    clean_text = text[:300].strip()
    if not clean_text:
        raise HTTPException(status_code=400, detail="Text is required for TTS")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    import httpx
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(
                "https://translate.google.com/translate_tts",
                params={
                    "ie": "UTF-8",
                    "q": clean_text,
                    "tl": lang,
                    "client": "tw-ob",
                },
                headers=headers,
            )

            if res.status_code != 200:
                raise HTTPException(status_code=502, detail="TTS service error")

            return Response(content=res.content, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS generation error: {str(e)}")
