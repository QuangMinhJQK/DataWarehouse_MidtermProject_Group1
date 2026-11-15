"""Reproducible exploratory analysis for the AdventureWorks sales scope.

The raw files in ``AdventureWorks/raw`` are tab-separated exports without a
header row.  Column names below are taken from ``instawdb.sql``.  The script
validates the core joins used by the warehouse design, writes summary tables,
and exports report-ready figures with CNSPlots.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

try:
    import cnsplots as cns
except ImportError as exc:  # pragma: no cover - environment-specific message
    raise SystemExit(
        "Missing dependency 'cnsplots'. Install EDA/requirements.txt before running."
    ) from exc


REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "AdventureWorks" / "raw"
OUTPUT_DIR = REPO_ROOT / "EDA" / "output"
FIGURE_DIR = (
    REPO_ROOT / "docs" / "data_warehouse" / "images" / "chapter-2" / "eda"
)

SCHEMAS: dict[str, list[str]] = {
    "SalesOrderHeader": [
        "SalesOrderID",
        "RevisionNumber",
        "OrderDate",
        "DueDate",
        "ShipDate",
        "Status",
        "OnlineOrderFlag",
        "SalesOrderNumber",
        "PurchaseOrderNumber",
        "AccountNumber",
        "CustomerID",
        "SalesPersonID",
        "TerritoryID",
        "BillToAddressID",
        "ShipToAddressID",
        "ShipMethodID",
        "CreditCardID",
        "CreditCardApprovalCode",
        "CurrencyRateID",
        "SubTotal",
        "TaxAmt",
        "Freight",
        "TotalDue",
        "Comment",
        "rowguid",
        "ModifiedDate",
    ],
    "SalesOrderDetail": [
        "SalesOrderID",
        "SalesOrderDetailID",
        "CarrierTrackingNumber",
        "OrderQty",
        "ProductID",
        "SpecialOfferID",
        "UnitPrice",
        "UnitPriceDiscount",
        "LineTotal",
        "rowguid",
        "ModifiedDate",
    ],
    "Product": [
        "ProductID",
        "Name",
        "ProductNumber",
        "MakeFlag",
        "FinishedGoodsFlag",
        "Color",
        "SafetyStockLevel",
        "ReorderPoint",
        "StandardCost",
        "ListPrice",
        "Size",
        "SizeUnitMeasureCode",
        "WeightUnitMeasureCode",
        "Weight",
        "DaysToManufacture",
        "ProductLine",
        "Class",
        "Style",
        "ProductSubcategoryID",
        "ProductModelID",
        "SellStartDate",
        "SellEndDate",
        "DiscontinuedDate",
        "rowguid",
        "ModifiedDate",
    ],
    "ProductSubcategory": [
        "ProductSubcategoryID",
        "ProductCategoryID",
        "Name",
        "rowguid",
        "ModifiedDate",
    ],
    "ProductCategory": [
        "ProductCategoryID",
        "Name",
        "rowguid",
        "ModifiedDate",
    ],
    "Customer": [
        "CustomerID",
        "PersonID",
        "StoreID",
        "TerritoryID",
        "AccountNumber",
        "rowguid",
        "ModifiedDate",
    ],
    "SalesTerritory": [
        "TerritoryID",
        "Name",
        "CountryRegionCode",
        "Group",
        "SalesYTD",
        "SalesLastYear",
        "CostYTD",
        "CostLastYear",
        "rowguid",
        "ModifiedDate",
    ],
}

PRIMARY_KEYS = {
    "SalesOrderHeader": ["SalesOrderID"],
    "SalesOrderDetail": ["SalesOrderDetailID"],
    "Product": ["ProductID"],
    "ProductSubcategory": ["ProductSubcategoryID"],
    "ProductCategory": ["ProductCategoryID"],
    "Customer": ["CustomerID"],
    "SalesTerritory": ["TerritoryID"],
}


def read_raw(table_name: str) -> pd.DataFrame:
    """Load one headerless tab-separated export with its SQL schema."""
    path = RAW_DIR / f"{table_name}.csv"
    if not path.exists():
        raise FileNotFoundError(f"Source table not found: {path}")
    expected_columns = SCHEMAS[table_name]
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        rows = list(csv.reader(source, delimiter="\t"))

    invalid_rows = [
        (row_number, len(row))
        for row_number, row in enumerate(rows, start=1)
        if len(row) != len(expected_columns)
    ]
    if invalid_rows:
        examples = ", ".join(
            f"row {row_number}: {width} columns"
            for row_number, width in invalid_rows[:5]
        )
        raise ValueError(
            f"Unexpected column count in {table_name}; "
            f"expected {len(expected_columns)} ({examples})"
        )

    return pd.DataFrame(rows, columns=expected_columns).replace("", pd.NA)


def convert_numeric(frame: pd.DataFrame, columns: list[str]) -> None:
    for column in columns:
        frame[column] = pd.to_numeric(frame[column], errors="raise")


def validate_primary_keys(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for table_name, key in PRIMARY_KEYS.items():
        frame = tables[table_name]
        missing_key = int(frame[key].isna().any(axis=1).sum())
        duplicate_key = int(frame.duplicated(key).sum())
        if missing_key or duplicate_key:
            raise ValueError(
                f"Invalid primary key in {table_name}: "
                f"missing={missing_key}, duplicate={duplicate_key}"
            )
        rows.append(
            {
                "Table": table_name,
                "Rows": len(frame),
                "MissingPrimaryKey": missing_key,
                "DuplicatePrimaryKey": duplicate_key,
            }
        )
    return pd.DataFrame(rows)


def count_orphans(child: pd.Series, parent: pd.Series) -> int:
    populated = child.dropna()
    return int((~populated.isin(parent)).sum())


def prepare_data() -> tuple[dict[str, pd.DataFrame], pd.DataFrame, pd.DataFrame]:
    tables = {name: read_raw(name) for name in SCHEMAS}
    profile = validate_primary_keys(tables)

    header = tables["SalesOrderHeader"]
    detail = tables["SalesOrderDetail"]
    product = tables["Product"]

    header["OrderDate"] = pd.to_datetime(header["OrderDate"], errors="raise")
    convert_numeric(header, ["SubTotal", "TaxAmt", "Freight", "TotalDue"])
    convert_numeric(
        detail, ["OrderQty", "UnitPrice", "UnitPriceDiscount", "LineTotal"]
    )

    orphan_checks = {
        "SalesOrderDetail -> SalesOrderHeader": count_orphans(
            detail["SalesOrderID"], header["SalesOrderID"]
        ),
        "SalesOrderDetail -> Product": count_orphans(
            detail["ProductID"], product["ProductID"]
        ),
        "SalesOrderHeader -> Customer": count_orphans(
            header["CustomerID"], tables["Customer"]["CustomerID"]
        ),
        "SalesOrderHeader -> SalesTerritory": count_orphans(
            header["TerritoryID"], tables["SalesTerritory"]["TerritoryID"]
        ),
        "Product -> ProductSubcategory": count_orphans(
            product["ProductSubcategoryID"],
            tables["ProductSubcategory"]["ProductSubcategoryID"],
        ),
        "ProductSubcategory -> ProductCategory": count_orphans(
            tables["ProductSubcategory"]["ProductCategoryID"],
            tables["ProductCategory"]["ProductCategoryID"],
        ),
    }
    if any(orphan_checks.values()):
        raise ValueError(f"Orphan keys detected: {orphan_checks}")

    line_total = float(detail["LineTotal"].sum())
    subtotal = float(header["SubTotal"].sum())
    if abs(line_total - subtotal) > 0.01:
        raise ValueError(
            f"LineTotal ({line_total}) does not reconcile to SubTotal ({subtotal})"
        )

    quality = pd.DataFrame(
        [
            {"Check": "Order rows", "Value": len(header)},
            {"Check": "Order-detail rows", "Value": len(detail)},
            {"Check": "Duplicate primary keys", "Value": 0},
            {"Check": "Orphan core foreign keys", "Value": 0},
            {"Check": "Distinct status values", "Value": header["Status"].nunique()},
            {
                "Check": "Missing SalesPersonID",
                "Value": int(header["SalesPersonID"].isna().sum()),
            },
            {
                "Check": "Missing CurrencyRateID",
                "Value": int(header["CurrencyRateID"].isna().sum()),
            },
            {
                "Check": "Customers without orders",
                "Value": int(
                    (~tables["Customer"]["CustomerID"].isin(header["CustomerID"])).sum()
                ),
            },
            {
                "Check": "Products without subcategory",
                "Value": int(product["ProductSubcategoryID"].isna().sum()),
            },
            {"Check": "LineTotal minus SubTotal", "Value": line_total - subtotal},
        ]
    )

    base = (
        detail.merge(
            header[
                [
                    "SalesOrderID",
                    "OrderDate",
                    "OnlineOrderFlag",
                    "CustomerID",
                    "TerritoryID",
                    "Status",
                ]
            ],
            on="SalesOrderID",
            validate="many_to_one",
        )
        .merge(
            product[["ProductID", "ProductSubcategoryID"]],
            on="ProductID",
            validate="many_to_one",
        )
        .merge(
            tables["ProductSubcategory"][
                ["ProductSubcategoryID", "ProductCategoryID"]
            ],
            on="ProductSubcategoryID",
            how="left",
            validate="many_to_one",
        )
        .merge(
            tables["ProductCategory"][["ProductCategoryID", "Name"]].rename(
                columns={"Name": "Category"}
            ),
            on="ProductCategoryID",
            how="left",
            validate="many_to_one",
        )
        .merge(
            tables["SalesTerritory"][["TerritoryID", "Name", "Group"]].rename(
                columns={"Name": "Territory", "Group": "RegionGroup"}
            ),
            on="TerritoryID",
            how="left",
            validate="many_to_one",
        )
    )

    channel_labels = {"1": "Trực tuyến", "0": "Đại lý"}
    base["Channel"] = base["OnlineOrderFlag"].map(channel_labels)
    header["Channel"] = header["OnlineOrderFlag"].map(channel_labels)
    if base["Channel"].isna().any() or header["Channel"].isna().any():
        raise ValueError("Unexpected OnlineOrderFlag value")

    base["Category"] = base["Category"].fillna("Chưa phân loại")
    base["Territory"] = base["Territory"].fillna("Chưa xác định")
    return tables, base, quality


def make_summaries(
    tables: dict[str, pd.DataFrame], base: pd.DataFrame
) -> dict[str, pd.DataFrame]:
    header = tables["SalesOrderHeader"]

    monthly = (
        base.assign(Month=base["OrderDate"].dt.to_period("M").dt.to_timestamp())
        .groupby("Month", as_index=False)
        .agg(
            Revenue=("LineTotal", "sum"),
            Quantity=("OrderQty", "sum"),
            Orders=("SalesOrderID", "nunique"),
        )
    )
    monthly["RevenueMillions"] = monthly["Revenue"] / 1_000_000

    channel = (
        header.groupby("Channel", as_index=False)
        .agg(
            Orders=("SalesOrderID", "nunique"),
            Customers=("CustomerID", "nunique"),
            Revenue=("SubTotal", "sum"),
            AverageOrderValue=("SubTotal", "mean"),
            MedianOrderValue=("SubTotal", "median"),
        )
        .sort_values("Revenue", ascending=False)
    )
    channel["OrderSharePct"] = channel["Orders"] / channel["Orders"].sum() * 100
    channel["RevenueSharePct"] = (
        channel["Revenue"] / channel["Revenue"].sum() * 100
    )

    category = (
        base.groupby("Category", as_index=False)
        .agg(
            Revenue=("LineTotal", "sum"),
            Quantity=("OrderQty", "sum"),
            Orders=("SalesOrderID", "nunique"),
        )
        .sort_values("Revenue", ascending=False)
    )
    category["RevenueSharePct"] = (
        category["Revenue"] / category["Revenue"].sum() * 100
    )
    category["RevenueMillions"] = category["Revenue"] / 1_000_000

    territory = (
        base.groupby("Territory", as_index=False)
        .agg(
            Revenue=("LineTotal", "sum"),
            Quantity=("OrderQty", "sum"),
            Orders=("SalesOrderID", "nunique"),
        )
        .sort_values("Revenue", ascending=False)
    )
    territory["RevenueSharePct"] = (
        territory["Revenue"] / territory["Revenue"].sum() * 100
    )
    territory["RevenueMillions"] = territory["Revenue"] / 1_000_000

    return {
        "monthly_summary": monthly,
        "channel_summary": channel,
        "category_summary": category,
        "territory_summary": territory,
    }


def annotate_bars(ax: plt.Axes, decimals: int = 1) -> None:
    for patch in ax.patches:
        value = patch.get_height()
        ax.annotate(
            f"{value:.{decimals}f}",
            (patch.get_x() + patch.get_width() / 2, value),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
        )


def save_figures(
    tables: dict[str, pd.DataFrame], summaries: dict[str, pd.DataFrame]
) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    header = tables["SalesOrderHeader"]
    monthly = summaries["monthly_summary"]
    category = summaries["category_summary"]
    territory = summaries["territory_summary"]

    with cns.settings.context(
        font_family="Times New Roman",
        figure_dpi=120,
        savefig_dpi=240,
        axes_grid=True,
    ):
        cns.figure(width=600, height=320, color_cycle="Tableau")
        ax = cns.lineplot(
            data=monthly,
            x="Month",
            y="RevenueMillions",
            errorbar=None,
            marker="o",
            linewidth=1.8,
        )
        ax.scatter(
            monthly.iloc[[0, -1]]["Month"],
            monthly.iloc[[0, -1]]["RevenueMillions"],
            color="#E66C37",
            s=35,
            zorder=4,
            label="Tháng biên chưa đủ dữ liệu",
        )
        ax.set(
            title="Doanh thu dòng hàng theo tháng",
            xlabel="Tháng đặt hàng",
            ylabel="Doanh thu (triệu đơn vị tiền tệ)",
        )
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))
        ax.tick_params(axis="x", rotation=45)
        ax.legend(loc="upper left", frameon=False)
        cns.savefig(FIGURE_DIR / "monthly_revenue.png")
        plt.close()

        cns.figure(width=520, height=320, color_cycle="Tableau")
        order = category["Category"].tolist()
        ax = cns.barplot(
            data=category,
            x="Category",
            y="RevenueMillions",
            order=order,
            color="#0078D4",
        )
        ax.set(
            title="Doanh thu theo danh mục sản phẩm",
            xlabel="Danh mục",
            ylabel="Doanh thu (triệu đơn vị tiền tệ)",
        )
        annotate_bars(ax)
        cns.savefig(FIGURE_DIR / "category_revenue.png")
        plt.close()

        cns.figure(width=500, height=330, color_cycle="Tableau")
        ax = cns.boxplot(
            data=header,
            x="Channel",
            y="SubTotal",
            order=["Trực tuyến", "Đại lý"],
            showoutliers=False,
            add_count=True,
            color="#00A88F",
        )
        ax.set_yscale("log")
        ax.set(
            title="Phân phối giá trị đơn hàng theo kênh",
            xlabel="Kênh bán hàng",
            ylabel="Giá trị đơn hàng (thang log)",
        )
        cns.savefig(FIGURE_DIR / "order_value_by_channel.png")
        plt.close()

        cns.figure(width=650, height=340, color_cycle="Tableau")
        territory_order = territory["Territory"].tolist()
        ax = cns.barplot(
            data=territory,
            x="Territory",
            y="RevenueMillions",
            order=territory_order,
            color="#5B5FC7",
        )
        ax.set(
            title="Doanh thu theo lãnh thổ bán hàng",
            xlabel="Lãnh thổ",
            ylabel="Doanh thu (triệu đơn vị tiền tệ)",
        )
        ax.tick_params(axis="x", rotation=35)
        annotate_bars(ax)
        cns.savefig(FIGURE_DIR / "territory_revenue.png")
        plt.close()


def write_outputs(
    profile: pd.DataFrame,
    quality: pd.DataFrame,
    summaries: dict[str, pd.DataFrame],
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    profile.to_csv(OUTPUT_DIR / "dataset_profile.csv", index=False, encoding="utf-8-sig")
    quality.to_csv(OUTPUT_DIR / "quality_checks.csv", index=False, encoding="utf-8-sig")
    for name, frame in summaries.items():
        frame.to_csv(OUTPUT_DIR / f"{name}.csv", index=False, encoding="utf-8-sig")


def main() -> None:
    tables, base, quality = prepare_data()
    profile = validate_primary_keys(tables)
    summaries = make_summaries(tables, base)
    write_outputs(profile, quality, summaries)
    save_figures(tables, summaries)

    header = tables["SalesOrderHeader"]
    print("EDA completed successfully")
    print(f"Orders: {len(header):,}")
    print(f"Order-detail rows: {len(base):,}")
    print(
        "Order-date range: "
        f"{header['OrderDate'].min().date()} to {header['OrderDate'].max().date()}"
    )
    print(f"Tables: {OUTPUT_DIR}")
    print(f"Figures: {FIGURE_DIR}")


if __name__ == "__main__":
    main()
