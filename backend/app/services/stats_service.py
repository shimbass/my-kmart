# -*- coding: utf-8 -*-
from supabase import Client
from datetime import datetime, timedelta
from collections import defaultdict
import re


class StatsService:
    def __init__(self, client: Client):
        self.client = client

    def _parse_date(self, date_str: str) -> datetime | None:
        """YY-MM-DD 형식의 날짜 문자열을 datetime으로 변환"""
        if not date_str:
            return None
        try:
            # YY-MM-DD 형식
            if len(date_str) == 8:
                return datetime.strptime(date_str, "%y-%m-%d")
            # YYYY-MM-DD 형식
            return datetime.strptime(date_str[:10], "%Y-%m-%d")
        except ValueError:
            return None

    def _filter_by_date(self, receipts: list, start_date: str, end_date: str) -> list:
        """영수증을 날짜로 필터링"""
        start = self._parse_date(start_date)
        end = self._parse_date(end_date)

        if not start and not end:
            return receipts

        filtered = []
        for r in receipts:
            purchase_dt = r.get("purchase_datetime", "")
            if not purchase_dt:
                continue

            # YY-MM-DD HH:MM 형식에서 날짜 부분 추출
            match = re.match(r"(\d{2})-(\d{2})-(\d{2})", purchase_dt)
            if not match:
                continue

            try:
                receipt_date = datetime(
                    2000 + int(match.group(1)),
                    int(match.group(2)),
                    int(match.group(3))
                )

                if start and receipt_date < start:
                    continue
                if end and receipt_date > end:
                    continue

                filtered.append(r)
            except ValueError:
                continue

        return filtered

    async def get_summary(self, start_date: str = None, end_date: str = None) -> dict:
        """기간별 요약 통계"""
        if not self.client:
            return {"success": False, "error": "데이터베이스 연결 없음"}

        try:
            result = self.client.table("receipts").select("*").execute()
            receipts = self._filter_by_date(result.data, start_date, end_date)

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
            result = self.client.table("receipts").select("*").execute()
            receipts = self._filter_by_date(result.data, start_date, end_date)

            monthly = defaultdict(lambda: {"total_amount": 0, "receipt_count": 0})

            for r in receipts:
                purchase_dt = r.get("purchase_datetime", "")
                match = re.match(r"(\d{2})-(\d{2})-(\d{2})", purchase_dt)
                if match:
                    month_key = f"20{match.group(1)}.{match.group(2)}"
                    monthly[month_key]["total_amount"] += r.get("total_amount", 0)
                    monthly[month_key]["receipt_count"] += 1

            # 정렬
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
            result = self.client.table("receipts").select("*").execute()
            receipts = self._filter_by_date(result.data, start_date, end_date)

            stores = defaultdict(lambda: {"total_amount": 0, "visit_count": 0})

            for r in receipts:
                store = r.get("store_name") or "기타"
                stores[store]["total_amount"] += r.get("total_amount", 0)
                stores[store]["visit_count"] += 1

            # 금액순 정렬
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
            result = self.client.table("receipts").select("*").execute()
            receipts = self._filter_by_date(result.data, start_date, end_date)

            cards = defaultdict(lambda: {"total_amount": 0, "usage_count": 0})

            for r in receipts:
                card = r.get("card_name") or "기타"
                cards[card]["total_amount"] += r.get("total_amount", 0)
                cards[card]["usage_count"] += 1

            # 금액순 정렬
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
            result = self.client.table("receipts").select("*").eq("store_name", store_name).execute()
            receipts = self._filter_by_date(result.data, start_date, end_date)

            cards = defaultdict(lambda: {"total_amount": 0, "usage_count": 0})

            for r in receipts:
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
            # 영수증 조회
            receipts_result = self.client.table("receipts").select("*").execute()
            receipts = self._filter_by_date(receipts_result.data, start_date, end_date)
            receipt_ids = [r["id"] for r in receipts]

            if not receipt_ids:
                return {"success": True, "data": []}

            # 영수증에 해당하는 아이템 조회
            items_result = self.client.table("items").select("*").in_("receipt_id", receipt_ids).execute()

            # 상품별 집계
            item_stats = defaultdict(lambda: {
                "purchase_count": 0,
                "total_amount": 0,
                "purchase_dates": []
            })

            # 영수증 ID -> 날짜 매핑
            receipt_dates = {r["id"]: r.get("purchase_datetime", "") for r in receipts}

            for item in items_result.data:
                name = item.get("name", "").strip()
                if not name:
                    continue

                item_stats[name]["purchase_count"] += item.get("quantity", 1)
                item_stats[name]["total_amount"] += item.get("amount", 0)

                receipt_id = item.get("receipt_id")
                if receipt_id and receipt_id in receipt_dates:
                    date_str = receipt_dates[receipt_id]
                    match = re.match(r"(\d{2})-(\d{2})-(\d{2})", date_str)
                    if match:
                        try:
                            dt = datetime(
                                2000 + int(match.group(1)),
                                int(match.group(2)),
                                int(match.group(3))
                            )
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
                    intervals = [i for i in intervals if i > 0]  # 같은 날 구매 제외
                    if intervals:
                        avg_interval = sum(intervals) // len(intervals)

                data.append({
                    "name": name,
                    "purchase_count": stats["purchase_count"],
                    "total_amount": stats["total_amount"],
                    "avg_interval_days": avg_interval
                })

            # 구매 횟수순 정렬
            data.sort(key=lambda x: x["purchase_count"], reverse=True)

            return {"success": True, "data": data[:limit]}
        except Exception as e:
            return {"success": False, "error": str(e)}
