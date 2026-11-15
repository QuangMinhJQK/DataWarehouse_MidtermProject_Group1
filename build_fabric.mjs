// AdventureWorks medallion architecture on Microsoft Fabric.
// Layout is fully declarative; drawio-ai computes all positions and routes.
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { Diagram, frame, grid, icon, box, phantom, renderTree } from "drawio-ai-kit";

const d = new Diagram("pipeline", { iconSize: 68 });

const sourceSchemas = grid("schemas", null, "Source schemas", { cols: 1, gap: 10, pad: 12 }, [
  box("schema_hr", "Human Resources\nHumanResources", { w: 180, h: 56 }),
  box("schema_person", "Person", { w: 180, h: 48 }),
  box("schema_production", "Production", { w: 180, h: 48 }),
  box("schema_purchasing", "Purchasing", { w: 180, h: 48 }),
  box("schema_sales", "Sales", { w: 180, h: 48 }),
]);

const source = frame("source", "Azure SQL Database · AdventureWorks", {
  dir: "col",
  gap: 15,
  fill: "light-dark(#F7F8FA, #151A20)",
  stroke: "#6C7885",
}, [
  icon("azure_sql", "azure_sql_database", "Azure SQL Database"),
  sourceSchemas,
]);

const bronzeLakehouse = frame("bronze_lakehouse_frame", "Lakehouse", {
  dir: "col",
  gap: 15,
  fill: "light-dark(#FFFFFF, #171A1F)",
  stroke: "#B7791F",
}, [
  icon("bronze_lakehouse", "lakehouse", "Lakehouse"),
  box("raw_tables", "Raw Source Tables", { w: 180, h: 64 }),
]);

const bronze = frame("bronze", "Bronze", {
  dir: "col",
  gap: 18,
  fill: "light-dark(#FFF3E4, #332315)",
  stroke: "#B7791F",
}, [bronzeLakehouse]);

const silverLakehouse = frame("silver_lakehouse_frame", "Lakehouse", {
  dir: "col",
  gap: 15,
  fill: "light-dark(#FFFFFF, #171A1F)",
  stroke: "#8A9199",
}, [
  icon("silver_lakehouse", "lakehouse", "Lakehouse"),
  box("stg", "STG\nData Standardization", { w: 220, h: 78 }),
  box("int", "INT\nData Integration & Business Rules", { w: 220, h: 90 }),
]);

const silver = frame("silver", "Silver", {
  dir: "col",
  gap: 18,
  fill: "light-dark(#F4F5F7, #20252B)",
  stroke: "#8A9199",
}, [silverLakehouse]);

const goldWarehouse = frame("gold_warehouse_frame", "Warehouse", {
  dir: "col",
  gap: 14,
  fill: "light-dark(#FFFFFF, #171A1F)",
  stroke: "#C59A16",
}, [
  icon("gold_warehouse", "dbx_data_warehouse", "Warehouse"),
  box("gold_tables", "Dimensions · Facts · Data Marts", { w: 225, h: 72 }),
]);

const goldLakehouse = frame("gold_lakehouse_frame", "Lakehouse", {
  dir: "col",
  gap: 14,
  fill: "light-dark(#FFFFFF, #171A1F)",
  stroke: "#C59A16",
}, [
  icon("gold_lakehouse", "lakehouse", "Lakehouse"),
  box("ml_features", "ML Features · Targets\nml_wide_repeat_30d", { w: 225, h: 82 }),
]);

const gold = frame("gold", "Gold", {
  dir: "col",
  gap: 20,
  fill: "light-dark(#FFF8D8, #332B12)",
  stroke: "#C59A16",
}, [
  goldWarehouse,
  goldLakehouse,
  icon("ml_model", "machine_learning", "Fabric AutoML / ML Model"),
]);

const medallion = phantom("medallion", "", {
  dir: "row",
  gap: 34,
  align: "top",
  header: 0,
  pad: 0,
}, [bronze, silver, gold]);

