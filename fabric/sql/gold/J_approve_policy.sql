-- Source: docs/source/Gold_Warehouse_Huong_dan_chi_tiet (3).docx
-- BEGIN J
-- Configure after confirming business semantics. NULL defaults deliberately block.
DECLARE @policy varchar(40)='DRAFT_V1';
DECLARE @reviewer varchar(200)=NULL; -- replace with real responsible person
DECLARE @currency_confirmed bit=0;  -- change only after verification
DECLARE @status_confirmed bit=0;
DECLARE @quota_confirmed bit=0;
IF @reviewer IS NULL OR @currency_confirmed<>1 OR @status_confirmed<>1 OR @quota_confirmed<>1
 THROW 51000,'Business approval fields incomplete',1;
IF (SELECT COUNT_BIG(*) FROM ref.policy WHERE policy_id=@policy)<>1
 THROW 51000,'Unknown or duplicate policy',1;
IF EXISTS(SELECT 1 FROM ops.publication WHERE policy_id=@policy)
 THROW 51000,'Published policy immutable: create new policy',1;
UPDATE ref.policy SET approved=1,approved_by=@reviewer,approved_at=SYSUTCDATETIME()
WHERE policy_id=@policy;

-- END J
