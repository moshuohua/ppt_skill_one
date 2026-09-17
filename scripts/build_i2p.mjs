#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const PT_TO_PX = 96 / 72;
const ptToPx = (pt) => Number(pt) * PT_TO_PX;
const position = (frame) => ({
  left: Number(frame.x),
  top: Number(frame.y),
  width: Number(frame.w),
  height: Number(frame.h),
  ...(frame.rotation !== undefined ? { rotation: Number(frame.rotation) } : {}),
});

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

function lineConfig(line = {}) {
  return {
    style: line.style ?? "solid",
    fill: line.color ?? "#8C8C8C",
    width: Number(line.width ?? 1),
  };
}

function textStyle(style = {}) {
  return {
    fontSize: ptToPx(style.fontPt ?? 14),
    typeface: style.fontFamily,
    bold: Boolean(style.bold),
    italic: Boolean(style.italic),
    color: style.color ?? "#000000",
    alignment: style.align ?? "left",
    verticalAlignment: style.valign ?? "top",
    lineSpacing: style.lineSpacing,
    autoFit: "none",
    wrap: "square",
    insets: style.insets ?? { top: 0, right: 0, bottom: 0, left: 0 },
  };
}

function paragraphInput(element) {
  const baseStyle = element.style ?? {};
  return element.paragraphs.map((paragraph) => {
    const rawRuns = paragraph.runs ?? [{ text: paragraph.text ?? "" }];
    const runs = rawRuns.map((run) => {
      if (typeof run === "string") return run;
      const runStyle = run.style ?? {};
      return {
        run: String(run.text ?? ""),
        textStyle: {
          bold: runStyle.bold,
          italic: runStyle.italic,
          underline: runStyle.underline,
          fontSize: `${runStyle.fontPt ?? baseStyle.fontPt ?? 14}pt`,
          typeface: runStyle.fontFamily ?? baseStyle.fontFamily,
          color: runStyle.color ?? baseStyle.color ?? "#000000",
        },
        ...(run.url ? { link: { uri: run.url, isExternal: true } } : {}),
      };
    });
    return {
      runs,
      ...(paragraph.bullet ? { bulletCharacter: paragraph.bulletCharacter ?? "•" } : {}),
      ...(paragraph.marginLeft !== undefined ? { marginLeft: Number(paragraph.marginLeft) } : {}),
      ...(paragraph.indent !== undefined ? { indent: Number(paragraph.indent) } : {}),
      ...(paragraph.spaceBefore !== undefined ? { spaceBefore: Number(paragraph.spaceBefore) } : {}),
      ...(paragraph.spaceAfter !== undefined ? { spaceAfter: Number(paragraph.spaceAfter) } : {}),
    };
  });
}

function contentTypeFor(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  if (ext === ".png") return "image/png";
  if (ext === ".jpg" || ext === ".jpeg") return "image/jpeg";
  if (ext === ".webp") return "image/webp";
  if (ext === ".svg") return "image/svg+xml";
  throw new Error(`Unsupported image extension: ${ext}`);
}

function addText(slide, element, objectMap) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    name: element.name,
    position: position(element.frame),
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  if (Array.isArray(element.paragraphs)) shape.text.set(paragraphInput(element));
  else shape.text = String(element.text ?? "");
  shape.text.style = textStyle(element.style);
  if (element.hyperlink && element.text) {
    shape.text.get(String(element.text)).link = { uri: element.hyperlink, isExternal: true };
  }
  objectMap.set(element.id, shape);
}

function addShape(slide, element, objectMap) {
  const shape = slide.shapes.add({
    geometry: element.geometry ?? "rect",
    name: element.name,
    position: position(element.frame),
    fill: element.fill ?? "none",
    line: element.line ? lineConfig(element.line) : { style: "solid", fill: "none", width: 0 },
    ...(element.radius !== undefined ? { borderRadius: Number(element.radius) } : {}),
    ...(element.shadow ? { shadow: element.shadow } : {}),
  });
  if (element.text !== undefined) {
    shape.text = String(element.text);
    shape.text.style = textStyle(element.style);
  }
  objectMap.set(element.id, shape);
}

