#!/usr/bin/env node
/**
 * 通用 Markdown → DOCX 转换器（本项目文档用，封面信息见 docs/cover/*.json）
 *
 * 用法：
 *   node gen-docx.js --md <报告.md> --out <报告.docx> --cover <cover.json>
 *
 * 特性：
 *  - 封面页（标题/副标题/元信息表/单位）来自 cover.json
 *  - 标题层级 H1~H4（黑体），正文宋体小四
 *  - GFM 表格、有序/无序列表、代码块、引用块、水平线（分页）
 *  - 图片自动按页宽缩放；紧跟其后的「图/表 X-Y 描述」行作为居中图注
 *  - 中文 EastAsia 字体（宋体/黑体），西文 Times New Roman
 *  - 页脚页码
 *
 * 字体说明：本机渲染用思源黑体/宋体 CN（微软黑体/宋体的开源等价）；
 * docx 内嵌字体名写「宋体/黑体」，由审阅方 Word 解析回退。
 */
'use strict';
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType,
  ImageRun, PageBreak, PageNumber, Header, Footer, LevelFormat,
  TabStopType, TabStopPosition, convertInchesToTwip, TableLayoutType,
} = require('docx');

// ---------- 字体与字号（half-point） ----------
const FONT = {
  bodyHei: { ascii: 'Times New Roman', eastAsia: '黑体', hAnsi: 'Times New Roman' },
  bodySong: { ascii: 'Times New Roman', eastAsia: '宋体', hAnsi: 'Times New Roman' },
};
const SZ = { h1: 36, h2: 32, h3: 28, h4: 24, body: 24, small: 21, caption: 21, code: 20 };

// ---------- 工具 ----------
function arg(k, d) { const i = process.argv.indexOf('--' + k); return i >= 0 ? process.argv[i + 1] : d; }
function pngSize(buf) {
  // PNG: 16..20 width BE, 20..24 height BE
  try { if (buf.slice(0,8).toString('hex') === '89504e470d0a1a0a') return { w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) }; } catch (_) {}
  return null;
}
function imgScaled(path_, maxW = 540) {
  const buf = fs.readFileSync(path_);
  const nat = pngSize(buf) || { w: maxW, h: maxW * 0.6 };
  let w = nat.w, h = nat.h;
  if (w > maxW) { h = Math.round(h * maxW / w); w = maxW; }
  return new ImageRun({ data: buf, transformation: { width: w, height: h } });
}

// 内联解析：**粗体** *斜体* `代码` → TextRun[]
function inlineRuns(text, font = FONT.bodySong, size = SZ.body, extra = {}) {
  const runs = [];
  // 按 `code` / **bold** / *italic* 分词
  const re = /(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*)/g;
  let last = 0, m;
  const push = (t, opts) => { if (t) runs.push(new TextRun({ text: t, font, size, ...opts, ...extra })); };
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) push(text.slice(last, m.index));
    const tok = m[0];
    if (tok.startsWith('**')) push(tok.slice(2, -2), { bold: true });
    else if (tok.startsWith('`')) push(tok.slice(1, -1), { font: { ascii: 'Consolas', eastAsia: '宋体', hAnsi: 'Consolas' } });
    else if (tok.startsWith('*')) push(tok.slice(1, -1), { italics: true });
    last = re.lastIndex;
  }
  if (last < text.length) push(text.slice(last));
  if (runs.length === 0) runs.push(new TextRun({ text, font, size, ...extra }));
  return runs;
}

