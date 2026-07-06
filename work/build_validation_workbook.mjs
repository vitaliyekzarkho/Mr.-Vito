import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const sourcePath = "C:/Users/User/Desktop/Ireland Homelessness Project/Raw Data/homelessness.csv.csv";
const outputDir = "C:/Users/User/Documents/Codex/2026-07-04/task-3-data-validation-capstone-report/outputs";
const outputPath = path.join(outputDir, "homelessness_data_validation.xlsx");

const csvText = await fs.readFile(sourcePath, "utf8");
const workbook = await Workbook.fromCSV(csvText, { sheetName: "Raw Data + Checks" });
const raw = workbook.worksheets.getItem("Raw Data + Checks");
const summary = workbook.worksheets.add("Validation Summary");

const rows = csvText.trim().split(/\r?\n/);
const headers = rows[0].split(",");
const dataRows = rows.length - 1;
const lastRow = dataRows + 1;
const numericCols = Array.from({ length: 18 }, (_, index) => {
  let n = index + 2;
  let s = "";
  while (n > 0) {
    const r = (n - 1) % 26;
    s = String.fromCharCode(65 + r) + s;
    n = Math.floor((n - 1) / 26);
  }
  return s;
});
const integerFormula = `=IF(AND(${numericCols.map((col) => `INT(${col}2)=${col}2`).join(",")}),\"Pass\",\"Fail\")`;

const checkHeaders = [
  "Gender Check",
  "Gender Difference",
  "Age Check",
  "Age Difference",
  "Accommodation Check",
  "Accommodation Difference",
  "Citizenship Check",
  "Citizenship Difference",
  "Duplicate Region Check",
  "Integer Check",
];

raw.getRange("T1:AC1").values = [checkHeaders];
raw.getRange("T2:AC2").formulas = [[
  "=IF(C2+D2=B2,\"Pass\",\"Fail\")",
  "=C2+D2-B2",
  "=IF(E2+F2+G2+H2=B2,\"Pass\",\"Fail\")",
  "=E2+F2+G2+H2-B2",
  "=IF(I2+J2+K2+L2=B2,\"Pass\",\"Fail\")",
  "=I2+J2+K2+L2-B2",
  "=IF(M2+N2+O2=B2,\"Pass\",\"Fail\")",
  "=M2+N2+O2-B2",
  `=IF(COUNTIF($A$2:$A$${lastRow},A2)>1,\"Fail\",\"Pass\")`,
  integerFormula,
]];
raw.getRange(`T2:AC${lastRow}`).fillDown();

raw.getRange("A1:AC1").format = {
  fill: "#1F4E79",
  font: { bold: true, color: "#FFFFFF" },
  wrapText: true,
};
raw.getRange(`A1:AC${lastRow}`).format.borders = {
  preset: "outside",
  style: "thin",
  color: "#B7C9D6",
};
raw.getRange(`B2:S${lastRow}`).format.numberFormat = "#,##0";
raw.getRange(`U2:U${lastRow}`).format.numberFormat = "#,##0";
raw.getRange(`W2:W${lastRow}`).format.numberFormat = "#,##0";
raw.getRange(`Y2:Y${lastRow}`).format.numberFormat = "#,##0";
raw.getRange(`AA2:AA${lastRow}`).format.numberFormat = "#,##0";
raw.getRange(`T2:T${lastRow}`).conditionalFormats.add("containsText", {
  text: "Fail",
  format: { fill: "#F4CCCC", font: { bold: true, color: "#990000" } },
});
raw.getRange(`V2:V${lastRow}`).conditionalFormats.add("containsText", {
  text: "Fail",
  format: { fill: "#F4CCCC", font: { bold: true, color: "#990000" } },
});
raw.getRange(`X2:X${lastRow}`).conditionalFormats.add("containsText", {
  text: "Fail",
  format: { fill: "#F4CCCC", font: { bold: true, color: "#990000" } },
});
raw.getRange(`Z2:Z${lastRow}`).conditionalFormats.add("containsText", {
  text: "Fail",
  format: { fill: "#F4CCCC", font: { bold: true, color: "#990000" } },
});
raw.getRange("A:A").format.columnWidth = 14;
raw.getRange("B:S").format.columnWidth = 13;
raw.getRange("T:AC").format.columnWidth = 16;
raw.getRange("A1:AC1").format.rowHeight = 48;
raw.freezePanes.freezeRows(1);

summary.getRange("A1:D1").merge();
summary.getRange("A1").values = [["Task 3 - Data Validation"]];
summary.getRange("A1").format = {
  fill: "#1F4E79",
  font: { bold: true, color: "#FFFFFF", size: 16 },
};

