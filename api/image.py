from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import Optional
import base64
import asyncio

from openai import OpenAI


router = APIRouter()


async def _analyze_image_bytes(image_bytes: bytes, mime_type: str) -> str:
    """Phân tích ảnh bằng OpenAI và trả về mô tả chi tiết.

    Hàm chạy tác vụ đồng bộ của OpenAI trong thread để giữ async cho FastAPI.
    """
    client = OpenAI()
    data_url = f"data:{mime_type};base64," + base64.b64encode(image_bytes).decode("utf-8")

    def _run() -> str:
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Phân tích thật chi tiết hình ảnh: mô tả đối tượng, màu sắc, chất liệu,"
                                " phong cách tổng thể, bối cảnh; đánh giá chất lượng và cảm xúc hình ảnh."
                                " Rút ra cảm nhận ngắn gọn phù hợp với sản phẩm thời trang da thật."
                            ),
                        },
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }
            ],
        )
        return res.choices[0].message.content or ""

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
            client = OpenAI()

            def _run_url() -> str:
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": (
                                        "Phân tích thật chi tiết hình ảnh: mô tả đối tượng, màu sắc, chất liệu,"
                                        " phong cách tổng thể, bối cảnh; đánh giá chất lượng và cảm xúc hình ảnh."
                                        " Rút ra cảm nhận ngắn gọn phù hợp với sản phẩm thời trang da thật."
                                    ),
                                },
                                {"type": "image_url", "image_url": {"url": url}},
                            ],
                        }
                    ],
                )
                return res.choices[0].message.content or ""

            text = await asyncio.to_thread(_run_url)
            resp = {"status": 200, "message": "success", "data": {"image_text": text}}
            return JSONResponse(content=jsonable_encoder(resp), status_code=200)

        resp = {"status": 400, "message": "No image provided"}
        return JSONResponse(content=jsonable_encoder(resp), status_code=400)

    except Exception as e:
        resp = {"status": 400, "message": "Error: " + str(e)}
        return JSONResponse(content=jsonable_encoder(resp), status_code=400)