const workspace = frame("fabric_workspace", "Microsoft Fabric Workspace", {
  dir: "col",
  gap: 22,
  fill: "light-dark(#F3FAF5, #10251A)",
  stroke: "#4E8A63",
}, [
  icon("fabric_logo", "rtb_fabric", "Microsoft Fabric"),
  medallion,
]);

const consumers = frame("consumers", "Consumers", {
  dir: "col",
  gap: 30,
  fill: "light-dark(#F4EEFA, #21162B)",
  stroke: "#8D68A8",
}, [
  icon("power_bi", "power_bi", "Power BI"),
  icon("data_agent", "agent", "Data Agent"),
]);

const tree = phantom("root", "", {
  dir: "row",
  gap: 42,
  align: "center",
  header: 0,
  pad: 10,
}, [
  source,
  icon("ingest_pipeline", "data_pipeline", "Data Pipeline · Copy Data"),
  workspace,
  icon("consumption_hub", "agent", "Consumption"),
  consumers,
]);

renderTree(d, tree, [40, 80]);
d.title("AdventureWorks Medallion Architecture on Microsoft Fabric");

d.link("source", "ingest_pipeline", "", { flow: true });
d.link("ingest_pipeline", "bronze_lakehouse", "Copy Data", { flow: true });
d.link("bronze_lakehouse", "stg", "Dataflow Gen2", { flow: true });
d.link("stg", "int", "", { flow: true });
d.link("int", "gold_warehouse", "Build Gold Tables", { flow: true });
d.link("gold_warehouse", "gold_lakehouse", "Prepare ML Features & Targets", { dash: true });
d.link("gold_lakehouse", "ml_model", "Training Data", { flow: true });
d.link("ml_model", "gold_lakehouse", "ML Results", { dash: true });
d.link("gold", "consumption_hub", "Consumption", { flow: true });
d.link("consumption_hub", "power_bi", "", { role: "fanout" });
d.link("consumption_hub", "data_agent", "", { role: "fanout" });

const res = d.validate();
console.log("VALIDATE:", JSON.stringify({
  ok: res.ok,
  errors: res.errors,
  warnings: res.warnings,
  advice: res.audit.advice,
}));

// Reuse the official Fabric icons supplied in the original fabric.drawio draft.
const assets = JSON.parse(readFileSync(new URL("./fabric-icons.json", import.meta.url), "utf8"));
let xml = d.mxfile("AdventureWorks on Microsoft Fabric");

function replaceCellImage(document, id, imageData) {
  const marker = `id="${id}"`;
  const markerAt = document.indexOf(marker);
  if (markerAt < 0) throw new Error(`Missing generated cell: ${id}`);
  const cellStart = document.lastIndexOf("<mxCell", markerAt);
  const cellEnd = document.indexOf(">", markerAt);
  const originalHead = document.slice(cellStart, cellEnd + 1);
  let updatedHead;
  if (/image=[^;\"]*/.test(originalHead)) {
    updatedHead = originalHead.replace(/image=[^;\"]*/, `image=${imageData}`);
  } else {
    updatedHead = originalHead.replace('style="', `style="image=${imageData};`);
  }
  return document.slice(0, cellStart) + updatedHead + document.slice(cellEnd + 1);
}

for (const [id, imageData] of Object.entries(assets)) {
  xml = replaceCellImage(xml, id, imageData);
}

writeFileSync(new URL("./fabric.drawio", import.meta.url), xml);

// Self-check tail: validate, then render when the draw.io desktop CLI is available.
import { execFileSync as execFileSync } from "node:child_process";
const cli = (args) => process.env.DRAWIO_AI_CLI
  ? execFileSync(process.execPath, [process.env.DRAWIO_AI_CLI, ...args], { encoding: "utf8" })
  : execFileSync("drawio-ai", args, { encoding: "utf8" });
const output = fileURLToPath(new URL("./fabric.drawio", import.meta.url));
try {
  console.log(cli(["render", output, "--check", "-o", output + ".png"]).trim());
} catch (error) {
  console.error("RENDER-SKIPPED:", String(error.message).split("\n")[0]);
}
