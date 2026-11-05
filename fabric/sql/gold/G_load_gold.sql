-- Source: docs/source/Gold_Warehouse_Huong_dan_chi_tiet (3).docx
-- BEGIN G
CREATE OR ALTER PROCEDURE ops.usp_load_gold
 @run_id varchar(36),
 @money_tolerance decimal(28,6),
 @source_run_id varchar(36),@policy_id varchar(40),
 @snapshot_date date=NULL
AS
BEGIN
 SET NOCOUNT ON;
 IF @run_id IS NULL OR LEN(@run_id)<>36
   THROW 51000,'Run ID can 36 ky tu',1;
 IF @money_tolerance IS NULL OR @money_tolerance<0
   THROW 51000,'Can tolerance da doi soat',1;
 IF EXISTS (SELECT 1 FROM ops.gold_run WHERE run_id=@run_id)
   THROW 51000,'Run ID da dung; tao ID moi cho lan thu lai',1;
 DECLARE @loaded_at datetime2(6)=SYSUTCDATETIME();
 INSERT INTO ops.gold_run VALUES
 (@run_id,@loaded_at,NULL,'RUNNING',NULL);
 BEGIN TRY
 BEGIN TRANSACTION;
IF (SELECT COUNT_BIG(*) FROM ref.policy WHERE policy_id=@policy_id AND approved=1 AND approved_by IS NOT NULL AND approved_at IS NOT NULL)<>1
 THROW 51000,'Approved unique policy required',1;

IF (SELECT COUNT_BIG(*) FROM ops.source_manifest WHERE source_run_id=@source_run_id)<>17
 THROW 51000,'Silver manifest must contain all 17 sources',1;

IF EXISTS(SELECT table_name FROM ops.source_manifest WHERE source_run_id=@source_run_id GROUP BY table_name HAVING COUNT_BIG(*)<>1)
 THROW 51000,'Duplicate manifest table',1;

IF NOT EXISTS(SELECT 1 FROM ops.source_manifest WHERE source_run_id=@source_run_id AND table_name='int_product' AND row_count=(SELECT COUNT_BIG(*) FROM src.int_product))
 THROW 51000,'Manifest count mismatch int_product',1;

IF NOT EXISTS(SELECT 1 FROM ops.source_manifest WHERE source_run_id=@source_run_id AND table_name='int_customer' AND row_count=(SELECT COUNT_BIG(*) FROM src.int_customer))
 THROW 51000,'Manifest count mismatch int_customer',1;

IF NOT EXISTS(SELECT 1 FROM ops.source_manifest WHERE source_run_id=@source_run_id AND table_name='int_sales_orders' AND row_count=(SELECT COUNT_BIG(*) FROM src.int_sales_orders))
 THROW 51000,'Manifest count mismatch int_sales_orders',1;

IF NOT EXISTS(SELECT 1 FROM ops.source_manifest WHERE source_run_id=@source_run_id AND table_name='int_sales_order_lines' AND row_count=(SELECT COUNT_BIG(*) FROM src.int_sales_order_lines))
 THROW 51000,'Manifest count mismatch int_sales_order_lines',1;

IF NOT EXISTS(SELECT 1 FROM ops.source_manifest WHERE source_run_id=@source_run_id AND table_name='int_product_price_history' AND row_count=(SELECT COUNT_BIG(*) FROM src.int_product_price_history))
 THROW 51000,'Manifest count mismatch int_product_price_history',1;

IF NOT EXISTS(SELECT 1 FROM ops.source_manifest WHERE source_run_id=@source_run_id AND table_name='int_product_cost_history' AND row_count=(SELECT COUNT_BIG(*) FROM src.int_product_cost_history))
 THROW 51000,'Manifest count mismatch int_product_cost_history',1;

IF NOT EXISTS(SELECT 1 FROM ops.source_manifest WHERE source_run_id=@source_run_id AND table_name='int_special_offers' AND row_count=(SELECT COUNT_BIG(*) FROM src.int_special_offers))
 THROW 51000,'Manifest count mismatch int_special_offers',1;

IF NOT EXISTS(SELECT 1 FROM ops.source_manifest WHERE source_run_id=@source_run_id AND table_name='int_special_offer_products' AND row_count=(SELECT COUNT_BIG(*) FROM src.int_special_offer_products))
 THROW 51000,'Manifest count mismatch int_special_offer_products',1;

IF NOT EXISTS(SELECT 1 FROM ops.source_manifest WHERE source_run_id=@source_run_id AND table_name='int_inventory_by_location' AND row_count=(SELECT COUNT_BIG(*) FROM src.int_inventory_by_location))
 THROW 51000,'Manifest count mismatch int_inventory_by_location',1;

IF NOT EXISTS(SELECT 1 FROM ops.source_manifest WHERE source_run_id=@source_run_id AND table_name='int_inventory_by_product' AND row_count=(SELECT COUNT_BIG(*) FROM src.int_inventory_by_product))
 THROW 51000,'Manifest count mismatch int_inventory_by_product',1;

IF NOT EXISTS(SELECT 1 FROM ops.source_manifest WHERE source_run_id=@source_run_id AND table_name='int_product_stock_status' AND row_count=(SELECT COUNT_BIG(*) FROM src.int_product_stock_status))
 THROW 51000,'Manifest count mismatch int_product_stock_status',1;

IF NOT EXISTS(SELECT 1 FROM ops.source_manifest WHERE source_run_id=@source_run_id AND table_name='int_geography' AND row_count=(SELECT COUNT_BIG(*) FROM src.int_geography))
 THROW 51000,'Manifest count mismatch int_geography',1;

IF NOT EXISTS(SELECT 1 FROM ops.source_manifest WHERE source_run_id=@source_run_id AND table_name='int_sales_person' AND row_count=(SELECT COUNT_BIG(*) FROM src.int_sales_person))
 THROW 51000,'Manifest count mismatch int_sales_person',1;

