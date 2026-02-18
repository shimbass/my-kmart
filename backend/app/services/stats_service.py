# -*- coding: utf-8 -*-
from supabase import Client
from datetime import datetime, timedelta
from collections import defaultdict


class StatsService:
    def __init__(self, client: Client):
        self.client = client

    def _parse_date(self, date_str: str) -> datetime | None:
        """YY-MM-DD 또는 YYYY-MM-DD 형식의 날짜 문자열을 datetime으로 변환"""
        if not date_str:
            return None
        try:
            if len(date_str) == 8:
                return datetime.strptime(date_str, "%y-%m-%d")
            return datetime.strptime(date_str[:10], "%Y-%m-%d")
        except ValueError:
            return None

    def _apply_date_filter(self, query, start_date: str, end_date: str):
        """purchase_date 컬럼에 DB 레벨 날짜 필터 적용"""
        start = self._parse_date(start_date)
        end = self._parse_date(end_date)
        if start:
            query = query.gte("purchase_date", start.isoformat())
        if end:
            query = query.lt("purchase_date", (end + timedelta(days=1)).isoformat())
        return query

    async def get_summary(self, start_date: str = None, end_date: str = None) -> dict:
        """기간별 요약 통계"""
        if not self.client:
            return {"success": False, "error": "데이터베이스 연결 없음"}

        try:
            query = self.client.table("receipts").select("total_amount")
            query = self._apply_date_filter(query, start_date, end_date)
            result = query.execute()
            receipts = result.data

            total_amount = sum(r.get("total_amount", 0) for r in receipts)
            receipt_count = len(receipts)
            avg_amount = total_amount // receipt_count if receipt_count > 0 else 0

            return {
                "success": True,
                "data": {
                    "total_amount": total_amount,
                    "receipt_count": receipt_count,
                    "avg_amount": avg_amount
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_monthly_stats(self, start_date: str = None, end_date: str = None) -> dict:
        """월별 지출 통계"""
        if not self.client:
            return {"success": False, "error": "데이터베이스 연결 없음"}

        try:
            query = self.client.table("receipts").select("purchase_date, total_amount")
            query = self._apply_date_filter(query, start_date, end_date)
            result = query.execute()

            monthly = defaultdict(lambda: {"total_amount": 0, "receipt_count": 0})

            for r in result.data:
                pd = r.get("purchase_date")
                if not pd:
                    continue
                # purchase_date는 ISO 8601 (2026-02-14T...)
                month_key = pd[:7].replace("-", ".")  # "2026.02"
                monthly[month_key]["total_amount"] += r.get("total_amount", 0)
                monthly[month_key]["receipt_count"] += 1

            data = [
                {"month": k, "total_amount": v["total_amount"], "receipt_count": v["receipt_count"]}
                for k, v in sorted(monthly.items())
            ]

            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_store_stats(self, start_date: str = None, end_date: str = None) -> dict:
        """상점별 지출 통계"""
        if not self.client:
            return {"success": False, "error": "데이터베이스 연결 없음"}

        try:
            query = self.client.table("receipts").select("store_name, total_amount")
            query = self._apply_date_filter(query, start_date, end_date)
            result = query.execute()

            stores = defaultdict(lambda: {"total_amount": 0, "visit_count": 0})

            for r in result.data:
                store = r.get("store_name") or "기타"
                stores[store]["total_amount"] += r.get("total_amount", 0)
                stores[store]["visit_count"] += 1

            data = [
                {"store_name": k, "total_amount": v["total_amount"], "visit_count": v["visit_count"]}
                for k, v in sorted(stores.items(), key=lambda x: x[1]["total_amount"], reverse=True)
            ]

            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_card_stats(self, start_date: str = None, end_date: str = None) -> dict:
        """카드별 지출 통계"""
        if not self.client:
            return {"success": False, "error": "데이터베이스 연결 없음"}

        try:
            query = self.client.table("receipts").select("card_name, total_amount")
            query = self._apply_date_filter(query, start_date, end_date)
            result = query.execute()

            cards = defaultdict(lambda: {"total_amount": 0, "usage_count": 0})

            for r in result.data:
                card = r.get("card_name") or "기타"
                cards[card]["total_amount"] += r.get("total_amount", 0)
                cards[card]["usage_count"] += 1

            data = [
                {"card_name": k, "total_amount": v["total_amount"], "usage_count": v["usage_count"]}
                for k, v in sorted(cards.items(), key=lambda x: x[1]["total_amount"], reverse=True)
            ]

            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_store_card_stats(self, store_name: str, start_date: str = None, end_date: str = None) -> dict:
        """특정 상점의 카드별 지출 통계"""
        if not self.client:
            return {"success": False, "error": "데이터베이스 연결 없음"}

        try:
            query = self.client.table("receipts").select("card_name, total_amount").eq("store_name", store_name)
            query = self._apply_date_filter(query, start_date, end_date)
            result = query.execute()

            cards = defaultdict(lambda: {"total_amount": 0, "usage_count": 0})

            for r in result.data:
                card = r.get("card_name") or "기타"
                cards[card]["total_amount"] += r.get("total_amount", 0)
                cards[card]["usage_count"] += 1

            data = [
                {"card_name": k, "total_amount": v["total_amount"], "usage_count": v["usage_count"]}
                for k, v in sorted(cards.items(), key=lambda x: x[1]["total_amount"], reverse=True)
            ]

            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_frequent_items(self, start_date: str = None, end_date: str = None, limit: int = 10) -> dict:
        """자주 구매하는 상품 통계"""
        if not self.client:
            return {"success": False, "error": "데이터베이스 연결 없음"}

        try:
            # 날짜 필터로 영수증 ID + purchase_date만 조회
            query = self.client.table("receipts").select("id, purchase_date")
            query = self._apply_date_filter(query, start_date, end_date)
            receipts_result = query.execute()

            receipt_ids = [r["id"] for r in receipts_result.data]
            if not receipt_ids:
                return {"success": True, "data": []}

            # 영수증 ID → purchase_date 매핑
            receipt_dates = {
                r["id"]: r.get("purchase_date")
                for r in receipts_result.data
            }

            # 해당 영수증의 아이템 조회 (필요한 컬럼만)
            items_result = self.client.table("items").select(
                "name, quantity, amount, receipt_id"
            ).in_("receipt_id", receipt_ids).execute()

            # 상품별 집계
            item_stats = defaultdict(lambda: {
                "purchase_count": 0,
                "total_amount": 0,
                "purchase_dates": []
            })

            for item in items_result.data:
                name = item.get("name", "").strip()
                if not name:
                    continue

                item_stats[name]["purchase_count"] += item.get("quantity", 1)
                item_stats[name]["total_amount"] += item.get("amount", 0)

                receipt_id = item.get("receipt_id")
                pd = receipt_dates.get(receipt_id)
                if pd:
                    try:
                        dt = datetime.fromisoformat(pd[:19])  # TZ 부분 제거
                        item_stats[name]["purchase_dates"].append(dt)
                    except ValueError:
                        pass

            # 평균 구매 주기 계산
            data = []
            for name, stats in item_stats.items():
                dates = sorted(stats["purchase_dates"])
                avg_interval = None

                if len(dates) >= 2:
                    intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
                    intervals = [i for i in intervals if i > 0]
                    if intervals:
                        avg_interval = sum(intervals) // len(intervals)

                data.append({
                    "name": name,
                    "purchase_count": stats["purchase_count"],
                    "total_amount": stats["total_amount"],
                    "avg_interval_days": avg_interval
                })

            data.sort(key=lambda x: x["purchase_count"], reverse=True)

            return {"success": True, "data": data[:limit]}
        except Exception as e:
            return {"success": False, "error": str(e)}
