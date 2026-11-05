-- Source: docs/source/Gold_Warehouse_Huong_dan_chi_tiet (3).docx
-- BEGIN H
CREATE OR ALTER PROCEDURE ops.usp_publish_forecast
 @scoring_run_id varchar(36),@expected_count int,@allow_reconstructed bit=0
AS
BEGIN
 SET NOCOUNT ON;
 BEGIN TRY
 BEGIN TRANSACTION;
 IF @expected_count<=0 OR (SELECT COUNT_BIG(*) FROM ml.forecast_stage
 WHERE scoring_run_id=@scoring_run_id)<>@expected_count
 THROW 51000,'Incomplete scoring stage',1;
 IF EXISTS(SELECT product_key,cutoff_date,horizon_days FROM ml.forecast_stage
 WHERE scoring_run_id=@scoring_run_id GROUP BY product_key,cutoff_date,horizon_days HAVING COUNT_BIG(*)>1)
 THROW 51000,'Duplicate predictions',1;
 IF EXISTS(SELECT 1 FROM ml.forecast_stage s LEFT JOIN dim.product p ON p.product_key=s.product_key
 WHERE s.scoring_run_id=@scoring_run_id AND (p.product_key IS NULL OR s.predicted_qty<0
 OR s.horizon_days<>7 OR s.valid_until<=s.scored_at
 OR s.source_gold_run_id<>(SELECT run_id FROM ops.publication)
 OR (@allow_reconstructed=0 AND s.availability_mode<>'OBSERVED')))
 THROW 51000,'Invalid, stale-source or reconstructed prediction',1;
 DELETE FROM ml.forecast_prediction WHERE scoring_run_id=@scoring_run_id;
 INSERT INTO ml.forecast_prediction SELECT * FROM ml.forecast_stage WHERE scoring_run_id=@scoring_run_id;
 DELETE FROM ops.scoring_publication WHERE scoring_run_id=@scoring_run_id;
 INSERT INTO ops.scoring_publication VALUES(@scoring_run_id,SYSUTCDATETIME());
 DELETE FROM rpt.Forecast;
 INSERT INTO rpt.Forecast SELECT * FROM agent.forecast;
 COMMIT;
 END TRY BEGIN CATCH
 IF @@TRANCOUNT>0 ROLLBACK;
 THROW;
 END CATCH;
END;
GO

-- END H