function addLine(slide, element, objectMap) {
  const shape = slide.shapes.add({
    geometry: "line",
    name: element.name,
    position: position(element.frame),
    fill: "none",
    line: lineConfig(element.line),
  });
  objectMap.set(element.id, shape);
}

async function addImage(slide, element, objectMap, specDir) {
  const imagePath = path.resolve(specDir, element.path);
  const bytes = await fs.readFile(imagePath);
  const arrayBuffer = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
  const image = slide.images.add({
    blob: arrayBuffer,
    contentType: contentTypeFor(imagePath),
    alt: element.alt ?? element.name,
    fit: element.fit ?? "contain",
    position: position(element.frame),
    ...(element.crop ? { crop: element.crop } : {}),
    ...(element.geometry ? { geometry: element.geometry } : {}),
    ...(element.radius !== undefined ? { borderRadius: Number(element.radius) } : {}),
  });
  if (element.rotation !== undefined) image.rotation = Number(element.rotation);
  objectMap.set(element.id, image);
}

function axisConfig(visible, numberFormat, side = "value", fontFamily = "Microsoft YaHei") {
  return {
    visible,
    numberFormatCode: numberFormat,
    textStyle: { fontSize: ptToPx(10), fill: "#000000", typeface: fontFamily },
    line: { style: "solid", fill: side === "value" ? "#8C8C8C" : "none", width: side === "value" ? 1 : 0 },
    majorGridlines: side === "value" ? { style: "solid", fill: "#8C8C8C", width: 0.5 } : null,
  };
}

function addChart(slide, element, objectMap) {
  const options = element.options ?? {};
  const fontFamily = options.fontFamily ?? "Microsoft YaHei";
  const chartType = element.chartType ?? "bar";
  const series = (element.series ?? []).map((seriesItem) => {
    const color = seriesItem.color ?? seriesItem.fill ?? "#C7000B";
    const needsStroke = ["line", "scatter", "area"].includes(chartType);
    return {
      name: seriesItem.name,
      values: seriesItem.values,
      ...(seriesItem.xValues ? { xValues: seriesItem.xValues } : {}),
      fill: color,
      ...(seriesItem.line
        ? { line: lineConfig(seriesItem.line) }
        : needsStroke
          ? { line: { style: "solid", fill: color, width: 3 } }
          : {}),
      ...(seriesItem.points ? { points: seriesItem.points } : {}),
      ...(seriesItem.valuesFormatCode ? { valuesFormatCode: seriesItem.valuesFormatCode } : {}),
      ...(seriesItem.dataLabelOverrides ? { dataLabelOverrides: seriesItem.dataLabelOverrides } : {}),
    };
  });
  const horizontalBar = chartType === "bar" && (options.direction ?? "bar") === "bar";
  const chart = slide.charts.add(chartType, {
    position: position(element.frame),
    categories: element.categories ?? [],
    series,
    ...(element.title ? {
      title: element.title,
      titleTextStyle: { fontSize: ptToPx(18), fill: "#C7000B", bold: true, typeface: fontFamily },
    } : {}),
    hasLegend: Boolean(options.legend),
    legend: {
      position: options.legendPosition ?? "bottom",
      overlay: false,
      textStyle: { fontSize: ptToPx(10), fill: "#000000", typeface: fontFamily },
    },
    ...(chartType === "bar" ? {
      barOptions: {
        direction: options.direction ?? "bar",
        grouping: options.grouping ?? "clustered",
        gapWidth: Number(options.gapWidth ?? 45),
      },
    } : {}),
    ...(chartType === "line" ? { lineOptions: { smooth: Boolean(options.smooth), grouping: options.grouping ?? "standard" } } : {}),
    dataLabels: {
      showValue: options.showValues !== false,
      showCategoryName: Boolean(options.showCategoryName),
      showPercent: Boolean(options.showPercent),
      position: options.labelPosition ?? "outEnd",
      textStyle: { fontSize: ptToPx(10), fill: "#000000", bold: true, typeface: fontFamily },
    },
    xAxis: axisConfig(
      options.xAxisVisible !== false,
      horizontalBar ? options.numberFormat : undefined,
      horizontalBar ? "value" : "category",
      fontFamily,
    ),
    yAxis: axisConfig(
      options.yAxisVisible !== false,
      horizontalBar ? undefined : options.numberFormat,
      horizontalBar ? "category" : "value",
      fontFamily,
    ),
    chartFill: "none",
    chartLine: { style: "solid", fill: "none", width: 0 },
    plotAreaFill: "none",
    plotAreaLine: { style: "solid", fill: "none", width: 0 },
  });
  objectMap.set(element.id, chart);
}