IF NOT EXISTS(SELECT 1 FROM ops.source_manifest WHERE source_run_id=@source_run_id AND table_name='int_sales_person_quota_history' AND row_count=(SELECT COUNT_BIG(*) FROM src.int_sales_person_quota_history))
 THROW 51000,'Manifest count mismatch int_sales_person_quota_history',1;

IF NOT EXISTS(SELECT 1 FROM ops.source_manifest WHERE source_run_id=@source_run_id AND table_name='int_sales_territory_history' AND row_count=(SELECT COUNT_BIG(*) FROM src.int_sales_territory_history))
 THROW 51000,'Manifest count mismatch int_sales_territory_history',1;

IF NOT EXISTS(SELECT 1 FROM ops.source_manifest WHERE source_run_id=@source_run_id AND table_name='int_currency' AND row_count=(SELECT COUNT_BIG(*) FROM src.int_currency))
 THROW 51000,'Manifest count mismatch int_currency',1;

IF NOT EXISTS(SELECT 1 FROM ops.source_manifest WHERE source_run_id=@source_run_id AND table_name='int_currency_rate' AND row_count=(SELECT COUNT_BIG(*) FROM src.int_currency_rate))
 THROW 51000,'Manifest count mismatch int_currency_rate',1;

IF EXISTS(SELECT 1 FROM ref.policy WHERE policy_id=@policy_id AND (fx_units<>'TO_PER_FROM' OR quota_grain<>'QUARTER' OR stock_max_age_hours<=0))
 THROW 51000,'Unsupported policy interpretation',1;

IF EXISTS(SELECT status_code FROM ref.order_status WHERE policy_id=@policy_id GROUP BY status_code HAVING COUNT_BIG(*)<>1)
 THROW 51000,'Duplicate status policy',1;

IF EXISTS(SELECT 1 FROM src.int_sales_orders h LEFT JOIN ref.order_status s ON s.policy_id=@policy_id AND h.status=s.status_code WHERE s.status_code IS NULL)
 THROW 51000,'Unmapped order status',1;

IF EXISTS(SELECT sales_person_id,DATEFROMPARTS(YEAR(quota_date),3*((MONTH(quota_date)-1)/3)+1,1) q FROM src.int_sales_person_quota_history GROUP BY sales_person_id,DATEFROMPARTS(YEAR(quota_date),3*((MONTH(quota_date)-1)/3)+1,1) HAVING COUNT_BIG(*)>1)
 THROW 51000,'Multiple quotas per quarter require revision rule',1;
IF NOT EXISTS (SELECT 1 FROM src.int_sales_orders)
  THROW 51000, 'DQ_EMPTY: Header rong; kiem tra nguon', 1;

IF EXISTS (SELECT 1 FROM src.int_sales_order_lines l
 LEFT JOIN src.int_sales_orders h
 ON l.sales_order_id=h.sales_order_id
 WHERE h.sales_order_id IS NULL)
  THROW 51000, 'DQ_FK: Detail khong co Header', 1;

IF EXISTS (SELECT location_id FROM src.int_inventory_by_location
 GROUP BY location_id HAVING COUNT(DISTINCT location_name)>1)
  THROW 51000, 'DQ_LOCATION: Mot ID nhieu ten', 1;

IF EXISTS (SELECT 1 FROM src.int_product_cost_history
 WHERE product_id IS NULL OR start_date IS NULL
 OR standard_cost IS NULL OR standard_cost < 0
 OR end_date < start_date)
  THROW 51000, 'DQ_COST: Khoa ngay hoac cost khong hop le', 1;

IF EXISTS (SELECT product_id FROM src.int_product
 GROUP BY product_id HAVING COUNT_BIG(*)>1)
  THROW 51000, 'DQ_DUP: int_product', 1;

IF EXISTS (SELECT 1 FROM src.int_product
 WHERE product_id IS NULL)
  THROW 51000, 'DQ_NULL: int_product', 1;

IF EXISTS (SELECT customer_id FROM src.int_customer
 GROUP BY customer_id HAVING COUNT_BIG(*)>1)
  THROW 51000, 'DQ_DUP: int_customer', 1;

IF EXISTS (SELECT 1 FROM src.int_customer
 WHERE customer_id IS NULL)
  THROW 51000, 'DQ_NULL: int_customer', 1;

IF EXISTS (SELECT address_id FROM src.int_geography
 GROUP BY address_id HAVING COUNT_BIG(*)>1)
  THROW 51000, 'DQ_DUP: int_geography', 1;

IF EXISTS (SELECT 1 FROM src.int_geography
 WHERE address_id IS NULL)
  THROW 51000, 'DQ_NULL: int_geography', 1;

IF EXISTS (SELECT sales_person_id FROM src.int_sales_person
 GROUP BY sales_person_id HAVING COUNT_BIG(*)>1)
  THROW 51000, 'DQ_DUP: int_sales_person', 1;

IF EXISTS (SELECT 1 FROM src.int_sales_person
 WHERE sales_person_id IS NULL)
  THROW 51000, 'DQ_NULL: int_sales_person', 1;

IF EXISTS (SELECT special_offer_id FROM src.int_special_offers
 GROUP BY special_offer_id HAVING COUNT_BIG(*)>1)
  THROW 51000, 'DQ_DUP: int_special_offers', 1;

IF EXISTS (SELECT 1 FROM src.int_special_offers
 WHERE special_offer_id IS NULL)
  THROW 51000, 'DQ_NULL: int_special_offers', 1;

IF EXISTS (SELECT territory_id FROM src.stg_sales_territory
 GROUP BY territory_id HAVING COUNT_BIG(*)>1)
  THROW 51000, 'DQ_DUP: stg_sales_territory', 1;

IF EXISTS (SELECT 1 FROM src.stg_sales_territory
 WHERE territory_id IS NULL)
  THROW 51000, 'DQ_NULL: stg_sales_territory', 1;

IF EXISTS (SELECT sales_order_id FROM src.int_sales_orders
 GROUP BY sales_order_id HAVING COUNT_BIG(*)>1)
  THROW 51000, 'DQ_DUP: int_sales_orders', 1;

