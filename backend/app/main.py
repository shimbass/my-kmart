# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from .services.ocr_service import OCRService
from .services.db_service import DatabaseService
from .services.stats_service import StatsService
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
stats_service = StatsService(db_service.client)


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
async def get_receipts(
    limit: int = 20,
    start_date: str = None,
    end_date: str = None,
    store_name: str = None,
    card_name: str = None,
    search: str = None
):
    """저장된 영수증 목록을 조회합니다."""
    try:
        result = await db_service.get_receipts(
            limit=limit,
            start_date=start_date,
            end_date=end_date,
            store_name=store_name,
            card_name=card_name,
            search=search
        )
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


# ===== Statistics APIs =====

@app.get("/api/stats/summary")
async def get_stats_summary(start_date: str = None, end_date: str = None):
    """기간별 요약 통계를 조회합니다."""
    try:
        result = await stats_service.get_summary(start_date, end_date)
        return json_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats/monthly")
async def get_monthly_stats(start_date: str = None, end_date: str = None):
    """월별 지출 통계를 조회합니다."""
    try:
        result = await stats_service.get_monthly_stats(start_date, end_date)
        return json_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats/by-store")
async def get_store_stats(start_date: str = None, end_date: str = None):
    """상점별 지출 통계를 조회합니다."""
    try:
        result = await stats_service.get_store_stats(start_date, end_date)
        return json_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats/by-card")
async def get_card_stats(start_date: str = None, end_date: str = None):
    """카드별 지출 통계를 조회합니다."""
    try:
        result = await stats_service.get_card_stats(start_date, end_date)
        return json_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats/frequent-items")
async def get_frequent_items(start_date: str = None, end_date: str = None, limit: int = 10):
    """자주 구매하는 상품 통계를 조회합니다."""
    try:
        result = await stats_service.get_frequent_items(start_date, end_date, limit)
        return json_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats/store/{store_name}/cards")
async def get_store_card_stats(store_name: str, start_date: str = None, end_date: str = None):
    """특정 상점의 카드별 지출 통계를 조회합니다."""
    try:
        result = await stats_service.get_store_card_stats(store_name, start_date, end_date)
        return json_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class DiscountRequest(BaseModel):
    name: str
    amount: int
    item_id: int | None = None


@app.post("/api/receipts/{receipt_id}/discounts")
async def add_discount(receipt_id: int, request: DiscountRequest):
    """특정 영수증에 할인 항목을 추가합니다."""
    try:
        result = await db_service.add_discount(receipt_id, request.name, request.amount, request.item_id)
        return json_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== Admin APIs =====

@app.post("/api/admin/cleanup")
async def cleanup_data():
    """기존 DB 데이터 유효성 검사 및 정리.
    - items.no 없으면 레코드 순서대로 001부터 부여
    - receipts.card_name 없으면 raw_text 분석으로 결제수단 추론
    """
    try:
        result = await db_service.cleanup_data()
        return json_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/admin/migrate-discounts")
async def migrate_discounts():
    """기존 items 테이블의 할인 항목을 discounts 테이블로 이전합니다.
    실행 전 Supabase에서 discounts 테이블이 생성되어 있어야 합니다.
    (backend/scripts/create_discounts_table.sql 참고)
    """
    try:
        result = await db_service.migrate_discounts()
        return json_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
