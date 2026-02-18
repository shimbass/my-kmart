-- discounts 테이블: 영수증의 할인 항목을 별도 관리
CREATE TABLE IF NOT EXISTS discounts (
    id          BIGSERIAL PRIMARY KEY,
    receipt_id  BIGINT NOT NULL REFERENCES receipts(id) ON DELETE CASCADE,
    name        TEXT    NOT NULL DEFAULT '',
    amount      INTEGER NOT NULL DEFAULT 0,   -- 양수로 저장 (할인된 금액)
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_discounts_receipt_id ON discounts(receipt_id);