IF EXISTS (SELECT 1 FROM src.int_sales_orders
 WHERE sales_order_id IS NULL)
  THROW 51000, 'DQ_NULL: int_sales_orders', 1;

IF EXISTS (SELECT sales_order_id, sales_order_detail_id FROM src.int_sales_order_lines
 GROUP BY sales_order_id, sales_order_detail_id HAVING COUNT_BIG(*)>1)
  THROW 51000, 'DQ_DUP: int_sales_order_lines', 1;

IF EXISTS (SELECT 1 FROM src.int_sales_order_lines
 WHERE sales_order_id IS NULL OR sales_order_detail_id IS NULL)
  THROW 51000, 'DQ_NULL: int_sales_order_lines', 1;

IF EXISTS (SELECT product_id, location_id FROM src.int_inventory_by_location
 GROUP BY product_id, location_id HAVING COUNT_BIG(*)>1)
  THROW 51000, 'DQ_DUP: int_inventory_by_location', 1;

IF EXISTS (SELECT 1 FROM src.int_inventory_by_location
 WHERE product_id IS NULL OR location_id IS NULL)
  THROW 51000, 'DQ_NULL: int_inventory_by_location', 1;

IF EXISTS (SELECT 1 FROM src.int_sales_order_lines
 WHERE order_qty IS NULL OR order_qty<=0 OR unit_price IS NULL
 OR unit_price<0 OR unit_price_discount IS NULL
 OR unit_price_discount<0 OR unit_price_discount>1
 OR gross_line_amount IS NULL OR discount_amount IS NULL
 OR net_line_amount IS NULL OR line_total IS NULL)
  THROW 51000, 'DQ_SALES: Quantity price discount amount', 1;

IF EXISTS (SELECT 1 FROM src.int_sales_orders
 WHERE order_date IS NULL OR customer_id IS NULL
 OR sub_total IS NULL OR tax_amt IS NULL
 OR freight IS NULL OR total_due IS NULL)
  THROW 51000, 'DQ_ORDER: Thieu ngay khach hoac tien', 1;

IF EXISTS (SELECT 1 FROM src.int_sales_order_lines
 WHERE product_id IS NULL OR special_offer_id IS NULL)
  THROW 51000, 'DQ_NULL: Product hoac offer tren line', 1;

IF EXISTS (SELECT 1 FROM src.int_inventory_by_location
 WHERE quantity IS NULL)
  THROW 51000, 'DQ_NULL: Inventory quantity', 1;

IF EXISTS (SELECT 1 FROM src.int_product
 WHERE safety_stock_level IS NULL OR reorder_point IS NULL
 OR safety_stock_level<0 OR reorder_point<0)
  THROW 51000, 'DQ_THRESHOLD: Product inventory threshold', 1;

DELETE FROM fact.inventory_current;
DELETE FROM fact.sales_order_line;
DELETE FROM fact.sales_order;
DELETE FROM dim.location;
DELETE FROM dim.special_offer;
DELETE FROM dim.sales_person;
DELETE FROM dim.geography;
DELETE FROM dim.territory;
DELETE FROM dim.customer;
DELETE FROM dim.product;
DELETE FROM dim.date;

DECLARE @d0 date, @d1 date;
SELECT @d0=MIN(CAST(order_date AS date)) FROM src.int_sales_orders;
SELECT @d1=MAX(dt) FROM (
 SELECT MAX(CAST(order_date AS date)) dt FROM src.int_sales_orders
 UNION ALL SELECT MAX(CAST(due_date AS date)) FROM src.int_sales_orders
 UNION ALL SELECT MAX(CAST(ship_date AS date)) FROM src.int_sales_orders
 UNION ALL SELECT @snapshot_date
) x;
IF DATEDIFF(day,@d0,@d1)>99999
  THROW 51000,'DQ_DATE: Vuot khoang 100000 ngay',1;
;WITH digits AS (
 SELECT n FROM (VALUES(0),(1),(2),(3),(4),(5),(6),(7),(8),(9)) v(n)
), numbers AS (
 SELECT a.n+10*b.n+100*c.n+1000*e.n+10000*f.n n
 FROM digits a CROSS JOIN digits b CROSS JOIN digits c
 CROSS JOIN digits e CROSS JOIN digits f
), days AS (
 SELECT DATEADD(day,n,@d0) dt FROM numbers
 WHERE n<=DATEDIFF(day,@d0,@d1)
)
INSERT INTO dim.date
SELECT CONVERT(int,CONVERT(char(8),dt,112)),dt,
 YEAR(dt),DATEPART(quarter,dt),MONTH(dt),DAY(dt),
 CONVERT(varchar(7),dt,126) FROM days;

INSERT INTO dim.product (
  product_key, product_name, product_number,
  category_name, subcategory_name, make_flag,
  finished_goods_flag, product_standard_cost, product_list_price,
  safety_stock_level, reorder_point, _gold_processed_at,
  _gold_run_id)
SELECT product_id, product_name, product_number, product_category_name,
  product_subcategory_name, make_flag, finished_goods_flag,
  product_standard_cost, product_list_price, safety_stock_level, reorder_point,
  @loaded_at, @run_id
FROM src.int_product;

INSERT INTO dim.customer (
  customer_key, customer_name, customer_type,
  store_name, _gold_processed_at, _gold_run_id)
SELECT customer_id, customer_name, customer_type, store_name,
  @loaded_at, @run_id
FROM src.int_customer;

INSERT INTO dim.territory (
  territory_key, territory_name, country_region_code,
  _gold_processed_at, _gold_run_id)
SELECT territory_id, name, country_region_code,
  @loaded_at, @run_id
FROM src.stg_sales_territory;

INSERT INTO dim.geography (
  geography_key, city, state_province_name,
  country_region_name, postal_code, _gold_processed_at,
  _gold_run_id)
SELECT address_id, city, state_province_name, country_region_name, postal_code,
  @loaded_at, @run_id
FROM src.int_geography;

INSERT INTO dim.sales_person (
  sales_person_key, sales_person_name, _gold_processed_at,
  _gold_run_id)
SELECT sales_person_id, sales_person_name,
  @loaded_at, @run_id
