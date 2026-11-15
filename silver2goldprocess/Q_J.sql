-- BLOCK J: POLICY APPROVAL

DECLARE @policy varchar(40) = 'DRAFT_V1';

-- Thay bằng tên người thực sự chịu trách nhiệm duyệt
DECLARE @reviewer varchar(200) = N'Tên người phê duyệt';

-- Đặt bằng 1 sau khi đã xác nhận các quy ước nghiệp vụ
DECLARE @currency_confirmed bit = 1;
DECLARE @status_confirmed bit = 1;
DECLARE @quota_confirmed bit = 1;
DECLARE @stock_confirmed bit = 1;

IF @reviewer = 'REPLACE_WITH_REVIEWER'
   OR @reviewer IS NULL
   OR @currency_confirmed <> 1
   OR @status_confirmed <> 1
   OR @quota_confirmed <> 1
   OR @stock_confirmed <> 1
    THROW 51000, 'Business approval fields incomplete', 1;

IF (
    SELECT COUNT_BIG(*)
    FROM ref.policy
    WHERE policy_id = @policy
) <> 1
    THROW 51000, 'Unknown or duplicate policy', 1;

IF EXISTS (
    SELECT 1
    FROM ops.publication
    WHERE policy_id = @policy
)
    THROW 51000, 'Published policy immutable', 1;

UPDATE ref.policy
SET
    approved = 1,
    approved_by = @reviewer,
    approved_at = SYSUTCDATETIME()
WHERE policy_id = @policy;

-- Kiểm tra kết quả phê duyệt
SELECT
    policy_id,
    approved,
    approved_by,
    approved_at,
    source_currency,
    report_currency,
    fx_units,
    quota_grain,
    stock_max_age_hours
FROM ref.policy
WHERE policy_id = @policy;
GO