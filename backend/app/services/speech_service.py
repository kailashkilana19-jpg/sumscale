"""
OmniAid — Multimodal Extractor Service
======================================
Extracts text content from uploaded files (PDFs, images, audio, plain text)
using Gemini 2.5 Flash multimodal capabilities.

Wrapped in strict error handling and timeouts.
"""

import logging
from pathlib import Path
from google import genai
from google.genai import types

from app.config import settings
from app.services.ai_service import get_genai_client, PROMPT_INJECTION_PROTECTION

logger = logging.getLogger("omniaid.multimodal_extractor")


import base64

def _call_groq_vision(file_bytes: bytes, mime_type: str, prompt: str) -> str:
    """Fallback image text extraction using active Groq Vision models."""
    try:
        from app.services.ai_service import get_groq_client
        client = get_groq_client()
        if not client:
            return ""

        clean_mime = mime_type if "/" in mime_type else "image/png"
        b64_str = base64.b64encode(file_bytes).decode("utf-8")
        data_url = f"data:{clean_mime};base64,{b64_str}"

        # Active non-decommissioned Groq Vision models
        vision_models = ["llama-3.2-11b-vision-instruct", "llama-3.2-90b-vision-instruct"]
        for model_name in vision_models:
            try:
                res = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": data_url}},
                            ],
                        }
                    ],
                    max_tokens=2048,
                    temperature=0.1,
                )
                txt = res.choices[0].message.content
                if txt and txt.strip():
                    logger.info(f"Multimodal extraction success via Groq Vision ({model_name})")
                    return txt.strip()
            except Exception as err:
                logger.warning(f"Groq Vision {model_name} failed: {err}")
    except Exception as exc:
        logger.warning(f"Groq Vision helper error: {exc}")
    return ""


def _call_ocr_space(file_bytes: bytes, mime_type: str, filename: str = "document.png") -> str:
    """Fallback OCR using OCR.space free API engine (supports images and PDFs)."""
    import httpx
    try:
        url = "https://api.ocr.space/parse/image"
        payload = {
            "apikey": "helloworld",
            "language": "eng",
            "isOverlayRequired": False,
            "detectOrientation": True,
            "scale": True,
            "OCREngine": "2"
        }
        files = {"file": (filename, file_bytes, mime_type)}
        with httpx.Client(timeout=25.0) as http_client:
            res = http_client.post(url, data=payload, files=files)
            if res.status_code == 200:
                data = res.json()
                results = data.get("ParsedResults", [])
                if results and results[0].get("ParsedText"):
                    txt = results[0]["ParsedText"].strip()
                    if txt and len(txt) > 10:
                        logger.info("OCR.space engine extraction success!")
                        return txt
    except Exception as exc:
        logger.warning(f"OCR.space engine call failed: {exc}")
    return ""


def _extract_pdf_text(file_path: Path) -> str:
    """Extracts text locally from PDF using pypdf without external API calls."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(file_path))
        parts = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text and page_text.strip():
                parts.append(f"--- Page {i + 1} ---\n{page_text.strip()}")
        full_text = "\n\n".join(parts).strip()
        if full_text and len(full_text) > 15:
            logger.info(f"Local pypdf extraction success for {file_path.name} ({len(reader.pages)} pages, {len(full_text)} chars)")
            return full_text
    except Exception as exc:
        logger.warning(f"Local pypdf extraction error for {file_path.name}: {exc}")
    return ""


async def extract_text_from_file(file_path: Path, mime_type: str) -> str:
    """
    Extracts text/transcript from PDF, image, audio, or text file.
    Uses local pypdf for PDFs, UTF-8 reading for plain text/CSV,
    and Gemini / Groq Vision / OCR.space multimodal for images/scans/audio.
    """
    # 1. Plain text / CSV files read directly
    if mime_type.startswith("text/") or mime_type in ("text/plain", "text/csv", "application/csv", "application/json") or file_path.suffix.lower() in (".txt", ".csv", ".json", ".md", ".log"):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()[:15000]
                if content and content.strip():
                    return content.strip()
        except Exception as e:
            logger.error(f"Failed to read text file {file_path}: {e}")
            return f"Document file {file_path.name} attached for review."

    # 2. PDFs — Fast local extraction first via pypdf
    is_pdf = mime_type == "application/pdf" or file_path.suffix.lower() == ".pdf"
    if is_pdf:
        local_pdf_text = _extract_pdf_text(file_path)
        if local_pdf_text:
            return local_pdf_text[:15000]

    # 3. Read raw file bytes for API multimodal / OCR processing
    try:
        with open(file_path, "rb") as f:
            file_bytes = f.read()
    except Exception as e:
        logger.error(f"Failed to read bytes for {file_path.name}: {e}")
        return f"Uploaded document: {file_path.name}. Preserved for AI case analysis."

    # 4. Multimodal extraction via Gemini (if configured and working)
    extracted = None
    try:
        client = get_genai_client()
        if client:
            file_part = types.Part.from_bytes(
                data=file_bytes,
                mime_type=mime_type,
            )
            prompt = f"""{PROMPT_INJECTION_PROTECTION}

Task: Transcribe or extract all visible text, numbers, dates, addresses, claimed amounts, URLs, spoken audio, or document details from the attached file.
Language Recognition Rule: The file or spoken audio may be in any language (English, Hindi, Telugu, Tamil, Kannada, etc.). Accurately extract all text, numbers, links, headers, amounts, and specific details preserving key terms.
Return plain text summary/transcription ONLY.
"""
            for model_name in ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.0-flash-lite"]:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=[file_part, prompt],
                        config=types.GenerateContentConfig(
                            temperature=0.1,
                            max_output_tokens=4096,
                        ),
                    )
                    if response and response.text and response.text.strip():
                        extracted = response.text.strip()
                        logger.info(f"Multimodal extraction success via {model_name} for {file_path.name}")
                        break
                except Exception as e:
                    logger.warning(f"Multimodal extraction failed with {model_name} for {file_path.name}: {type(e).__name__}: {e}")
    except Exception as e:
        logger.warning(f"Gemini client setup error: {e}")

    # 5. Fallback for Images via Groq Vision
    if not extracted and mime_type.startswith("image/"):
        groq_prompt = "Extract all readable text, values, numbers, and medical/financial details from this image accurately."
        extracted = _call_groq_vision(file_bytes, mime_type, groq_prompt)

    # 6. Fallback via OCR.space Engine (works on images and scanned PDFs)
    if not extracted and (mime_type.startswith("image/") or is_pdf):
        ocr_filename = file_path.name if is_pdf else "document.png"
        extracted = _call_ocr_space(file_bytes, mime_type, filename=ocr_filename)

    if not extracted or "content extraction failed" in extracted.lower():
        logger.warning(f"Using default fallback descriptor for {file_path.name}")
        return f"Uploaded document: {file_path.name} ({len(file_bytes)} bytes). Content preserved for AI case analysis and threat audit."

    return extracted[:15000]

