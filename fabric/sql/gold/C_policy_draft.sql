-- Source: docs/source/Gold_Warehouse_Huong_dan_chi_tiet (3).docx
-- BEGIN C
-- Run once. Replace DRAFT_V1 with a new ID for revisions.
-- Labels and flags below are proposals for AdventureWorks, NOT an approval.
IF EXISTS (SELECT 1 FROM ref.policy WHERE policy_id='DRAFT_V1')
 THROW 51000,'Policy already exists: use a new policy ID',1;
INSERT INTO ref.policy VALUES
 ('DRAFT_V1',0,NULL,NULL,'USD','USD','TO_PER_FROM','QUARTER',24,'1.0');
INSERT INTO ref.order_status VALUES
 ('DRAFT_V1',1,'In process',0),('DRAFT_V1',2,'Approved',0),
 ('DRAFT_V1',3,'Backordered',0),('DRAFT_V1',4,'Rejected',0),
 ('DRAFT_V1',5,'Shipped',1),('DRAFT_V1',6,'Cancelled',0);
-- Confirm labels/flags, base currency of source amounts, rate units,
-- quarterly quota meaning and acceptable stock age before approval.
-- Then set approved=1, approved_by to your real reviewer, approved_at UTC.
-- Never change policy rows referenced by a published run. Create a new ID.

-- END C