FROM src.int_sales_person;

INSERT INTO dim.special_offer (
  special_offer_key, description, offer_type,
  category, discount_pct, start_date,
  end_date, _gold_processed_at, _gold_run_id)
SELECT special_offer_id, description, offer_type, category, discount_pct,
  CAST(start_date AS date), CAST(end_date AS date),
  @loaded_at, @run_id
FROM src.int_special_offers;

INSERT INTO dim.location (
  location_key, location_name, _gold_processed_at,
  _gold_run_id)
SELECT location_id, MAX(location_name),
  @loaded_at, @run_id
FROM src.int_inventory_by_location GROUP BY location_id;

IF EXISTS (SELECT 1 FROM dim.sales_person WHERE sales_person_key=-1)
 OR EXISTS (SELECT 1 FROM dim.territory WHERE territory_key=-1)
 OR EXISTS (SELECT 1 FROM dim.geography WHERE geography_key=-1)
 THROW 51000,'DQ_KEY: -1 da ton tai o nguon',1;
INSERT INTO dim.sales_person VALUES
 (-1,'NOT_ASSIGNED',@loaded_at,@run_id);
INSERT INTO dim.territory VALUES
 (-1,'NOT_ASSIGNED',NULL,@loaded_at,@run_id);
INSERT INTO dim.geography VALUES
 (-1,'NOT_ASSIGNED',NULL,NULL,NULL,@loaded_at,@run_id);

INSERT INTO fact.sales_order (
  sales_order_id, order_date_key, due_date_key,
  ship_date_key, customer_key, territory_key,
  sales_person_key, bill_to_geography_key, ship_to_geography_key,
  order_status, online_order_flag, sub_total,
  tax_amt, freight, total_due,
  days_to_ship, is_late_shipment, _gold_processed_at,
  _gold_run_id)
SELECT h.sales_order_id,
  CONVERT(int, CONVERT(char(8), h.order_date, 112)),
  CONVERT(int, CONVERT(char(8), h.due_date, 112)),
  CONVERT(int, CONVERT(char(8), h.ship_date, 112)),
  h.customer_id, COALESCE(h.territory_id,-1),
  COALESCE(h.sales_person_id,-1),
  COALESCE(h.bill_to_address_id,-1),
  COALESCE(h.ship_to_address_id,-1), h.status, h.online_order_flag,
  h.sub_total, h.tax_amt, h.freight, h.total_due,
  h.days_to_ship, h.is_late_shipment,
  @loaded_at, @run_id
FROM src.int_sales_orders h;

INSERT INTO fact.sales_order_line (
  sales_order_id, sales_order_detail_id, order_date_key,
  product_key, customer_key, territory_key,
  sales_person_key, special_offer_key, order_status,
  online_order_flag, order_qty, unit_price,
  unit_price_discount, gross_line_amount, discount_amount,
  net_line_amount, source_line_total, standard_unit_cost_at_order,
  estimated_standard_cost_amount, estimated_standard_margin_amount, cost_match_status,
  _gold_processed_at, _gold_run_id)
SELECT l.sales_order_id, l.sales_order_detail_id,
  CONVERT(int, CONVERT(char(8), h.order_date, 112)),
  l.product_id, h.customer_id, COALESCE(h.territory_id,-1),
  COALESCE(h.sales_person_id,-1), l.special_offer_id,
  h.status, h.online_order_flag, l.order_qty, l.unit_price,
  l.unit_price_discount, l.gross_line_amount, l.discount_amount,
  l.net_line_amount, l.line_total, c.standard_cost,
  CAST(l.order_qty * c.standard_cost AS decimal(28,6)),
  CAST(l.net_line_amount - l.order_qty * c.standard_cost
    AS decimal(28,6)),
  CASE WHEN c.product_id IS NULL THEN 'NO_COST_MATCH'
       ELSE 'MATCHED' END,
  @loaded_at, @run_id
FROM src.int_sales_order_lines l
JOIN src.int_sales_orders h ON l.sales_order_id=h.sales_order_id
LEFT JOIN src.int_product_cost_history c
 ON c.product_id=l.product_id
 AND CAST(h.order_date AS date)>=CAST(c.start_date AS date)
 AND (c.end_date IS NULL
      OR CAST(h.order_date AS date)<=CAST(c.end_date AS date));

INSERT INTO fact.inventory_current (
  product_key, location_key, quantity,
  source_modified_at, _gold_processed_at, _gold_run_id)
SELECT product_id, location_id, quantity, CAST(modified_date AS datetime2(6)),
  @loaded_at, @run_id
FROM src.int_inventory_by_location;

IF EXISTS (SELECT sales_order_id FROM fact.sales_order
 GROUP BY sales_order_id HAVING COUNT_BIG(*)>1)
  THROW 51000, 'DQ_DUP_FACT: sales_order', 1;

IF EXISTS (SELECT sales_order_id, sales_order_detail_id FROM fact.sales_order_line
 GROUP BY sales_order_id, sales_order_detail_id HAVING COUNT_BIG(*)>1)
  THROW 51000, 'DQ_DUP_FACT: sales_order_line', 1;

IF EXISTS (SELECT product_key, location_key FROM fact.inventory_current
 GROUP BY product_key, location_key HAVING COUNT_BIG(*)>1)
  THROW 51000, 'DQ_DUP_FACT: inventory_current', 1;

IF EXISTS (SELECT 1 FROM fact.sales_order f
 LEFT JOIN dim.date d ON f.order_date_key=d.date_key
 WHERE f.order_date_key IS NOT NULL AND d.date_key IS NULL)
  THROW 51000, 'DQ_FK: sales_order.order_date_key', 1;

IF EXISTS (SELECT 1 FROM fact.sales_order f
 LEFT JOIN dim.date d ON f.due_date_key=d.date_key
 WHERE f.due_date_key IS NOT NULL AND d.date_key IS NULL)
  THROW 51000, 'DQ_FK: sales_order.due_date_key', 1;

