-- Source: docs/source/Gold_Warehouse_Huong_dan_chi_tiet (3).docx
-- BEGIN D
CREATE OR ALTER PROCEDURE ops.usp_register_silver
 @source_run_id varchar(36),@last_complete_date date,
 @inventory_observed_at datetime2(6)
AS
BEGIN
 SET NOCOUNT ON;
 IF @source_run_id IS NULL OR LEN(@source_run_id)<>36
  OR @last_complete_date IS NULL OR @inventory_observed_at IS NULL
  THROW 51000,'Explicit source run, complete date and inventory observation required',1;
 IF @inventory_observed_at>SYSUTCDATETIME()
  THROW 51000,'Inventory observation cannot be in the future',1;
 IF EXISTS(SELECT 1 FROM ops.source_manifest WHERE source_run_id=@source_run_id)
  THROW 51000,'Source manifest immutable: use new source run',1;
 BEGIN TRY
 BEGIN TRANSACTION;
INSERT INTO ops.source_manifest SELECT @source_run_id,'int_product',COUNT_BIG(*),SYSUTCDATETIME(),@last_complete_date,@inventory_observed_at FROM src.int_product;
INSERT INTO ops.source_manifest SELECT @source_run_id,'int_customer',COUNT_BIG(*),SYSUTCDATETIME(),@last_complete_date,@inventory_observed_at FROM src.int_customer;
INSERT INTO ops.source_manifest SELECT @source_run_id,'int_sales_orders',COUNT_BIG(*),SYSUTCDATETIME(),@last_complete_date,@inventory_observed_at FROM src.int_sales_orders;
INSERT INTO ops.source_manifest SELECT @source_run_id,'int_sales_order_lines',COUNT_BIG(*),SYSUTCDATETIME(),@last_complete_date,@inventory_observed_at FROM src.int_sales_order_lines;
INSERT INTO ops.source_manifest SELECT @source_run_id,'int_product_price_history',COUNT_BIG(*),SYSUTCDATETIME(),@last_complete_date,@inventory_observed_at FROM src.int_product_price_history;
INSERT INTO ops.source_manifest SELECT @source_run_id,'int_product_cost_history',COUNT_BIG(*),SYSUTCDATETIME(),@last_complete_date,@inventory_observed_at FROM src.int_product_cost_history;
INSERT INTO ops.source_manifest SELECT @source_run_id,'int_special_offers',COUNT_BIG(*),SYSUTCDATETIME(),@last_complete_date,@inventory_observed_at FROM src.int_special_offers;
INSERT INTO ops.source_manifest SELECT @source_run_id,'int_special_offer_products',COUNT_BIG(*),SYSUTCDATETIME(),@last_complete_date,@inventory_observed_at FROM src.int_special_offer_products;
INSERT INTO ops.source_manifest SELECT @source_run_id,'int_inventory_by_location',COUNT_BIG(*),SYSUTCDATETIME(),@last_complete_date,@inventory_observed_at FROM src.int_inventory_by_location;
INSERT INTO ops.source_manifest SELECT @source_run_id,'int_inventory_by_product',COUNT_BIG(*),SYSUTCDATETIME(),@last_complete_date,@inventory_observed_at FROM src.int_inventory_by_product;
INSERT INTO ops.source_manifest SELECT @source_run_id,'int_product_stock_status',COUNT_BIG(*),SYSUTCDATETIME(),@last_complete_date,@inventory_observed_at FROM src.int_product_stock_status;
INSERT INTO ops.source_manifest SELECT @source_run_id,'int_geography',COUNT_BIG(*),SYSUTCDATETIME(),@last_complete_date,@inventory_observed_at FROM src.int_geography;
INSERT INTO ops.source_manifest SELECT @source_run_id,'int_sales_person',COUNT_BIG(*),SYSUTCDATETIME(),@last_complete_date,@inventory_observed_at FROM src.int_sales_person;
INSERT INTO ops.source_manifest SELECT @source_run_id,'int_sales_person_quota_history',COUNT_BIG(*),SYSUTCDATETIME(),@last_complete_date,@inventory_observed_at FROM src.int_sales_person_quota_history;
INSERT INTO ops.source_manifest SELECT @source_run_id,'int_sales_territory_history',COUNT_BIG(*),SYSUTCDATETIME(),@last_complete_date,@inventory_observed_at FROM src.int_sales_territory_history;
INSERT INTO ops.source_manifest SELECT @source_run_id,'int_currency',COUNT_BIG(*),SYSUTCDATETIME(),@last_complete_date,@inventory_observed_at FROM src.int_currency;
INSERT INTO ops.source_manifest SELECT @source_run_id,'int_currency_rate',COUNT_BIG(*),SYSUTCDATETIME(),@last_complete_date,@inventory_observed_at FROM src.int_currency_rate;
COMMIT;
END TRY BEGIN CATCH
 IF @@TRANCOUNT>0 ROLLBACK;
 THROW;
END CATCH;
END;
GO

-- END D