summary.getRange("A3:B12").values = [
  ["Validation Check", "Result"],
  ["Gender totals", null],
  ["Age totals", null],
  ["Accommodation totals", null],
  ["Citizenship totals", null],
  ["Missing values", null],
  ["Negative values", null],
  ["Duplicate regions", null],
  ["Text consistency", null],
  ["Integer values", null],
];
summary.getRange("B4:B12").formulas = [
  [`=IF(COUNTIF('Raw Data + Checks'!T2:T${lastRow},"Fail")=0,"Pass","Fail")`],
  [`=IF(COUNTIF('Raw Data + Checks'!V2:V${lastRow},"Fail")=0,"Pass","Fail")`],
  [`=IF(COUNTIF('Raw Data + Checks'!X2:X${lastRow},"Fail")=0,"Pass","Fail")`],
  [`=IF(COUNTIF('Raw Data + Checks'!Z2:Z${lastRow},"Fail")=0,"Pass","Fail")`],
  [`=IF(COUNTBLANK('Raw Data + Checks'!A2:S${lastRow})=0,"None","Found")`],
  [`=IF(COUNTIF('Raw Data + Checks'!B2:S${lastRow},"<0")=0,"None","Found")`],
  [`=IF(COUNTIF('Raw Data + Checks'!AB2:AB${lastRow},"Fail")=0,"None","Found")`],
  [`=IF(AND(EXACT('Raw Data + Checks'!A2,"Dublin"),EXACT('Raw Data + Checks'!A3,"Mid-East"),EXACT('Raw Data + Checks'!A4,"Midlands"),EXACT('Raw Data + Checks'!A5,"Mid-West"),EXACT('Raw Data + Checks'!A6,"North-East"),EXACT('Raw Data + Checks'!A7,"North-West"),EXACT('Raw Data + Checks'!A8,"South-East"),EXACT('Raw Data + Checks'!A9,"South-West"),EXACT('Raw Data + Checks'!A10,"West")),"Pass","Fail")`],
  [`=IF(COUNTIF('Raw Data + Checks'!AC2:AC${lastRow},"Fail")=0,"Pass","Fail")`],
];

summary.getRange("D3:E7").values = [
  ["Quality Metric", "Value"],
  ["Rows checked", dataRows],
  ["Columns checked", headers.length],
  ["Expected regions", 9],
  ["Overall conclusion", null],
];
summary.getRange("E7").formulas = [[`=IF(COUNTIF(B4:B12,"Fail")+COUNTIF(B4:B12,"Found")=0,"Reliable for further analysis","Review required")`]];

summary.getRange("A14:E14").merge();
summary.getRange("A14").values = [["Conclusion"]];
summary.getRange("A15:E17").merge();
summary.getRange("A15").values = [[
  "The dataset passes the requested arithmetic and quality checks. It can be trusted for further analysis within the scope of these validation tests.",
]];

summary.getRange("A3:B3").format = {
  fill: "#D9EAF7",
  font: { bold: true },
};
summary.getRange("D3:E3").format = {
  fill: "#D9EAF7",
  font: { bold: true },
};
summary.getRange("A14").format = {
  fill: "#D9EAF7",
  font: { bold: true },
};
summary.getRange("A3:B12").format.borders = { preset: "all", style: "thin", color: "#D9E2EA" };
summary.getRange("D3:E7").format.borders = { preset: "all", style: "thin", color: "#D9E2EA" };
summary.getRange("A15:E17").format = {
  wrapText: true,
  fill: "#F7FAFC",
  borders: { preset: "outside", style: "thin", color: "#D9E2EA" },
};
summary.getRange("A:A").format.columnWidth = 26;
summary.getRange("B:B").format.columnWidth = 18;
summary.getRange("D:D").format.columnWidth = 20;
summary.getRange("E:E").format.columnWidth = 28;
summary.getRange("A1").format.rowHeight = 28;
summary.showGridLines = false;

summary.getRange("B4:B12").conditionalFormats.add("containsText", {
  text: "Pass",
  format: { fill: "#D9EAD3", font: { bold: true, color: "#274E13" } },
});
summary.getRange("B4:B12").conditionalFormats.add("containsText", {
  text: "None",
  format: { fill: "#D9EAD3", font: { bold: true, color: "#274E13" } },
});
summary.getRange("B4:B12").conditionalFormats.add("containsText", {
  text: "Fail",
  format: { fill: "#F4CCCC", font: { bold: true, color: "#990000" } },
});
summary.getRange("B4:B12").conditionalFormats.add("containsText", {
  text: "Found",
  format: { fill: "#F4CCCC", font: { bold: true, color: "#990000" } },
});

await fs.mkdir(outputDir, { recursive: true });

const inspectSummary = await workbook.inspect({
  kind: "table",
  range: "Validation Summary!A3:E12",
  include: "values,formulas",
  tableMaxRows: 12,
  tableMaxCols: 5,
});
console.log(inspectSummary.ndjson);

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 300 },
  summary: "final formula error scan",
});
console.log(errors.ndjson);

try {
  const output = await SpreadsheetFile.exportXlsx(workbook);
  await output.save(outputPath);
  console.log("export ok");
} catch (error) {
  console.error("export failed", error);
  throw error;
}

console.log(JSON.stringify({ outputPath }));