// ---------- 段落构造 ----------
function bodyPara(text) {
  // 首行缩进 2 字符：正文小四 12pt × 2 × 20twips/pt = 480 twips
  return new Paragraph({ children: inlineRuns(text), spacing: { line: 360, before: 60, after: 60 }, alignment: AlignmentType.JUSTIFIED, indent: { firstLine: 480 } });
}
function heading(text, level) {
  const sizes = { 1: SZ.h1, 2: SZ.h2, 3: SZ.h3, 4: SZ.h4 };
  const map = { 1: HeadingLevel.HEADING_1, 2: HeadingLevel.HEADING_2, 3: HeadingLevel.HEADING_3, 4: HeadingLevel.HEADING_4 };
  return new Paragraph({
    heading: map[level],
    children: [new TextRun({ text, font: FONT.bodyHei, size: sizes[level], bold: true, color: '1F4E5F' })],
    spacing: { before: level === 1 ? 240 : 180, after: 100 },
    pageBreakBefore: level === 1,
  });
}
function captionPara(text) {
  return new Paragraph({ children: [new TextRun({ text, font: FONT.bodySong, size: SZ.caption, bold: true })], alignment: AlignmentType.CENTER, spacing: { before: 40, after: 160 } });
}
function imgPara(p) {
  return new Paragraph({ children: [imgScaled(p)], alignment: AlignmentType.CENTER, spacing: { before: 120, after: 40 } });
}
function codePara(text) {
  return new Paragraph({
    children: [new TextRun({ text, font: { ascii: 'Consolas', eastAsia: '宋体', hAnsi: 'Consolas' }, size: SZ.code })],
    spacing: { line: 280, before: 20, after: 20 },
    shading: { type: ShadingType.CLEAR, fill: 'F2F4F4' },
    indent: { left: convertInchesToTwip(0.15) },
  });
}
function quotePara(text) {
  return new Paragraph({ children: inlineRuns(text, FONT.bodySong, SZ.body, { italics: true, color: '555555' }), indent: { left: convertInchesToTwip(0.3) }, spacing: { before: 60, after: 60 } });
}
function listItem(text, ordered, level, ref) {
  return new Paragraph({
    children: inlineRuns(text, FONT.bodySong, SZ.body),
    bullet: ordered ? undefined : { level },
    numbering: ordered ? { reference: ref || 'num', level } : undefined,
    spacing: { line: 320, before: 20, after: 20 },
  });
}

// ---------- 表格 ----------
function buildTable(rows) {
  const header = rows[0].map(c => c.trim());
  const body = rows.slice(1).filter(r => !r.every(c => /^[-: ]+$/.test(c.trim())));
  const ncol = header.length;
  // 字符显示宽度：中文/全角=2，其他（数字/字母/符号）=1
  const strW = s => [...s].reduce((a, ch) => { const c = ch.codePointAt(0); return a + ((c >= 0x2e80 && c <= 0x9fff) || (c >= 0xac00 && c <= 0xd7a3) || (c >= 0xf900 && c <= 0xfaff) || (c >= 0xfe30 && c <= 0xfe4f) || (c >= 0xff00 && c <= 0xff60) || (c >= 0xffe0 && c <= 0xffe6) || (c >= 0x3000 && c <= 0x303f) ? 4 : 1); }, 0);
  // 各列最大显示宽度（cap 80 防超长单元格吞噬宽度）→ 按比例分配列宽，最小 5%
  const colMax = new Array(ncol).fill(0);
  for (const r of [header, ...body]) for (let c = 0; c < ncol; c++) { const w = Math.min(strW((r[c] || '').trim()), 80); if (w > colMax[c]) colMax[c] = w; }
  const total = colMax.reduce((a, b) => a + b, 0) || 1;
  const widths = colMax.map(m => Math.max(5, Math.round(m / total * 100)));
  widths[widths.indexOf(Math.max(...widths))] += 100 - widths.reduce((a, b) => a + b, 0);
  const PAGEW = 8730; // 正文区宽 dxa：A4(11906) - 左右页边距(1588×2)
  const colWidthsDxa = widths.map(p => Math.round(PAGEW * p / 100));
  const cell = (text, isHead, ci) => new TableCell({
    children: [new Paragraph({
      children: inlineRuns(text, FONT.bodySong, SZ.small, isHead ? { bold: true } : {}),
      alignment: AlignmentType.LEFT, spacing: { line: 260, before: 20, after: 20 },
    })],
    shading: isHead ? { type: ShadingType.CLEAR, fill: '1F4E5F' } : undefined,
    margins: { top: 40, bottom: 40, left: 80, right: 80 },
    width: { size: widths[ci], type: WidthType.PERCENTAGE },
  });
  // 表头文字白色
  const headCell = (text, ci) => new TableCell({
    children: [new Paragraph({ children: [new TextRun({ text, font: FONT.bodyHei, size: SZ.small, bold: true, color: 'FFFFFF' })], alignment: AlignmentType.CENTER, spacing: { line: 260 } })],
    shading: { type: ShadingType.CLEAR, fill: '1F4E5F' },
    margins: { top: 40, bottom: 40, left: 80, right: 80 },
    width: { size: widths[ci], type: WidthType.PERCENTAGE },
  });
  const tableRows = [new TableRow({ children: header.map((h, i) => headCell(h, i)), tableHeader: true })];
  for (const r of body) {
    while (r.length < ncol) r.push('');
    tableRows.push(new TableRow({ children: r.slice(0, ncol).map((c, i) => cell(c, false, i)) }));
  }
  return new Table({
    rows: tableRows,
    width: { size: 100, type: WidthType.PERCENTAGE },
    columnWidths: colWidthsDxa,
    layout: TableLayoutType.FIXED,
    borders: {
      top: { style: BorderStyle.SINGLE, size: 4, color: '1F4E5F' },
      bottom: { style: BorderStyle.SINGLE, size: 4, color: '1F4E5F' },
      left: { style: BorderStyle.SINGLE, size: 4, color: '7A8B8E' },
      right: { style: BorderStyle.SINGLE, size: 4, color: '7A8B8E' },
      insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: 'BFC9CB' },
      insideVertical: { style: BorderStyle.SINGLE, size: 2, color: 'BFC9CB' },
    },
  });
}

