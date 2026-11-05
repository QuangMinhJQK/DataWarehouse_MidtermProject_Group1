-- Source: docs/source/Gold_Warehouse_Huong_dan_chi_tiet (3).docx
-- BEGIN B
IF OBJECT_ID('dim.date', 'U') IS NULL
CREATE TABLE dim.date (
  date_key int NOT NULL, full_date date NOT NULL,
  calendar_year int NOT NULL, calendar_quarter int NOT NULL,
  month_number int NOT NULL, day_of_month int NOT NULL,
  year_month varchar(7) NOT NULL
);
GO
IF OBJECT_ID('dim.product', 'U') IS NULL
CREATE TABLE dim.product (
  product_key int NOT NULL,
  product_name varchar(200) NULL,
  product_number varchar(50) NULL,
  category_name varchar(100) NULL,
  subcategory_name varchar(100) NULL,
  make_flag bit NULL,
  finished_goods_flag bit NULL,
  product_standard_cost decimal(28,6) NULL,
  product_list_price decimal(28,6) NULL,
  safety_stock_level int NULL,
  reorder_point int NULL,
  _gold_processed_at datetime2(6) NOT NULL,
  _gold_run_id varchar(36) NOT NULL
);
GO
IF OBJECT_ID('dim.customer', 'U') IS NULL
CREATE TABLE dim.customer (
  customer_key int NOT NULL,
  customer_name varchar(300) NULL,
  customer_type varchar(20) NULL,
  store_name varchar(200) NULL,
  _gold_processed_at datetime2(6) NOT NULL,
  _gold_run_id varchar(36) NOT NULL
);
GO
IF OBJECT_ID('dim.territory', 'U') IS NULL
CREATE TABLE dim.territory (
  territory_key int NOT NULL,
  territory_name varchar(100) NULL,
  country_region_code varchar(10) NULL,
  _gold_processed_at datetime2(6) NOT NULL,
  _gold_run_id varchar(36) NOT NULL
);
GO
IF OBJECT_ID('dim.geography', 'U') IS NULL
CREATE TABLE dim.geography (
  geography_key int NOT NULL,
  city varchar(100) NULL,
  state_province_name varchar(100) NULL,
  country_region_name varchar(100) NULL,
  postal_code varchar(30) NULL,
  _gold_processed_at datetime2(6) NOT NULL,
  _gold_run_id varchar(36) NOT NULL
);
GO
IF OBJECT_ID('dim.sales_person', 'U') IS NULL
CREATE TABLE dim.sales_person (
  sales_person_key int NOT NULL,
  sales_person_name varchar(300) NULL,
  _gold_processed_at datetime2(6) NOT NULL,
  _gold_run_id varchar(36) NOT NULL
);
GO
IF OBJECT_ID('dim.special_offer', 'U') IS NULL
CREATE TABLE dim.special_offer (
  special_offer_key int NOT NULL,
  description varchar(300) NULL,
  offer_type varchar(100) NULL,
  category varchar(100) NULL,
  discount_pct decimal(19,8) NULL,
  start_date date NULL,
  end_date date NULL,
  _gold_processed_at datetime2(6) NOT NULL,
  _gold_run_id varchar(36) NOT NULL
);
GO
IF OBJECT_ID('dim.location', 'U') IS NULL
CREATE TABLE dim.location (
  location_key int NOT NULL,
  location_name varchar(100) NULL,
  _gold_processed_at datetime2(6) NOT NULL,
  _gold_run_id varchar(36) NOT NULL
);
GO
IF OBJECT_ID('fact.sales_order', 'U') IS NULL
CREATE TABLE fact.sales_order (
  sales_order_id int NOT NULL,
  order_date_key int NULL,
  due_date_key int NULL,
  ship_date_key int NULL,
  customer_key int NULL,
  territory_key int NULL,
  sales_person_key int NULL,
  bill_to_geography_key int NULL,
  ship_to_geography_key int NULL,
  order_status int NULL,
  online_order_flag bit NULL,
  sub_total decimal(28,6) NULL,
  tax_amt decimal(28,6) NULL,
  freight decimal(28,6) NULL,
  total_due decimal(28,6) NULL,
  days_to_ship int NULL,
  is_late_shipment bit NULL,
  _gold_processed_at datetime2(6) NOT NULL,
  _gold_run_id varchar(36) NOT NULL
);
GO
IF OBJECT_ID('fact.sales_order_line', 'U') IS NULL
CREATE TABLE fact.sales_order_line (
  sales_order_id int NOT NULL,
  sales_order_detail_id int NOT NULL,
  order_date_key int NULL,
  product_key int NULL,
  customer_key int NULL,
  territory_key int NULL,
  sales_person_key int NULL,
  special_offer_key int NULL,
  order_status int NULL,
  online_order_flag bit NULL,
  order_qty int NULL,
  unit_price decimal(28,6) NULL,
  unit_price_discount decimal(19,8) NULL,
  gross_line_amount decimal(28,6) NULL,
  discount_amount decimal(28,6) NULL,
  net_line_amount decimal(28,6) NULL,
  source_line_total decimal(28,6) NULL,
  standard_unit_cost_at_order decimal(28,6) NULL,
  estimated_standard_cost_amount decimal(28,6) NULL,
  estimated_standard_margin_amount decimal(28,6) NULL,
  cost_match_status varchar(30) NULL,
  _gold_processed_at datetime2(6) NOT NULL,
  _gold_run_id varchar(36) NOT NULL
);
GO
IF OBJECT_ID('fact.inventory_current', 'U') IS NULL
CREATE TABLE fact.inventory_current (
  product_key int NOT NULL,
  location_key int NOT NULL,
  quantity bigint NULL,
  source_modified_at datetime2(6) NULL,
  _gold_processed_at datetime2(6) NOT NULL,
  _gold_run_id varchar(36) NOT NULL
);
GO
IF OBJECT_ID('ops.gold_run', 'U') IS NULL
CREATE TABLE ops.gold_run (
  run_id varchar(36) NOT NULL,
  started_at datetime2(6) NOT NULL,
  completed_at datetime2(6) NULL,
  status varchar(20) NOT NULL,
  message varchar(2000) NULL
);
GO
IF OBJECT_ID('dim.product_eligibility','U') IS NULL
CREATE TABLE dim.product_eligibility (
 product_key int NULL,
 active_start date NULL,
 active_end date NULL,
 finished_goods_flag bit NULL,
 _gold_processed_at datetime2(6) NULL,
 _gold_run_id varchar(36) NULL
);
GO
IF OBJECT_ID('dim.currency','U') IS NULL
CREATE TABLE dim.currency (
 currency_key varchar(10) NULL,
 currency_name varchar(100) NULL,
 _gold_processed_at datetime2(6) NULL,
 _gold_run_id varchar(36) NULL
);
GO
IF OBJECT_ID('fact.product_price_history','U') IS NULL
CREATE TABLE fact.product_price_history (
 product_key int NULL,
 start_date datetime2(6) NULL,
 end_date datetime2(6) NULL,
 list_price decimal(28,6) NULL,
 _gold_processed_at datetime2(6) NULL,
 _gold_run_id varchar(36) NULL
);
GO
IF OBJECT_ID('fact.product_cost_history','U') IS NULL
CREATE TABLE fact.product_cost_history (
 product_key int NULL,
 start_date datetime2(6) NULL,
 end_date datetime2(6) NULL,
 standard_cost decimal(28,6) NULL,
 _gold_processed_at datetime2(6) NULL,
 _gold_run_id varchar(36) NULL
);
GO
IF OBJECT_ID('fact.offer_product','U') IS NULL
CREATE TABLE fact.offer_product (
 special_offer_key int NULL,
 product_key int NULL,
 _gold_processed_at datetime2(6) NULL,
 _gold_run_id varchar(36) NULL
);
GO
IF OBJECT_ID('fact.sales_quota','U') IS NULL
CREATE TABLE fact.sales_quota (
 sales_person_key int NULL,
 quota_date date NULL,
 quota_quarter date NULL,
 sales_quota decimal(28,6) NULL,
 _gold_processed_at datetime2(6) NULL,
 _gold_run_id varchar(36) NULL
);
GO
IF OBJECT_ID('fact.sales_territory_assignment','U') IS NULL
CREATE TABLE fact.sales_territory_assignment (
 sales_person_key int NULL,
 territory_key int NULL,
 start_date datetime2(6) NULL,
 end_date datetime2(6) NULL,
 _gold_processed_at datetime2(6) NULL,
 _gold_run_id varchar(36) NULL
);
GO
IF OBJECT_ID('fact.currency_rate','U') IS NULL
CREATE TABLE fact.currency_rate (
 currency_rate_id int NULL,
 rate_date date NULL,
 from_currency_key varchar(10) NULL,
 to_currency_key varchar(10) NULL,
 average_rate decimal(28,10) NULL,
 end_of_day_rate decimal(28,10) NULL,
 _gold_processed_at datetime2(6) NULL,
 _gold_run_id varchar(36) NULL
);
GO
IF OBJECT_ID('fact.inventory_product_current','U') IS NULL
CREATE TABLE fact.inventory_product_current (
 product_key int NULL,
 total_stock_qty bigint NULL,
 location_count bigint NULL,
 has_inventory_record bit NULL,
 is_out_of_stock bit NULL,
 is_below_safety_stock bit NULL,
 is_at_reorder_point bit NULL,
 stock_data_status varchar(40) NULL,
 _gold_processed_at datetime2(6) NULL,
 _gold_run_id varchar(36) NULL
);
GO
IF OBJECT_ID('ref.policy','U') IS NULL
CREATE TABLE ref.policy(
 policy_id varchar(40) NOT NULL, approved bit NOT NULL,
 approved_by varchar(200) NULL, approved_at datetime2(6) NULL,
 source_currency varchar(10) NOT NULL,
 report_currency varchar(10) NOT NULL,
 fx_units varchar(30) NOT NULL,
 quota_grain varchar(20) NOT NULL,
 stock_max_age_hours int NOT NULL,
 metric_version varchar(40) NOT NULL
);
GO
IF OBJECT_ID('ref.order_status','U') IS NULL
CREATE TABLE ref.order_status(
 policy_id varchar(40) NOT NULL,status_code int NOT NULL,
 status_label varchar(100) NOT NULL,include_sales bit NOT NULL
);
GO
IF OBJECT_ID('ops.source_manifest','U') IS NULL
CREATE TABLE ops.source_manifest(
 source_run_id varchar(36) NOT NULL,table_name varchar(100) NOT NULL,
 row_count bigint NOT NULL,recorded_at datetime2(6) NOT NULL,
 last_complete_business_date date NOT NULL,
 inventory_observed_at datetime2(6) NOT NULL
);
GO
IF OBJECT_ID('ops.publication','U') IS NULL
CREATE TABLE ops.publication(
 publication_id int NOT NULL,run_id varchar(36) NOT NULL,
 source_run_id varchar(36) NOT NULL,policy_id varchar(40) NOT NULL,
 published_at datetime2(6) NOT NULL,last_complete_date date NOT NULL,
 inventory_observed_at datetime2(6) NOT NULL
);
GO
IF OBJECT_ID('ops.dq_result','U') IS NULL
CREATE TABLE ops.dq_result(
 run_id varchar(36) NOT NULL,check_id varchar(100) NOT NULL,
 severity varchar(10) NOT NULL,observed_value decimal(28,6) NULL,
 passed bit NOT NULL,recorded_at datetime2(6) NOT NULL
);
GO
IF OBJECT_ID('fact.inventory_daily_snapshot','U') IS NULL
CREATE TABLE fact.inventory_daily_snapshot(
 snapshot_date date NOT NULL,product_key int NOT NULL,
 location_key int NOT NULL,quantity bigint NOT NULL,
 inventory_observed_at datetime2(6) NOT NULL,
 source_gold_run_id varchar(36) NOT NULL
);
GO
IF OBJECT_ID('ml.forecast_stage','U') IS NULL
CREATE TABLE ml.forecast_stage(
 scoring_run_id varchar(36) NOT NULL,product_key int NOT NULL,
 cutoff_date date NOT NULL,horizon_days int NOT NULL,
 predicted_qty decimal(28,6) NOT NULL,baseline_qty decimal(28,6) NULL,
 model_version varchar(100) NOT NULL,dataset_id varchar(100) NOT NULL,
 feature_version varchar(40) NOT NULL,source_gold_run_id varchar(36) NOT NULL,
 availability_mode varchar(30) NOT NULL,scored_at datetime2(6) NOT NULL,
 valid_until datetime2(6) NOT NULL
);
GO
IF OBJECT_ID('ml.forecast_prediction','U') IS NULL
CREATE TABLE ml.forecast_prediction(
 scoring_run_id varchar(36) NOT NULL,product_key int NOT NULL,
 cutoff_date date NOT NULL,horizon_days int NOT NULL,
 predicted_qty decimal(28,6) NOT NULL,baseline_qty decimal(28,6) NULL,
 model_version varchar(100) NOT NULL,dataset_id varchar(100) NOT NULL,
 feature_version varchar(40) NOT NULL,source_gold_run_id varchar(36) NOT NULL,
 availability_mode varchar(30) NOT NULL,scored_at datetime2(6) NOT NULL,
 valid_until datetime2(6) NOT NULL
);
GO
IF OBJECT_ID('ops.scoring_publication','U') IS NULL
CREATE TABLE ops.scoring_publication(
 scoring_run_id varchar(36) NOT NULL,published_at datetime2(6) NOT NULL
);
GO

-- END B
