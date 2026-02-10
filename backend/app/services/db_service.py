# -*- coding: utf-8 -*-
from supabase import create_client, Client
import os
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

    async def get_receipts(self, limit: int = 20) -> dict:
        """저장된 영수증 목록을 조회합니다."""
        if not self.client:
            return {"success": False, "error": "데이터베이스 연결이 설정되지 않았습니다."}

        try:
            result = self.client.table("receipts")\
                .select("*")\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()

            return {
                "success": True,
                "receipts": result.data
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
