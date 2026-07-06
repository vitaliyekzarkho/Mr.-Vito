import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const inputPath = "C:/Users/User/Documents/Codex/2026-07-04/task-3-data-validation-capstone-report/work/other_datasets_validation.json";
const outputDir = "C:/Users/User/Documents/Codex/2026-07-04/task-3-data-validation-capstone-report/outputs";
const outputPath = path.join(outputDir, "other_datasets_data_validation.xlsx");

const results = JSON.parse(await fs.readFile(inputPath, "utf8"));
const workbook = Workbook.create();

function colName(n) {
  let s = "";
  while (n > 0) {
    const r = (n - 1) % 26;
    s = String.fromCharCode(65 + r) + s;
    n = Math.floor((n - 1) / 26);
  }
  return s;
}

function safeSheetName(name) {
  return name.replace(/[\\/*?:[\]]/g, " ").slice(0, 31);
}

function writeTable(sheet, startRow, startCol, headers, rows) {
  const matrix = [headers, ...rows.map((row) => headers.map((h) => row[h] ?? ""))];
  const endRow = startRow + matrix.length - 1;
  const endCol = startCol + headers.length - 1;
  const range = `${colName(startCol)}${startRow}:${colName(endCol)}${endRow}`;
  sheet.getRange(range).values = matrix;
  sheet.getRange(`${colName(startCol)}${startRow}:${colName(endCol)}${startRow}`).format = {
    fill: "#1F4E79",
    font: { bold: true, color: "#FFFFFF" },
    wrapText: true,
  };
  sheet.getRange(range).format.borders = { preset: "outside", style: "thin", color: "#B7C9D6" };
  return endRow;
}

function applyStatusFormatting(sheet, range) {
  for (const text of ["Pass", "None"]) {
    sheet.getRange(range).conditionalFormats.add("containsText", {
      text,
      format: { fill: "#D9EAD3", font: { bold: true, color: "#274E13" } },
    });
  }
  for (const text of ["Fail", "Found", "Review", "Review required"]) {
    sheet.getRange(range).conditionalFormats.add("containsText", {
      text,
      format: { fill: "#F4CCCC", font: { bold: true, color: "#990000" } },
    });
  }
}

const summary = workbook.worksheets.add("Overall Summary");
summary.showGridLines = false;
summary.getRange("A1:G1").merge();
summary.getRange("A1").values = [["Data Validation - Supporting Datasets"]];
summary.getRange("A1").format = {
  fill: "#1F4E79",
  font: { bold: true, color: "#FFFFFF", size: 16 },
};

const summaryRows = results.map((r) => {
  const reviewReasons = r.checks
    .filter((c) => ["Fail", "Found", "Review"].includes(c.Result))
    .filter((c) => !(c["Validation Check"] === "Missing values - all columns" && ["Housing Prices", "Rent by County"].includes(r.dataset)))
    .map((c) => `${c["Validation Check"]}: ${c.Details}`)
    .join("; ");
  return {
    Dataset: r.dataset,
    Rows: r.rows,
    Columns: r.columns,
    "Overall Result": r.overall,
    "Main Finding": reviewReasons || "No blocking quality issues found",
    "Logical Key": r.logical_key.join(" + "),
    "Critical Columns": r.critical_columns.join(", "),
  };
});

writeTable(summary, 3, 1, ["Dataset", "Rows", "Columns", "Overall Result", "Main Finding", "Logical Key", "Critical Columns"], summaryRows);
summary.getRange("A:A").format.columnWidth = 24;
summary.getRange("B:C").format.columnWidth = 12;
summary.getRange("D:D").format.columnWidth = 18;
summary.getRange("E:E").format.columnWidth = 48;
summary.getRange("F:G").format.columnWidth = 40;
summary.getRange("A3:G8").format.wrapText = true;
applyStatusFormatting(summary, "D4:D8");

summary.getRange("A11:G11").merge();
summary.getRange("A11").values = [["Capstone Use Recommendation"]];
summary.getRange("A11").format = { fill: "#D9EAF7", font: { bold: true } };
summary.getRange("A12:G14").merge();
summary.getRange("A12").values = [[
  "Housing prices, population, and rent datasets are suitable for further analysis after noting non-critical missing fields. Unemployment requires care because many VALUE cells are blank. Housing supply/sales requires duplicate transaction-key review before transaction-level modelling.",
]];
summary.getRange("A12:G14").format = {
  wrapText: true,
  fill: "#F7FAFC",
  borders: { preset: "outside", style: "thin", color: "#D9E2EA" },
};

for (const result of results) {
  const sheet = workbook.worksheets.add(safeSheetName(result.dataset));
  sheet.showGridLines = false;
  sheet.getRange("A1:F1").merge();
  sheet.getRange("A1").values = [[`${result.dataset} Validation`]];
  sheet.getRange("A1").format = {
    fill: "#1F4E79",
    font: { bold: true, color: "#FFFFFF", size: 15 },
  };

  const metadataRows = [
    { Field: "Source file", Value: result.file },
    { Field: "Rows", Value: result.rows },
    { Field: "Columns", Value: result.columns },
    { Field: "Overall result", Value: result.overall },
    { Field: "Logical key", Value: result.logical_key.join(" + ") },
    { Field: "Critical columns", Value: result.critical_columns.join(", ") },
  ];
  let row = writeTable(sheet, 3, 1, ["Field", "Value"], metadataRows) + 2;
  sheet.getRange("A:A").format.columnWidth = 28;
  sheet.getRange("B:B").format.columnWidth = 72;
  applyStatusFormatting(sheet, "B6:B6");

  row = writeTable(sheet, row, 1, ["Validation Check", "Result", "Details"], result.checks) + 2;
  applyStatusFormatting(sheet, `B${row - result.checks.length - 1}:B${row - 2}`);

  const uniqueRows = Object.entries(result.unique_counts).map(([Field, Value]) => ({ Field, Value }));
  if (uniqueRows.length) {
    row = writeTable(sheet, row, 1, ["Field", "Value"], uniqueRows) + 2;
  }

  const issueSections = [
    ["Duplicate key samples", result.duplicate_samples],
    ["Text consistency issues", result.text_issues],
    ["Date / period issues", result.date_issues],
    ["Range / domain issues", result.range_issues],
    ["Numeric parsing issues", result.numeric_issues],
  ];

  for (const [title, rows] of issueSections) {
    if (!rows || rows.length === 0) continue;
    sheet.getRange(`A${row}:F${row}`).merge();
    sheet.getRange(`A${row}`).values = [[title]];
    sheet.getRange(`A${row}`).format = { fill: "#D9EAF7", font: { bold: true } };
    row += 1;
    const headers = Array.from(new Set(rows.flatMap((item) => Object.keys(item))));
    row = writeTable(sheet, row, 1, headers, rows) + 2;
  }

  for (const arithmetic of result.arithmetic || []) {
    if (!arithmetic.Samples || arithmetic.Samples.length === 0) continue;
    sheet.getRange(`A${row}:F${row}`).merge();
    sheet.getRange(`A${row}`).values = [[`Arithmetic issue samples - ${arithmetic.Check}`]];
    sheet.getRange(`A${row}`).format = { fill: "#D9EAF7", font: { bold: true } };
    row += 1;
    const headers = Array.from(new Set(arithmetic.Samples.flatMap((item) => Object.keys(item))));
    row = writeTable(sheet, row, 1, headers, arithmetic.Samples) + 2;
  }

  sheet.getRange("A:F").format.wrapText = true;
  sheet.freezePanes.freezeRows(1);
}

await fs.mkdir(outputDir, { recursive: true });

const inspect = await workbook.inspect({
  kind: "table",
  range: "Overall Summary!A3:G8",
  include: "values",
  tableMaxRows: 8,
  tableMaxCols: 7,
});
console.log(inspect.ndjson);

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 300 },
  summary: "final formula error scan",
});
console.log(errors.ndjson);

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(JSON.stringify({ outputPath }));