IF EXISTS (SELECT 1 FROM fact.sales_order f
 LEFT JOIN dim.date d ON f.ship_date_key=d.date_key
 WHERE f.ship_date_key IS NOT NULL AND d.date_key IS NULL)
  THROW 51000, 'DQ_FK: sales_order.ship_date_key', 1;

IF EXISTS (SELECT 1 FROM fact.sales_order f
 LEFT JOIN dim.customer d ON f.customer_key=d.customer_key
 WHERE f.customer_key IS NOT NULL AND d.customer_key IS NULL)
  THROW 51000, 'DQ_FK: sales_order.customer_key', 1;

IF EXISTS (SELECT 1 FROM fact.sales_order f
 LEFT JOIN dim.territory d ON f.territory_key=d.territory_key
 WHERE f.territory_key IS NOT NULL AND d.territory_key IS NULL)
  THROW 51000, 'DQ_FK: sales_order.territory_key', 1;

IF EXISTS (SELECT 1 FROM fact.sales_order f
 LEFT JOIN dim.sales_person d ON f.sales_person_key=d.sales_person_key
 WHERE f.sales_person_key IS NOT NULL AND d.sales_person_key IS NULL)
  THROW 51000, 'DQ_FK: sales_order.sales_person_key', 1;

IF EXISTS (SELECT 1 FROM fact.sales_order f
 LEFT JOIN dim.geography d ON f.bill_to_geography_key=d.geography_key
 WHERE f.bill_to_geography_key IS NOT NULL AND d.geography_key IS NULL)
  THROW 51000, 'DQ_FK: sales_order.bill_to_geography_key', 1;

IF EXISTS (SELECT 1 FROM fact.sales_order f
 LEFT JOIN dim.geography d ON f.ship_to_geography_key=d.geography_key
 WHERE f.ship_to_geography_key IS NOT NULL AND d.geography_key IS NULL)
  THROW 51000, 'DQ_FK: sales_order.ship_to_geography_key', 1;

IF EXISTS (SELECT 1 FROM fact.sales_order_line f
 LEFT JOIN dim.date d ON f.order_date_key=d.date_key
 WHERE f.order_date_key IS NOT NULL AND d.date_key IS NULL)
  THROW 51000, 'DQ_FK: sales_order_line.order_date_key', 1;

IF EXISTS (SELECT 1 FROM fact.sales_order_line f
 LEFT JOIN dim.product d ON f.product_key=d.product_key
 WHERE f.product_key IS NOT NULL AND d.product_key IS NULL)
  THROW 51000, 'DQ_FK: sales_order_line.product_key', 1;

IF EXISTS (SELECT 1 FROM fact.sales_order_line f
 LEFT JOIN dim.customer d ON f.customer_key=d.customer_key
 WHERE f.customer_key IS NOT NULL AND d.customer_key IS NULL)
  THROW 51000, 'DQ_FK: sales_order_line.customer_key', 1;

IF EXISTS (SELECT 1 FROM fact.sales_order_line f
 LEFT JOIN dim.territory d ON f.territory_key=d.territory_key
 WHERE f.territory_key IS NOT NULL AND d.territory_key IS NULL)
  THROW 51000, 'DQ_FK: sales_order_line.territory_key', 1;

IF EXISTS (SELECT 1 FROM fact.sales_order_line f
 LEFT JOIN dim.sales_person d ON f.sales_person_key=d.sales_person_key
 WHERE f.sales_person_key IS NOT NULL AND d.sales_person_key IS NULL)
  THROW 51000, 'DQ_FK: sales_order_line.sales_person_key', 1;

IF EXISTS (SELECT 1 FROM fact.sales_order_line f
 LEFT JOIN dim.special_offer d ON f.special_offer_key=d.special_offer_key
 WHERE f.special_offer_key IS NOT NULL AND d.special_offer_key IS NULL)
  THROW 51000, 'DQ_FK: sales_order_line.special_offer_key', 1;

IF EXISTS (SELECT 1 FROM fact.inventory_current f
 LEFT JOIN dim.product d ON f.product_key=d.product_key
 WHERE f.product_key IS NOT NULL AND d.product_key IS NULL)
  THROW 51000, 'DQ_FK: inventory_current.product_key', 1;

IF EXISTS (SELECT 1 FROM fact.inventory_current f
 LEFT JOIN dim.location d ON f.location_key=d.location_key
 WHERE f.location_key IS NOT NULL AND d.location_key IS NULL)
  THROW 51000, 'DQ_FK: inventory_current.location_key', 1;

IF (SELECT COUNT_BIG(*) FROM fact.sales_order)
 <> (SELECT COUNT_BIG(*) FROM src.int_sales_orders)
  THROW 51000, 'DQ_COUNT: sales_order', 1;

IF (SELECT COUNT_BIG(*) FROM fact.sales_order_line)
 <> (SELECT COUNT_BIG(*) FROM src.int_sales_order_lines)
  THROW 51000, 'DQ_COUNT: sales_order_line', 1;

IF (SELECT COUNT_BIG(*) FROM fact.inventory_current)
 <> (SELECT COUNT_BIG(*) FROM src.int_inventory_by_location)
  THROW 51000, 'DQ_COUNT: inventory_current', 1;

IF EXISTS (SELECT h.sales_order_id
 FROM fact.sales_order h
 LEFT JOIN (SELECT sales_order_id,SUM(net_line_amount) net
 FROM fact.sales_order_line GROUP BY sales_order_id) l
 ON h.sales_order_id=l.sales_order_id
 WHERE l.sales_order_id IS NULL
 OR ABS(h.sub_total-l.net)>@money_tolerance)
  THROW 51000, 'DQ_MONEY: Header subtotal va lines', 1;

IF EXISTS (SELECT 1 FROM fact.sales_order_line
 WHERE ABS(net_line_amount-source_line_total)>@money_tolerance
 OR ABS(gross_line_amount-discount_amount-net_line_amount)
 >@money_tolerance)
  THROW 51000, 'DQ_MONEY: Line amount', 1;

IF EXISTS (SELECT 1 FROM fact.sales_order
 WHERE ABS(sub_total+tax_amt+freight-total_due)>@money_tolerance)
  THROW 51000, 'DQ_MONEY: Total due', 1;

