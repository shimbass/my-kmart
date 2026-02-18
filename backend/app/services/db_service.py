# -*- coding: utf-8 -*-
from supabase import create_client, Client
import os
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# 할인 항목 판별 키워드
_DISCOUNT_KEYWORDS = ["할인", "DC", "DISCOUNT", "쿠폰", "COUPON"]


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

    # ── 날짜 변환 헬퍼 ───────────────────────────────────────────────────────
    def _to_purchase_date(self, dt_str: str) -> str | None:
        """YY-MM-DD HH:MM 형식을 ISO 8601 문자열로 변환 (purchase_date 컬럼 저장용)"""
        if not dt_str:
            return None
        match = re.match(r"(\d{2})-(\d{2})-(\d{2})\s*(\d{2}):(\d{2})", dt_str)
        if match:
            try:
                dt = datetime(
                    2000 + int(match.group(1)),
                    int(match.group(2)),
                    int(match.group(3)),
                    int(match.group(4)),
                    int(match.group(5)),
                )
                return dt.isoformat()
            except ValueError:
                return None
        return None

    def _parse_filter_date(self, date_str: str) -> datetime | None:
        """필터 날짜 문자열(YY-MM-DD 또는 YYYY-MM-DD)을 datetime으로 변환"""
        if not date_str:
            return None
        try:
            if len(date_str) == 8:
                return datetime.strptime(date_str, "%y-%m-%d")
            return datetime.strptime(date_str[:10], "%Y-%m-%d")
        except ValueError:
            return None

    def _parse_purchase_date(self, date_str: str) -> datetime | None:
        """purchase_datetime 문자열(YY-MM-DD HH:MM)을 datetime으로 변환 (레거시용)"""
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

    # ── 할인 항목 판별 ────────────────────────────────────────────────────────
    def _is_discount_item(self, item: dict) -> bool:
        """상품 항목이 할인 항목인지 판별합니다."""
        amount = item.get("amount", 0) or 0
        if amount < 0:
            return True
        name = str(item.get("name", "")).upper()
        return any(kw in name for kw in _DISCOUNT_KEYWORDS)

    # ── 영수증 저장 ───────────────────────────────────────────────────────────
    async def save_receipt(self, data: dict) -> dict:
        """영수증 인식 결과를 데이터베이스에 저장합니다.
        할인 항목은 discounts 테이블에 별도 저장합니다.
        """
        if not self.client:
            return {"success": False, "error": "데이터베이스 연결이 설정되지 않았습니다."}

        try:
            all_items = data.get("items", [])

            regular_items  = [i for i in all_items if not self._is_discount_item(i)]
            discount_items = [i for i in all_items if self._is_discount_item(i)]

            total_amount = sum(i.get("amount", 0) for i in all_items)
            purchase_dt  = data.get("purchaseDateTime")

            receipt_data = {
                "store_name":        data.get("storeName"),
                "card_name":         data.get("cardName"),
                "purchase_datetime": purchase_dt,
                "purchase_date":     self._to_purchase_date(purchase_dt),  # ★ TIMESTAMPTZ
                "raw_text":          data.get("rawText", ""),
                "total_amount":      total_amount,
            }
            receipt_result = self.client.table("receipts").insert(receipt_data).execute()
            if not receipt_result.data:
                return {"success": False, "error": "영수증 저장 실패"}

            receipt_id = receipt_result.data[0]["id"]

            if regular_items:
                items_data = []
                for idx, item in enumerate(regular_items, start=1):
                    no = item.get("no")
                    if not no or not str(no).strip():
                        no = f"{idx:03d}"
                    items_data.append({
                        "receipt_id": receipt_id,
                        "no":         no,
                        "name":       item.get("name", ""),
                        "barcode":    item.get("barcode"),
                        "unit_price": item.get("unitPrice", 0),
                        "quantity":   item.get("quantity", 0),
                        "amount":     item.get("amount", 0),
                    })
                self.client.table("items").insert(items_data).execute()

            if discount_items:
                discounts_data = [
                    {
                        "receipt_id": receipt_id,
                        "name":       item.get("name", "할인"),
                        "amount":     abs(item.get("amount", 0)),
                    }
                    for item in discount_items
                ]
                self.client.table("discounts").insert(discounts_data).execute()

            return {
                "success":        True,
                "receipt_id":     receipt_id,
                "discount_count": len(discount_items),
                "message":        "저장 완료",
            }

        except Exception as e:
            return {"success": False, "error": f"저장 오류: {str(e)}"}

    # ── 영수증 목록 조회 ─────────────────────────────────────────────────────
    async def get_receipts(
        self,
        limit: int = 20,
        start_date: str = None,
        end_date: str = None,
        store_name: str = None,
        card_name: str = None,
        search: str = None
    ) -> dict:
        """저장된 영수증 목록을 조회합니다.
        purchase_date(TIMESTAMPTZ)로 DB 레벨에서 날짜 필터링합니다.
        """
        if not self.client:
            return {"success": False, "error": "데이터베이스 연결이 설정되지 않았습니다."}

        try:
            query = self.client.table("receipts").select("*")

            if store_name:
                query = query.eq("store_name", store_name)
            if card_name:
                query = query.eq("card_name", card_name)

            # ★ DB 레벨 날짜 필터링 (Python 필터링 제거)
            start = self._parse_filter_date(start_date)
            end   = self._parse_filter_date(end_date)
            if start:
                query = query.gte("purchase_date", start.isoformat())
            if end:
                query = query.lt("purchase_date", (end + timedelta(days=1)).isoformat())

            # ★ DB 레벨 정렬 + 정확한 limit (limit * 5 제거)
            result = query.order("purchase_date", desc=True).limit(limit).execute()
            receipts = result.data

            # 상품명 검색
            if search and receipts:
                receipt_ids = [r["id"] for r in receipts]
                items_result = self.client.table("items")\
                    .select("receipt_id")\
                    .in_("receipt_id", receipt_ids)\
                    .ilike("name", f"%{search}%")\
                    .execute()
                matching_ids = set(item["receipt_id"] for item in items_result.data)
                receipts = [r for r in receipts if r["id"] in matching_ids]

            return {"success": True, "receipts": receipts}

        except Exception as e:
            return {"success": False, "error": f"조회 오류: {str(e)}"}

    # ── 영수증 상세 조회 ─────────────────────────────────────────────────────
    async def get_receipt_detail(self, receipt_id: int) -> dict:
        """특정 영수증의 상세 정보를 조회합니다. (할인 항목 포함)"""
        if not self.client:
            return {"success": False, "error": "데이터베이스 연결이 설정되지 않았습니다."}

        try:
            receipt_result = self.client.table("receipts")\
                .select("*").eq("id", receipt_id).execute()

            if not receipt_result.data:
                return {"success": False, "error": "영수증을 찾을 수 없습니다."}

            items_result = self.client.table("items")\
                .select("*").eq("receipt_id", receipt_id).execute()

            discounts_result = self.client.table("discounts")\
                .select("*").eq("receipt_id", receipt_id).execute()

            return {
                "success":   True,
                "receipt":   receipt_result.data[0],
                "items":     items_result.data,
                "discounts": discounts_result.data,
            }

        except Exception as e:
            return {"success": False, "error": f"조회 오류: {str(e)}"}

    # ── 영수증 삭제 ───────────────────────────────────────────────────────────
    async def delete_receipt(self, receipt_id: int) -> dict:
        """영수증을 삭제합니다."""
        if not self.client:
            return {"success": False, "error": "데이터베이스 연결이 설정되지 않았습니다."}

        try:
            self.client.table("receipts").delete().eq("id", receipt_id).execute()
            return {"success": True, "message": "삭제 완료"}

        except Exception as e:
            return {"success": False, "error": f"삭제 오류: {str(e)}"}

    # ── 할인 항목 직접 추가 ──────────────────────────────────────────────────
    async def add_discount(self, receipt_id: int, name: str, amount: int, item_id: int = None) -> dict:
        """특정 영수증에 할인 항목을 직접 추가합니다."""
        if not self.client:
            return {"success": False, "error": "데이터베이스 연결이 설정되지 않았습니다."}
        try:
            row = {
                "receipt_id": receipt_id,
                "name":       name,
                "amount":     abs(amount),
            }
            if item_id is not None:
                row["item_id"] = item_id
            result = self.client.table("discounts").insert(row).execute()
            return {"success": True, "discount": result.data[0]}
        except Exception as e:
            return {"success": False, "error": f"저장 오류: {str(e)}"}

    # ── 결제수단 감지 ────────────────────────────────────────────────────────
    def _detect_payment_method(self, raw_text: str) -> str | None:
        """raw_text에서 결제수단을 감지합니다."""
        if not raw_text:
            return None

        text_lower = raw_text.lower()

        if "배민1" in raw_text or "배민 1" in raw_text or "baemin1" in text_lower or "baemin 1" in text_lower:
            return "배민1(one)"
        if "배달의민족" in raw_text or "배민" in raw_text or "baemin" in text_lower:
            return "배달의민족"
        if "요기요" in raw_text or "yogiyo" in text_lower:
            return "요기요"
        if "쿠팡이츠" in raw_text or "쿠팡 이츠" in raw_text or "coupang eats" in text_lower:
            return "쿠팡이츠"
        if "땡겨요" in raw_text:
            return "땡겨요"
        if "카카오페이" in raw_text or "kakaopay" in text_lower or "kakao pay" in text_lower:
            return "카카오페이"
        if "네이버페이" in raw_text or "naverpay" in text_lower or "naver pay" in text_lower:
            return "네이버페이"
        if "삼성페이" in raw_text or "samsung pay" in text_lower:
            return "삼성페이"
        if "애플페이" in raw_text or "apple pay" in text_lower:
            return "애플페이"
        if "토스페이" in raw_text or "toss pay" in text_lower:
            return "토스페이"
        if "토스" in raw_text or "toss" in text_lower:
            return "토스"
        if "현금" in raw_text:
            return "현금"

        return None

    # ── Admin: 데이터 정리 ───────────────────────────────────────────────────
    async def cleanup_data(self) -> dict:
        """기존 데이터 유효성 검사 및 정리."""
        if not self.client:
            return {"success": False, "error": "데이터베이스 연결이 설정되지 않았습니다."}

        no_fixed = 0
        card_fixed = 0
        details = []

        try:
            all_items_result = self.client.table("items").select("*").order("id").execute()

            receipt_items: dict[int, list] = {}
            for item in all_items_result.data:
                rid = item["receipt_id"]
                receipt_items.setdefault(rid, []).append(item)

            for rid, items in receipt_items.items():
                for idx, item in enumerate(items, start=1):
                    no = item.get("no")
                    if not no or not str(no).strip():
                        new_no = f"{idx:03d}"
                        self.client.table("items")\
                            .update({"no": new_no}).eq("id", item["id"]).execute()
                        no_fixed += 1
                        details.append(f"[no] item id={item['id']} receipt_id={rid} → {new_no}")

            receipts_result = self.client.table("receipts").select("*").execute()

            for receipt in receipts_result.data:
                card_name = receipt.get("card_name")
                if not card_name or not str(card_name).strip():
                    detected = self._detect_payment_method(receipt.get("raw_text", ""))
                    if detected:
                        self.client.table("receipts")\
                            .update({"card_name": detected}).eq("id", receipt["id"]).execute()
                        card_fixed += 1
                        details.append(
                            f"[card] receipt id={receipt['id']} "
                            f"({receipt.get('store_name', '?')}) → {detected}"
                        )

            return {
                "success":         True,
                "no_fixed":        no_fixed,
                "card_name_fixed": card_fixed,
                "details":         details,
                "message":         f"정리 완료 — no {no_fixed}건, 결제수단 {card_fixed}건 수정",
            }

        except Exception as e:
            return {"success": False, "error": f"정리 오류: {str(e)}"}

    # ── Admin: 할인 항목 마이그레이션 ────────────────────────────────────────
    async def migrate_discounts(self) -> dict:
        """기존 items 테이블에서 할인 항목을 찾아 discounts 테이블로 이전합니다."""
        if not self.client:
            return {"success": False, "error": "데이터베이스 연결이 설정되지 않았습니다."}

        migrated = 0
        skipped  = 0
        details  = []

        try:
            all_items = self.client.table("items").select("*").order("id").execute().data

            for item in all_items:
                if not self._is_discount_item(item):
                    skipped += 1
                    continue

                exists = self.client.table("discounts")\
                    .select("id")\
                    .eq("receipt_id", item["receipt_id"])\
                    .eq("name", item.get("name", ""))\
                    .execute()

                if exists.data:
                    details.append(f"[skip] item id={item['id']} 이미 존재")
                    continue

                self.client.table("discounts").insert({
                    "receipt_id": item["receipt_id"],
                    "name":       item.get("name", "할인"),
                    "amount":     abs(item.get("amount", 0)),
                }).execute()

                self.client.table("items").delete().eq("id", item["id"]).execute()

                migrated += 1
                details.append(
                    f"[이전] item id={item['id']} receipt_id={item['receipt_id']} "
                    f"'{item.get('name')}' ₩{abs(item.get('amount', 0)):,}"
                )

            return {
                "success":  True,
                "migrated": migrated,
                "skipped":  skipped,
                "details":  details,
                "message":  f"마이그레이션 완료 — 할인 항목 {migrated}건 이전, 일반 상품 {skipped}건 유지",
            }

        except Exception as e:
            return {"success": False, "error": f"마이그레이션 오류: {str(e)}"}
