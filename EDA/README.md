# AdventureWorks exploratory data analysis

The analysis uses the comma-separated AdventureWorks 2019 exports in
`AdventureWorks_2019`. Each file has a header row and a schema-qualified
filename; no source file is modified.

From the repository root, run:

```powershell
python EDA/run_eda.py
```

The script validates primary keys and the core sales joins, reconciles
`SalesOrderDetail.LineTotal` with `SalesOrderHeader.SubTotal`, and writes:

- reproducible summary tables to `EDA/output`;
- report-ready CNSPlots figures to
  `docs/data_warehouse/images/chapter-2/eda`.

The first month in the time series is a partial period because the source date
range begins on 2011-05-31. The range ends on 2014-06-30, so the final month is
complete.