IF (SELECT COALESCE(SUM(quantity),0) FROM fact.inventory_current)
 <> (SELECT COALESCE(SUM(quantity),0)
 FROM src.int_inventory_by_location)
  THROW 51000, 'DQ_STOCK: Tong quantity', 1;

IF EXISTS (SELECT 1 FROM src.int_product_stock_status s
 LEFT JOIN (SELECT product_key,SUM(quantity) q
 FROM fact.inventory_current GROUP BY product_key) i
 ON s.product_id=i.product_key
 WHERE (s.total_stock_qty IS NULL AND i.product_key IS NOT NULL)
 OR (s.total_stock_qty IS NOT NULL AND i.product_key IS NULL)
 OR s.total_stock_qty<>i.q)
  THROW 51000, 'DQ_STOCK: Status va inventory lech nhau', 1;

DELETE FROM dim.product_eligibility;
INSERT INTO dim.product_eligibility (product_key,active_start,active_end,finished_goods_flag,_gold_processed_at,_gold_run_id)
SELECT product_id,CAST(sell_start_date AS date),CAST(sell_end_date AS date),finished_goods_flag,@loaded_at,@run_id FROM src.int_product;
IF EXISTS(SELECT product_key FROM dim.product_eligibility GROUP BY product_key HAVING COUNT_BIG(*)>1)
 THROW 51000,'Duplicate dim.product_eligibility',1;

IF EXISTS(SELECT 1 FROM dim.product_eligibility WHERE product_key IS NULL)
 THROW 51000,'Null key dim.product_eligibility',1;

DELETE FROM dim.currency;
INSERT INTO dim.currency (currency_key,currency_name,_gold_processed_at,_gold_run_id)
SELECT currency_code,name,@loaded_at,@run_id FROM src.int_currency;
IF EXISTS(SELECT currency_key FROM dim.currency GROUP BY currency_key HAVING COUNT_BIG(*)>1)
 THROW 51000,'Duplicate dim.currency',1;

IF EXISTS(SELECT 1 FROM dim.currency WHERE currency_key IS NULL)
 THROW 51000,'Null key dim.currency',1;

DELETE FROM fact.product_price_history;
INSERT INTO fact.product_price_history (product_key,start_date,end_date,list_price,_gold_processed_at,_gold_run_id)
SELECT product_id,start_date,end_date,list_price,@loaded_at,@run_id FROM src.int_product_price_history;
IF EXISTS(SELECT product_key,start_date FROM fact.product_price_history GROUP BY product_key,start_date HAVING COUNT_BIG(*)>1)
 THROW 51000,'Duplicate fact.product_price_history',1;

IF EXISTS(SELECT 1 FROM fact.product_price_history WHERE product_key IS NULL OR start_date IS NULL)
 THROW 51000,'Null key fact.product_price_history',1;

DELETE FROM fact.product_cost_history;
INSERT INTO fact.product_cost_history (product_key,start_date,end_date,standard_cost,_gold_processed_at,_gold_run_id)
SELECT product_id,start_date,end_date,standard_cost,@loaded_at,@run_id FROM src.int_product_cost_history;
IF EXISTS(SELECT product_key,start_date FROM fact.product_cost_history GROUP BY product_key,start_date HAVING COUNT_BIG(*)>1)
 THROW 51000,'Duplicate fact.product_cost_history',1;

IF EXISTS(SELECT 1 FROM fact.product_cost_history WHERE product_key IS NULL OR start_date IS NULL)
 THROW 51000,'Null key fact.product_cost_history',1;

DELETE FROM fact.offer_product;
INSERT INTO fact.offer_product (special_offer_key,product_key,_gold_processed_at,_gold_run_id)
SELECT special_offer_id,product_id,@loaded_at,@run_id FROM src.int_special_offer_products;
IF EXISTS(SELECT special_offer_key,product_key FROM fact.offer_product GROUP BY special_offer_key,product_key HAVING COUNT_BIG(*)>1)
 THROW 51000,'Duplicate fact.offer_product',1;

IF EXISTS(SELECT 1 FROM fact.offer_product WHERE special_offer_key IS NULL OR product_key IS NULL)
 THROW 51000,'Null key fact.offer_product',1;

DELETE FROM fact.sales_quota;
INSERT INTO fact.sales_quota (sales_person_key,quota_date,quota_quarter,sales_quota,_gold_processed_at,_gold_run_id)
SELECT sales_person_id,CAST(quota_date AS date),
 DATEFROMPARTS(YEAR(quota_date),3*((MONTH(quota_date)-1)/3)+1,1),sales_quota,@loaded_at,@run_id FROM src.int_sales_person_quota_history;
IF EXISTS(SELECT sales_person_key,quota_date FROM fact.sales_quota GROUP BY sales_person_key,quota_date HAVING COUNT_BIG(*)>1)
 THROW 51000,'Duplicate fact.sales_quota',1;

IF EXISTS(SELECT 1 FROM fact.sales_quota WHERE sales_person_key IS NULL OR quota_date IS NULL)
 THROW 51000,'Null key fact.sales_quota',1;

DELETE FROM fact.sales_territory_assignment;
INSERT INTO fact.sales_territory_assignment (sales_person_key,territory_key,start_date,end_date,_gold_processed_at,_gold_run_id)
SELECT sales_person_id,territory_id,start_date,end_date,@loaded_at,@run_id FROM src.int_sales_territory_history;
IF EXISTS(SELECT sales_person_key,territory_key,start_date FROM fact.sales_territory_assignment GROUP BY sales_person_key,territory_key,start_date HAVING COUNT_BIG(*)>1)
 THROW 51000,'Duplicate fact.sales_territory_assignment',1;

IF EXISTS(SELECT 1 FROM fact.sales_territory_assignment WHERE sales_person_key IS NULL OR territory_key IS NULL OR start_date IS NULL)
 THROW 51000,'Null key fact.sales_territory_assignment',1;

