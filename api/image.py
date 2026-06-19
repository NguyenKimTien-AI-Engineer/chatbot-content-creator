from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import Optional
import asyncio
import os

import google.generativeai as genai


router = APIRouter()

GEMINI_VISION_MODEL = os.getenv("GEMINI_VISION_MODEL", "gemini-2.5-flash")
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""


def _get_model() -> genai.GenerativeModel:
    genai.configure(api_key=GOOGLE_API_KEY)
    return genai.GenerativeModel(GEMINI_VISION_MODEL)


def _analysis_prompt() -> str:
    return (
        "Phân tích thật chi tiết hình ảnh: mô tả đối tượng, màu sắc, chất liệu,"
        " phong cách tổng thể, bối cảnh; đánh giá chất lượng và cảm xúc hình ảnh."
        " Rút ra cảm nhận ngắn gọn phù hợp với sản phẩm thời trang da thật."
    )


async def _analyze_image_bytes(image_bytes: bytes, mime_type: str) -> str:
    """Phân tích ảnh bằng Gemini và trả về mô tả chi tiết."""
    model = _get_model()

    def _run() -> str:
        response = model.generate_content(
            [
                _analysis_prompt(),
                {"mime_type": mime_type, "data": image_bytes},
            ]
        )
        return response.text or ""

    return await asyncio.to_thread(_run)


@router.post("/v1/analyze-image")
@router.post("/v1/analyze-image/")
async def analyze_image_endpoint(
    file: Optional[UploadFile] = File(None),
    url: Optional[str] = Form("")
):
    try:
        if file is not None:
            content = await file.read()
            mime = file.content_type or "image/png"
            text = await _analyze_image_bytes(content, mime)
            resp = {"status": 200, "message": "success", "data": {"image_text": text}}
            return JSONResponse(content=jsonable_encoder(resp), status_code=200)

        if url:
            model = _get_model()

            def _run_url() -> str:
                response = model.generate_content([_analysis_prompt(), url])
                return response.text or ""

            text = await asyncio.to_thread(_run_url)
            resp = {"status": 200, "message": "success", "data": {"image_text": text}}
            return JSONResponse(content=jsonable_encoder(resp), status_code=200)

        resp = {"status": 400, "message": "No image provided"}
        return JSONResponse(content=jsonable_encoder(resp), status_code=400)

    except Exception as e:
        resp = {"status": 400, "message": "Error: " + str(e)}
        return JSONResponse(content=jsonable_encoder(resp), status_code=400)