// ---------- Markdown 解析 ----------
function parseTable(lines, i) {
  const rows = [];
  while (i < lines.length && lines[i].includes('|')) { rows.push(lines[i].split('|').slice(1, -1)); i++; }
  return { table: buildTable(rows), next: i };
}

function parseMd(md, baseDir) {
  const lines = md.replace(/\r\n/g, '\n').split('\n');
  const out = [];
  const olRefs = [];   // 每个有序列表块一个独立 reference，保证序号每块从 1 开始
  let olSeq = 0;
  let i = 0;
  const isCaption = s => /^[图表]\s*\d+[-－—]\d+/.test(s.trim());
  while (i < lines.length) {
    let line = lines[i];
    // 空行
    if (/^\s*$/.test(line)) { i++; continue; }
    // 代码块
    if (/^```/.test(line.trim())) {
      const buf = []; i++;
      while (i < lines.length && !/^```/.test(lines[i].trim())) { buf.push(lines[i]); i++; }
      i++; // skip closing
      buf.forEach(b => out.push(codePara(b)));
      continue;
    }
    // 标题
    const hm = /^(#{1,4})\s+(.*)$/.exec(line);
    if (hm) { out.push(heading(hm[2].trim(), hm[1].length)); i++; continue; }
    // 水平线 → 分页
    if (/^(\s*[-*_]){3,}\s*$/.test(line)) { out.push(new Paragraph({ children: [new PageBreak()] })); i++; continue; }
    // 表格
    if (line.includes('|') && i + 1 < lines.length && /^\s*\|?[\s:|-]+\|?\s*$/.test(lines[i + 1]) && lines[i + 1].includes('-')) {
      const r = parseTable(lines, i); out.push(r.table); i = r.next;
      // 紧跟表注：居中、置于表下方（与图注渲染一致）
      if (i < lines.length && isCaption(lines[i])) { out.push(captionPara(lines[i].trim())); i++; }
      continue;
    }
    // 图片（独占一行）
    const im = /^!\[[^\]]*\]\(([^)]+)\)\s*$/.exec(line.trim());
    if (im) {
      const p = path.resolve(baseDir, im[1]);
      if (fs.existsSync(p)) {
        out.push(imgPara(p));
        i++;
        // 紧跟图注
        if (i < lines.length && isCaption(lines[i])) { out.push(captionPara(lines[i].trim())); i++; }
      } else {
        out.push(bodyPara(`[图片缺失: ${im[1]}]`)); i++;
      }
      continue;
    }
    // 引用
    if (/^>\s?/.test(line)) { out.push(quotePara(line.replace(/^>\s?/, ''))); i++; continue; }
    // 有序列表（每个连续块用独立 numbering，序号每块从 1 重置）
    const olm = /^\s*(\d+)\.\s+(.*)$/.exec(line);
    if (olm) {
      // 上一非空行若也是有序项则续接同一块，否则开新块
      let p = i - 1;
      while (p >= 0 && /^\s*$/.test(lines[p])) p--;
      const prevWasOL = p >= 0 && /^\s*\d+\.\s+/.test(lines[p]);
      if (!prevWasOL) { olSeq += 1; olRefs.push(`ol${olSeq}`); }
      out.push(listItem(olm[2], true, 0, olRefs[olRefs.length - 1]));
      i++; continue;
    }
    // 无序列表
    const ulm = /^\s*[-*]\s+(.*)$/.exec(line);
    if (ulm) { out.push(listItem(ulm[1], false, 0)); i++; continue; }
    // 普通段落（合并连续非空行）
    const para = [line];
    i++;
    while (i < lines.length && !/^\s*$/.test(lines[i]) && !/^(#{1,4}\s|```|>\s?|\s*[-*]\s|\s*\d+\.\s)/.test(lines[i]) && !/^!\[[^\]]*\]\([^)]+\)\s*$/.test(lines[i].trim()) && !(lines[i].includes('|') && i + 1 < lines.length && /^\s*\|?[\s:|-]+\|?\s*$/.test(lines[i + 1]) && lines[i + 1].includes('-'))) {
      para.push(lines[i]); i++;
    }
    out.push(bodyPara(para.join(' ')));
  }
  return { paras: out, olRefs };
}