DELETE FROM fact.currency_rate;
INSERT INTO fact.currency_rate (currency_rate_id,rate_date,from_currency_key,to_currency_key,average_rate,end_of_day_rate,_gold_processed_at,_gold_run_id)
SELECT currency_rate_id,CAST(currency_rate_date AS date),from_currency_code,to_currency_code,average_rate,end_of_day_rate,@loaded_at,@run_id FROM src.int_currency_rate;
IF EXISTS(SELECT currency_rate_id FROM fact.currency_rate GROUP BY currency_rate_id HAVING COUNT_BIG(*)>1)
 THROW 51000,'Duplicate fact.currency_rate',1;

IF EXISTS(SELECT 1 FROM fact.currency_rate WHERE currency_rate_id IS NULL)
 THROW 51000,'Null key fact.currency_rate',1;

DELETE FROM fact.inventory_product_current;
INSERT INTO fact.inventory_product_current (product_key,total_stock_qty,location_count,has_inventory_record,is_out_of_stock,is_below_safety_stock,is_at_reorder_point,stock_data_status,_gold_processed_at,_gold_run_id)
SELECT s.product_id,i.total_stock_qty,i.location_count,
 s.has_inventory_record,s.is_out_of_stock,s.is_below_safety_stock,
 s.is_at_reorder_point,s.stock_data_status,@loaded_at,@run_id FROM src.int_product_stock_status s LEFT JOIN src.int_inventory_by_product i ON s.product_id=i.product_id;
IF EXISTS(SELECT product_key FROM fact.inventory_product_current GROUP BY product_key HAVING COUNT_BIG(*)>1)
 THROW 51000,'Duplicate fact.inventory_product_current',1;

IF EXISTS(SELECT 1 FROM fact.inventory_product_current WHERE product_key IS NULL)
 THROW 51000,'Null key fact.inventory_product_current',1;

IF EXISTS(SELECT 1 FROM fact.product_price_history f LEFT JOIN dim.product d ON f.product_key=d.product_key WHERE d.product_key IS NULL)
 THROW 51000,'FK product_price_history.product_key',1;

IF EXISTS(SELECT 1 FROM fact.product_cost_history f LEFT JOIN dim.product d ON f.product_key=d.product_key WHERE d.product_key IS NULL)
 THROW 51000,'FK product_cost_history.product_key',1;

IF EXISTS(SELECT 1 FROM fact.offer_product f LEFT JOIN dim.product d ON f.product_key=d.product_key WHERE d.product_key IS NULL)
 THROW 51000,'FK offer_product.product_key',1;

IF EXISTS(SELECT 1 FROM fact.offer_product f LEFT JOIN dim.special_offer d ON f.special_offer_key=d.special_offer_key WHERE d.special_offer_key IS NULL)
 THROW 51000,'FK offer_product.special_offer_key',1;

IF EXISTS(SELECT 1 FROM fact.sales_quota f LEFT JOIN dim.sales_person d ON f.sales_person_key=d.sales_person_key WHERE d.sales_person_key IS NULL)
 THROW 51000,'FK sales_quota.sales_person_key',1;

IF EXISTS(SELECT 1 FROM fact.sales_territory_assignment f LEFT JOIN dim.sales_person d ON f.sales_person_key=d.sales_person_key WHERE d.sales_person_key IS NULL)
 THROW 51000,'FK sales_territory_assignment.sales_person_key',1;

IF EXISTS(SELECT 1 FROM fact.sales_territory_assignment f LEFT JOIN dim.territory d ON f.territory_key=d.territory_key WHERE d.territory_key IS NULL)
 THROW 51000,'FK sales_territory_assignment.territory_key',1;

IF EXISTS(SELECT 1 FROM fact.currency_rate f LEFT JOIN dim.currency d ON f.from_currency_key=d.currency_key WHERE d.currency_key IS NULL)
 THROW 51000,'FK currency_rate.from_currency_key',1;

IF EXISTS(SELECT 1 FROM fact.currency_rate f LEFT JOIN dim.currency d ON f.to_currency_key=d.currency_key WHERE d.currency_key IS NULL)
 THROW 51000,'FK currency_rate.to_currency_key',1;

IF EXISTS(SELECT 1 FROM fact.inventory_product_current f LEFT JOIN dim.product d ON f.product_key=d.product_key WHERE d.product_key IS NULL)
 THROW 51000,'FK inventory_product_current.product_key',1;

IF EXISTS(SELECT 1 FROM fact.product_price_history WHERE list_price IS NULL OR list_price<0 OR end_date<start_date)
 OR EXISTS(SELECT 1 FROM fact.sales_quota WHERE sales_quota IS NULL OR sales_quota<0)
 OR EXISTS(SELECT 1 FROM fact.currency_rate WHERE average_rate IS NULL OR average_rate<=0 OR end_of_day_rate IS NULL OR end_of_day_rate<=0)
 THROW 51000,'Invalid history quota or rates',1;

IF EXISTS(SELECT from_currency_key,to_currency_key,rate_date FROM fact.currency_rate
 GROUP BY from_currency_key,to_currency_key,rate_date HAVING COUNT_BIG(*)>1)
 THROW 51000,'Duplicate daily FX pair',1;

IF EXISTS(SELECT 1 FROM fact.product_price_history a JOIN fact.product_price_history b
 ON a.product_key=b.product_key AND a.start_date<b.start_date
 AND (a.end_date IS NULL OR CAST(a.end_date AS date)>=CAST(b.start_date AS date)))
 THROW 51000,'Overlapping dates product_price_history',1;

IF EXISTS(SELECT 1 FROM fact.product_cost_history a JOIN fact.product_cost_history b
 ON a.product_key=b.product_key AND a.start_date<b.start_date
 AND (a.end_date IS NULL OR CAST(a.end_date AS date)>=CAST(b.start_date AS date)))
 THROW 51000,'Overlapping dates product_cost_history',1;

