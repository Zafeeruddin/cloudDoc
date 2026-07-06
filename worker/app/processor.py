from __future__ import annotations

import json
import logging
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader

logger = logging.getLogger(__name__)

TEXT_CONTENT_TYPES = {
    "text/plain",
    "text/markdown",
    "text/csv",
    "application/json",
    "application/xml",
}


def extract_text_and_metadata(content: bytes, filename: str, content_type: str) -> tuple[str, dict]:
    suffix = Path(filename).suffix.lower()
    extracted_text = ""

    if content_type == "application/pdf" or suffix == ".pdf":
        extracted_text = _extract_pdf_text(content)
    elif content_type in TEXT_CONTENT_TYPES or suffix in {".txt", ".md", ".csv", ".json"}:
        extracted_text = content.decode("utf-8", errors="ignore")
    else:
        try:
            extracted_text = content.decode("utf-8", errors="ignore")
        except UnicodeDecodeError:
            extracted_text = ""

    normalized_text = extracted_text.strip()
    summary = normalized_text[:240] if normalized_text else "No extractable text content found."
    metadata = {
        "filename": filename,
        "content_type": content_type,
        "summary": summary,
        "text_length": len(normalized_text),
        "line_count": len([line for line in normalized_text.splitlines() if line.strip()]),
        "preview_json": _safe_json_preview(normalized_text, content_type),
    }
    return normalized_text, metadata


def _extract_pdf_text(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages)


def _safe_json_preview(text: str, content_type: str) -> dict | None:
    if content_type != "application/json" or not text:
        return None
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        logger.warning("invalid_json_content")
        return None
    if isinstance(parsed, dict):
        return dict(list(parsed.items())[:10])
    return {"type": type(parsed).__name__}

