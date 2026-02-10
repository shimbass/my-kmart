# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from .services.ocr_service import OCRService
from .services.db_service import DatabaseService
import os
import json

app = FastAPI(title="K마트 영수증 스캐너 API")

# CORS 설정 (로컬 네트워크 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발용: 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 서비스 초기화
ocr_service = OCRService()
db_service = DatabaseService()


class ImageRequest(BaseModel):
    image: str  # base64 encoded image


class ProductItem(BaseModel):
    no: str
    name: str
    barcode: str | None = None
    unitPrice: int
    quantity: int
    amount: int


class OCRResponse(BaseModel):
    success: bool
    storeName: str | None = None
    cardName: str | None = None
    items: list[ProductItem] = []
    rawText: str = ""
    purchaseDateTime: str | None = None
    error: str | None = None


class SaveReceiptRequest(BaseModel):
    items: list[ProductItem] = []
    rawText: str = ""
    storeName: str | None = None
    cardName: str | None = None
    purchaseDateTime: str | None = None


# UTF-8 JSON 응답 헬퍼
def json_response(data: dict):
    return JSONResponse(
        content=data,
        media_type="application/json; charset=utf-8"
    )


@app.get("/")
async def root():
    return json_response({"message": "K마트 영수증 스캐너 API", "status": "running"})


@app.get("/health")
async def health_check():
    api_key = os.getenv("GEMINI_API_KEY")
    return json_response({
        "status": "healthy",
        "gemini_configured": bool(api_key),
        "database_connected": db_service.is_connected()
    })


@app.post("/api/ocr")
async def process_receipt(request: ImageRequest):
    """영수증 이미지를 분석하여 상품 정보를 추출합니다."""
    try:
        result = await ocr_service.process_image(request.image)
        return json_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/receipts")
async def save_receipt(request: SaveReceiptRequest):
    """인식된 영수증 결과를 데이터베이스에 저장합니다."""
    try:
        data = {
            "items": [item.model_dump() for item in request.items],
            "rawText": request.rawText,
            "storeName": request.storeName,
            "cardName": request.cardName,
            "purchaseDateTime": request.purchaseDateTime
        }
        result = await db_service.save_receipt(data)
        return json_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/receipts")
async def get_receipts(limit: int = 20):
    """저장된 영수증 목록을 조회합니다."""
    try:
        result = await db_service.get_receipts(limit)
        return json_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/receipts/{receipt_id}")
async def get_receipt_detail(receipt_id: int):
    """특정 영수증의 상세 정보를 조회합니다."""
    try:
        result = await db_service.get_receipt_detail(receipt_id)
        return json_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/receipts/{receipt_id}")
async def delete_receipt(receipt_id: int):
    """영수증을 삭제합니다."""
    try:
        result = await db_service.delete_receipt(receipt_id)
        return json_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