// ---------- 封面 ----------
function cover(cover) {
  const c = cover || {};
  const big = (t, sz, font = FONT.bodyHei, color = '1F4E5F', bold = true) =>
    new Paragraph({ children: [new TextRun({ text: t, font, size: sz, bold, color })], alignment: AlignmentType.CENTER, spacing: { before: 200, after: 200 } });
  const blank = (n = 1) => Array.from({ length: n }, () => new Paragraph({ children: [new TextRun({ text: '' })] }));
  const meta = (k, v) => new TableRow({ children: [
    new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: k, font: FONT.bodyHei, size: SZ.body, bold: true })], alignment: AlignmentType.CENTER })], width: { size: 28, type: WidthType.PERCENTAGE }, margins: { top: 80, bottom: 80, left: 80, right: 80 } }),
    new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: v || '', font: FONT.bodySong, size: SZ.body })], alignment: AlignmentType.CENTER })], width: { size: 72, type: WidthType.PERCENTAGE }, margins: { top: 80, bottom: 80, left: 80, right: 80 } }),
  ] });
  const metaTable = new Table({
    width: { size: 80, type: WidthType.PERCENTAGE },
    alignment: AlignmentType.CENTER,
    rows: [
      meta('文档名称', c.title),
      meta('文档编号', c.docNo || ''),
      meta('版本号', c.version || 'V1.0'),
      meta('编制日期', c.date || ''),
      meta('编 制 人', c.preparedBy || ''),
      meta('审 核 人', c.reviewedBy || ''),
      meta('批 准 人', c.approvedBy || ''),
    ],
    borders: {
      top: { style: BorderStyle.SINGLE, size: 6, color: '1F4E5F' },
      bottom: { style: BorderStyle.SINGLE, size: 6, color: '1F4E5F' },
      left: { style: BorderStyle.SINGLE, size: 6, color: '1F4E5F' },
      right: { style: BorderStyle.SINGLE, size: 6, color: '1F4E5F' },
      insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: '7A8B8E' },
      insideVertical: { style: BorderStyle.SINGLE, size: 2, color: '7A8B8E' },
    },
  });
  const els = [
    ...blank(3),
    big(c.org || '', 36, FONT.bodyHei, 'C8A35C'),
    ...blank(4),
    big(c.title || '文档', 56, FONT.bodyHei, '1F4E5F'),
    ...(c.subtitle ? [big(c.subtitle, 28, FONT.bodySong, '3A4A4F', false)] : []),
    ...blank(5),
    metaTable,
    ...blank(2),
    big(c.classification || '', 20, FONT.bodySong, 'A23B3B', false),
    new Paragraph({ children: [new PageBreak()] }),
  ];
  return els;
}