function addTable(slide, element, objectMap) {
  const values = element.values ?? [];
  const rows = values.length;
  const columns = rows ? Math.max(...values.map((row) => row.length)) : 0;
  if (!rows || !columns) throw new Error(`Table ${element.id} has no values`);
  const table = slide.tables.add({
    rows,
    columns,
    left: Number(element.frame.x),
    top: Number(element.frame.y),
    width: Number(element.frame.w),
    height: Number(element.frame.h),
    values,
  });
  table.borders.assign({ style: "solid", fill: "#8C8C8C", width: 1 });
  const all = table.cells.block({ row: 0, column: 0, rowCount: rows, columnCount: columns });
  all.textStyle.fontSize = ptToPx(element.fontPt ?? 10);
  all.textStyle.color = "#000000";
  all.textStyle.typeface = element.fontFamily ?? "Microsoft YaHei";
  all.fill = "#FFFFFF";
  if (element.header) {
    const header = table.cells.block({ row: 0, column: 0, rowCount: 1, columnCount: columns });
    header.fill = "#C7000B";
    header.textStyle.color = "#FFFFFF";
    header.textStyle.bold = true;
  }
  objectMap.set(element.id, table);
}

function addConnector(slide, element, objectMap) {
  const source = objectMap.get(element.fromId);
  const target = objectMap.get(element.toId);
  if (!source || !target) throw new Error(`Connector ${element.id} references a missing endpoint`);
  const startArrow = element.startArrow ?? element.head;
  const endArrow = element.endArrow ?? element.tail;
  const connector = slide.shapes.connect(source, target, {
    kind: element.kind ?? "elbow",
    fromSide: element.fromSide,
    toSide: element.toSide,
    line: lineConfig(element.line),
    ...(startArrow ? { head: { type: startArrow, width: "med", length: "med" } } : {}),
    ...(endArrow ? { tail: { type: endArrow, width: "med", length: "med" } } : {}),
  });
  if (element.bringToFront) connector.bringToFront();
  objectMap.set(element.id, connector);
}

function sourceNotes(sources, meta = {}) {
  const lines = ["[Sources]"];
  for (const [index, source] of sources.entries()) {
    const published = source.publishedDate ? ` (${source.publishedDate})` : "";
    lines.push(`${index + 1}. ${source.institution}. ${source.title}${published}. ${source.url}`);
    if (source.metric) {
      lines.push(`   Metric: ${source.metric.definition ?? ""}; unit=${source.metric.unit ?? ""}; period=${source.metric.period ?? ""}; scope=${source.metric.scope ?? ""}`);
    }
    if (Array.isArray(source.supports)) lines.push(`   Supports: ${source.supports.join(", ")}`);
  }
  const insight = meta.insightChain;
  if (insight && typeof insight === "object") {
    lines.push("", "[Analysis]");
    lines.push(`Fact: ${insight.fact ?? ""}`);
    lines.push(`Mechanism: ${insight.mechanism ?? ""}`);
    lines.push(`Strategic intent (inference): ${insight.strategicIntent ?? ""}`);
    lines.push(`Control-point shift (inference): ${insight.controlPointShift ?? ""}`);
    lines.push(`Company action: ${insight.companyAction ?? ""}`);
    lines.push(`Alternative explanation: ${insight.alternativeExplanation ?? ""}`);
    if (Array.isArray(insight.observableSignals)) {
      insight.observableSignals.forEach((signal, index) => lines.push(`Observable signal ${index + 1}: ${signal}`));
    }
  }
  return lines.join("\n");
}

