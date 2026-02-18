-- ================================================================
-- DB 최적화 마이그레이션
-- ================================================================

-- 1. 누락 인덱스 추가
-- ----------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_items_receipt_id
    ON items(receipt_id);

CREATE INDEX IF NOT EXISTS idx_discounts_item_id
    ON discounts(item_id);

CREATE INDEX IF NOT EXISTS idx_receipts_store_name
    ON receipts(store_name);

CREATE INDEX IF NOT EXISTS idx_receipts_card_name
    ON receipts(card_name);

-- 2. purchase_date (TIMESTAMPTZ) 컬럼 추가
--    purchase_datetime(TEXT "YY-MM-DD HH:MM")을 변환해 저장
-- ----------------------------------------------------------------
ALTER TABLE receipts
    ADD COLUMN IF NOT EXISTS purchase_date TIMESTAMPTZ;

UPDATE receipts
SET purchase_date = TO_TIMESTAMP(
        '20' || purchase_datetime,
        'YYYY-MM-DD HH24:MI'
    )
WHERE purchase_datetime IS NOT NULL
  AND purchase_datetime != ''
  AND purchase_datetime ~ '^\d{2}-\d{2}-\d{2}';

CREATE INDEX IF NOT EXISTS idx_receipts_purchase_date
    ON receipts(purchase_date);