IF (SELECT COUNT_BIG(*) FROM fact.inventory_product_current)<>
 (SELECT COUNT_BIG(*) FROM dim.product)
 OR EXISTS(SELECT 1 FROM fact.inventory_product_current i JOIN dim.product p
 ON p.product_key=i.product_key WHERE i.has_inventory_record IS NULL OR i.stock_data_status IS NULL OR
 (i.total_stock_qty IS NULL AND (i.has_inventory_record<>0 OR i.stock_data_status<>'NO_INVENTORY_RECORD' OR i.is_out_of_stock IS NOT NULL OR i.is_below_safety_stock IS NOT NULL OR i.is_at_reorder_point IS NOT NULL))
 OR (i.total_stock_qty IS NOT NULL AND (i.has_inventory_record<>1 OR i.stock_data_status<>'AVAILABLE'))
 OR (i.total_stock_qty IS NOT NULL AND (i.is_out_of_stock IS NULL
 OR i.is_out_of_stock<>CASE WHEN i.total_stock_qty<=0 THEN 1 ELSE 0 END
 OR i.is_below_safety_stock IS NULL
 OR i.is_below_safety_stock<>CASE WHEN i.total_stock_qty<p.safety_stock_level THEN 1 ELSE 0 END
 OR i.is_at_reorder_point IS NULL
 OR i.is_at_reorder_point<>CASE WHEN i.total_stock_qty<=p.reorder_point THEN 1 ELSE 0 END)))
 THROW 51000,'Stock status inconsistent',1;

IF EXISTS(SELECT 1 FROM src.int_inventory_by_product p
 FULL JOIN (SELECT product_key,SUM(quantity) q,COUNT_BIG(*) n
 FROM fact.inventory_current GROUP BY product_key) i ON p.product_id=i.product_key
 WHERE p.product_id IS NULL OR i.product_key IS NULL
 OR p.total_stock_qty IS NULL OR p.total_stock_qty<>i.q
 OR p.location_count IS NULL OR p.location_count<>i.n)
 THROW 51000,'Product inventory aggregate mismatch',1;

IF EXISTS(SELECT 1 FROM ref.policy p WHERE p.policy_id=@policy_id AND (NOT EXISTS(SELECT 1 FROM dim.currency c WHERE c.currency_key=p.source_currency) OR NOT EXISTS(SELECT 1 FROM dim.currency c WHERE c.currency_key=p.report_currency)))
 THROW 51000,'Policy currency absent from currency master',1;

IF EXISTS(SELECT 1 FROM fact.sales_territory_assignment a
 JOIN fact.sales_territory_assignment b ON a.sales_person_key=b.sales_person_key
 AND a.territory_key=b.territory_key AND a.start_date<b.start_date
 AND (a.end_date IS NULL OR a.end_date>=b.start_date))
 OR EXISTS(SELECT 1 FROM fact.sales_territory_assignment WHERE end_date<start_date)
 THROW 51000,'Invalid territory assignment intervals',1;

IF EXISTS(SELECT 1 FROM dim.product_eligibility WHERE active_start IS NULL OR active_end<active_start)
 THROW 51000,'Invalid product eligibility',1;

DECLARE @complete date,@observed datetime2(6);
SELECT @complete=MIN(last_complete_business_date),
 @observed=MIN(inventory_observed_at)
FROM ops.source_manifest WHERE source_run_id=@source_run_id;
IF @snapshot_date IS NOT NULL
BEGIN
 IF @snapshot_date<>CAST(@observed AS date)
  THROW 51000,'Snapshot date must equal UTC observation date; no invented history',1;
 DELETE FROM fact.inventory_daily_snapshot WHERE snapshot_date=@snapshot_date;
 INSERT INTO fact.inventory_daily_snapshot
 SELECT @snapshot_date,product_key,location_key,quantity,@observed,@run_id
 FROM fact.inventory_current;
END;
DELETE FROM ops.publication;
INSERT INTO ops.publication VALUES
 (1,@run_id,@source_run_id,@policy_id,SYSUTCDATETIME(),@complete,@observed);
INSERT INTO ops.dq_result SELECT @run_id,'ALL_BLOCKING_GATES','BLOCK',0,1,SYSUTCDATETIME();
INSERT INTO ops.dq_result
 SELECT @run_id,'COST_MISSING','WARN',COUNT_BIG(*),
 CASE WHEN COUNT_BIG(*)=0 THEN 1 ELSE 0 END,SYSUTCDATETIME()
 FROM fact.sales_order_line WHERE cost_match_status='NO_COST_MATCH';
DELETE FROM rpt.Sales;
INSERT INTO rpt.Sales SELECT * FROM mart.sales_line_approved;
DELETE FROM rpt.OrdersHeader;
INSERT INTO rpt.OrdersHeader SELECT * FROM mart.order_operations;
DELETE FROM rpt.Stock;
INSERT INTO rpt.Stock SELECT * FROM mart.inventory_product_current;
DELETE FROM rpt.Quota;
INSERT INTO rpt.Quota SELECT * FROM mart.quota_performance;
DELETE FROM rpt.Price;
INSERT INTO rpt.Price SELECT * FROM mart.price_realization;
DELETE FROM rpt.Offer;
INSERT INTO rpt.Offer SELECT * FROM mart.offer_performance;
DELETE FROM rpt.CustomerRFM;
INSERT INTO rpt.CustomerRFM SELECT * FROM mart.customer_rfm_current;
DELETE FROM rpt.DataHealth;
INSERT INTO rpt.DataHealth SELECT * FROM mart.data_health;
 UPDATE ops.gold_run SET status='SUCCEEDED',
   completed_at=SYSUTCDATETIME()
 WHERE run_id=@run_id;
 COMMIT TRANSACTION;
 END TRY
 BEGIN CATCH
  IF @@TRANCOUNT>0 ROLLBACK TRANSACTION;
  UPDATE ops.gold_run SET status='FAILED',
    completed_at=SYSUTCDATETIME(),
    message=LEFT(ERROR_MESSAGE(),2000)
  WHERE run_id=@run_id;
  INSERT INTO ops.dq_result VALUES (@run_id,'LOAD_FAILED','BLOCK',NULL,0,SYSUTCDATETIME());
  THROW;
 END CATCH;
END;
GO

-- END G
