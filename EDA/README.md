# AdventureWorks exploratory data analysis

The analysis uses the headerless, tab-separated exports in
`AdventureWorks/raw`. Column names are mapped from `instawdb.sql`; no source
file is modified.

From the repository root, run:

```powershell
python EDA/run_eda.py
```

The script validates primary keys and the core sales joins, reconciles
`SalesOrderDetail.LineTotal` with `SalesOrderHeader.SubTotal`, and writes:

- reproducible summary tables to `EDA/output`;
- report-ready CNSPlots figures to
  `docs/data_warehouse/images/chapter-2/eda`.

The first and last months in the time series are partial periods because the
source date range begins on 2022-05-30 and ends on 2025-06-29.
