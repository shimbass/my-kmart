# -*- coding: utf-8 -*-
from supabase import create_client, Client
import os
import re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class DatabaseService:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if url and key:
            self.client: Client = create_client(url, key)
        else:
            self.client = None

    def is_connected(self) -> bool:
        return self.client is not None

    async def save_receipt(self, data: dict) -> dict:
        """영수증 인식 결과를 데이터베이스에 저장합니다."""
        if not self.client:
            return {"success": False, "error": "데이터베이스 연결이 설정되지 않았습니다."}

        try:
            items = data.get("items", [])
            total_amount = sum(item.get("amount", 0) for item in items)

            # 영수증 정보 저장
            receipt_data = {
                "store_name": data.get("storeName"),
                "card_name": data.get("cardName"),
                "purchase_datetime": data.get("purchaseDateTime"),
                "raw_text": data.get("rawText", ""),
                "total_amount": total_amount
            }

            receipt_result = self.client.table("receipts").insert(receipt_data).execute()

            if not receipt_result.data:
                return {"success": False, "error": "영수증 저장 실패"}

            receipt_id = receipt_result.data[0]["id"]

            # 상품 항목 저장
            if items:
                items_data = []
                for item in items:
                    items_data.append({
                        "receipt_id": receipt_id,
                        "no": item.get("no", ""),
                        "name": item.get("name", ""),
                        "barcode": item.get("barcode"),
                        "unit_price": item.get("unitPrice", 0),
                        "quantity": item.get("quantity", 0),
                        "amount": item.get("amount", 0)
                    })

                self.client.table("items").insert(items_data).execute()

            return {
                "success": True,
                "receipt_id": receipt_id,
                "message": "저장 완료"
            }

        except Exception as e:
            return {"success": False, "error": f"저장 오류: {str(e)}"}

    def _parse_purchase_date(self, date_str: str) -> datetime | None:
        """purchase_datetime 문자열을 datetime으로 변환"""
        if not date_str:
            return None
        match = re.match(r"(\d{2})-(\d{2})-(\d{2})", date_str)
        if match:
            try:
                return datetime(
                    2000 + int(match.group(1)),
                    int(match.group(2)),
                    int(match.group(3))
                )
            except ValueError:
                return None
        return None

    def _parse_filter_date(self, date_str: str) -> datetime | None:
        """필터 날짜 문자열(YY-MM-DD)을 datetime으로 변환"""
        if not date_str:
            return None
        try:
            if len(date_str) == 8:
                return datetime.strptime(date_str, "%y-%m-%d")
            return datetime.strptime(date_str[:10], "%Y-%m-%d")
        except ValueError:
            return None

    async def get_receipts(
        self,
        limit: int = 20,
        start_date: str = None,
        end_date: str = None,
        store_name: str = None,
        card_name: str = None,
        search: str = None
    ) -> dict:
        """저장된 영수증 목록을 조회합니다."""
        if not self.client:
            return {"success": False, "error": "데이터베이스 연결이 설정되지 않았습니다."}

        try:
            # 기본 쿼리
            query = self.client.table("receipts").select("*")

            # 상점 필터
            if store_name:
                query = query.eq("store_name", store_name)

            # 카드 필터
            if card_name:
                query = query.eq("card_name", card_name)

            result = query.order("created_at", desc=True).limit(limit * 5).execute()
            receipts = result.data

            # 날짜 필터 (클라이언트 측 필터링 - purchase_datetime이 문자열이므로)
            start = self._parse_filter_date(start_date)
            end = self._parse_filter_date(end_date)

            if start or end:
                filtered = []
                for r in receipts:
                    purchase_dt = self._parse_purchase_date(r.get("purchase_datetime", ""))
                    if not purchase_dt:
                        continue
                    if start and purchase_dt < start:
                        continue
                    if end and purchase_dt > end:
                        continue
                    filtered.append(r)
                receipts = filtered

            # 상품명 검색
            if search:
                receipt_ids = [r["id"] for r in receipts]
                if receipt_ids:
                    items_result = self.client.table("items")\
                        .select("receipt_id")\
                        .in_("receipt_id", receipt_ids)\
                        .ilike("name", f"%{search}%")\
                        .execute()

                    matching_ids = set(item["receipt_id"] for item in items_result.data)
                    receipts = [r for r in receipts if r["id"] in matching_ids]

            # purchase_datetime 기준 정렬 (최신순)
            receipts.sort(
                key=lambda r: self._parse_purchase_date(r.get("purchase_datetime", "")) or datetime.min,
                reverse=True
            )

            return {
                "success": True,
                "receipts": receipts[:limit]
            }

        except Exception as e:
            return {"success": False, "error": f"조회 오류: {str(e)}"}

    async def get_receipt_detail(self, receipt_id: int) -> dict:
        """특정 영수증의 상세 정보를 조회합니다."""
        if not self.client:
            return {"success": False, "error": "데이터베이스 연결이 설정되지 않았습니다."}

        try:
            # 영수증 정보 조회
            receipt_result = self.client.table("receipts")\
                .select("*")\
                .eq("id", receipt_id)\
                .execute()

            if not receipt_result.data:
                return {"success": False, "error": "영수증을 찾을 수 없습니다."}

            # 상품 항목 조회
            items_result = self.client.table("items")\
                .select("*")\
                .eq("receipt_id", receipt_id)\
                .execute()

            return {
                "success": True,
                "receipt": receipt_result.data[0],
                "items": items_result.data
            }

        except Exception as e:
            return {"success": False, "error": f"조회 오류: {str(e)}"}

    async def delete_receipt(self, receipt_id: int) -> dict:
        """영수증을 삭제합니다."""
        if not self.client:
            return {"success": False, "error": "데이터베이스 연결이 설정되지 않았습니다."}

        try:
            self.client.table("receipts")\
                .delete()\
                .eq("id", receipt_id)\
                .execute()

            return {"success": True, "message": "삭제 완료"}

        except Exception as e:
            return {"success": False, "error": f"삭제 오류: {str(e)}"}