// ---------- 主 ----------
async function main() {
  const mdPath = arg('md'); const outPath = arg('out'); const coverPath = arg('cover');
  if (!mdPath || !outPath) { console.error('用法: gen-docx.js --md <in.md> --out <out.docx> [--cover <cover.json>]'); process.exit(1); }
  const md = fs.readFileSync(mdPath, 'utf8');
  const baseDir = path.dirname(path.resolve(mdPath));
  let coverObj = null;
  if (coverPath && fs.existsSync(coverPath)) coverObj = JSON.parse(fs.readFileSync(coverPath, 'utf8'));

  const { paras: body, olRefs } = parseMd(md, baseDir);
  const olConfig = olRefs.map(ref => ({ reference: ref, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.START }] }));
  const sections = [];
  // 封面节（无页码）
  if (coverObj) sections.push({ properties: { page: { margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } }, children: cover(coverObj) });
  // 正文节（带页脚页码）
  sections.push({
    properties: { page: { margin: { top: 1440, bottom: 1440, left: 1588, right: 1588 } }, type: undefined },
    headers: { default: new Header({ children: [new Paragraph({ children: [new TextRun({ text: coverObj ? (coverObj.title || '') : '', font: FONT.bodySong, size: 18, color: '7A8B8E' })], alignment: AlignmentType.CENTER })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ children: [new TextRun({ children: ['第 ', PageNumber.CURRENT, ' 页 / 共 ', PageNumber.TOTAL_PAGES, ' 页'], font: FONT.bodySong, size: 18, color: '7A8B8E' })], alignment: AlignmentType.CENTER })] }) },
    children: body,
  });

  const doc = new Document({
    creator: (coverObj && coverObj.preparedBy) || '井震联合速度场建模系统项目组',
    title: coverObj ? coverObj.title : '交付报告',
    styles: {
      default: { document: { run: { font: FONT.bodySong, size: SZ.body }, paragraph: { spacing: { line: 360 } } } },
      paragraphStyles: [
        { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', run: { font: FONT.bodyHei, size: SZ.h1, bold: true, color: '1F4E5F' } },
        { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', run: { font: FONT.bodyHei, size: SZ.h2, bold: true, color: '1F4E5F' } },
        { id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', run: { font: FONT.bodyHei, size: SZ.h3, bold: true, color: '1F4E5F' } },
        { id: 'Heading4', name: 'Heading 4', basedOn: 'Normal', next: 'Normal', run: { font: FONT.bodyHei, size: SZ.h4, bold: true, color: '1F4E5F' } },
      ],
    },
    numbering: { config: olConfig.length ? olConfig : [{ reference: 'num', levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.START }] }] },
    sections,
  });

  const buf = await Packer.toBuffer(doc);
  fs.writeFileSync(outPath, buf);
  console.log(`✓ 已生成 ${outPath}（${body.length} 个正文元素）`);
}
main().catch(e => { console.error('转换失败:', e); process.exit(1); });