function applyRenderFontFallback(spec, fontFamily) {
  for (const element of spec.elements ?? []) {
    if ((element.type === "text" || (element.type === "shape" && element.text !== undefined)) && element.style) {
      element.style.fontFamily = fontFamily;
    }
    if (Array.isArray(element.paragraphs)) {
      for (const paragraph of element.paragraphs) {
        for (const run of paragraph.runs ?? []) {
          if (run && typeof run === "object") {
            run.style = { ...(run.style ?? {}), fontFamily };
          }
        }
      }
    }
    if (element.type === "chart") {
      element.options = { ...(element.options ?? {}), fontFamily };
    }
    if (element.type === "table") element.fontFamily = fontFamily;
  }
}

async function main() {
  const [specArg, outArg, baseArg = "i2p-slide"] = process.argv.slice(2);
  if (!specArg || !outArg) {
    throw new Error("Usage: build_i2p.mjs <slide-spec.json> <output-dir> [basename]");
  }
  const specPath = path.resolve(specArg);
  const outDir = path.resolve(outArg);
  const baseName = baseArg.replace(/[^a-zA-Z0-9._-]+/g, "-");
  const sourceSpec = JSON.parse(await fs.readFile(specPath, "utf8"));
  const spec = JSON.parse(JSON.stringify(sourceSpec));
  const renderFontFallback = String(sourceSpec.meta?.renderFontFallback ?? "").trim();
  if (renderFontFallback) applyRenderFontFallback(spec, renderFontFallback);
  await fs.mkdir(outDir, { recursive: true });

  const presentation = Presentation.create({
    slideSize: { width: Number(spec.slide.width), height: Number(spec.slide.height) },
  });
  const slide = presentation.slides.add();
  slide.background.fill = spec.slide.background ?? "#FFFFFF";
  const objectMap = new Map();
  const elements = [...spec.elements].sort((a, b) => Number(a.z ?? 0) - Number(b.z ?? 0));
  for (const element of elements.filter((item) => item.type !== "connector")) {
    if (element.type === "text") addText(slide, element, objectMap);
    else if (element.type === "shape") addShape(slide, element, objectMap);
    else if (element.type === "line") addLine(slide, element, objectMap);
    else if (element.type === "image") await addImage(slide, element, objectMap, path.dirname(specPath));
    else if (element.type === "chart") addChart(slide, element, objectMap);
    else if (element.type === "table") addTable(slide, element, objectMap);
  }
  for (const element of elements.filter((item) => item.type === "connector")) {
    addConnector(slide, element, objectMap);
  }

  slide.speakerNotes.textFrame.setText(sourceNotes(spec.sources ?? [], spec.meta ?? {}));
  slide.speakerNotes.setVisible(true);

  const masterPath = path.join(outDir, `${baseName}-master.png`);
  await writeBlob(masterPath, await presentation.export({ slide, format: "png", scale: 3 }));
  const layout = await slide.export({ format: "layout" });
  await fs.writeFile(path.join(outDir, `${baseName}-layout.json`), await layout.text());
  const inspect = await presentation.inspect({ kind: "slide,textbox,shape,image,chart,table,notes", maxChars: 30000 });
  await fs.writeFile(path.join(outDir, `${baseName}-inspect.ndjson`), inspect.ndjson);
  await fs.writeFile(path.join(outDir, `${baseName}-slide-spec.json`), JSON.stringify(sourceSpec, null, 2));

  const pptx = await PresentationFile.exportPptx(presentation);
  const pptxPath = path.join(outDir, `${baseName}.pptx`);
  await pptx.save(pptxPath);
  process.stdout.write(JSON.stringify({ master: masterPath, pptx: pptxPath, renderFontFallback: renderFontFallback || null }, null, 2) + "\n");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
