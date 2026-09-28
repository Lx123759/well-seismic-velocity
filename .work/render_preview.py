"""把生成的任务书转为 PDF 并渲染成页面图片，用于检查排版。"""
from pathlib import Path

import fitz  # PyMuPDF
from docx2pdf import convert

ROOT = Path(__file__).resolve().parent.parent
WORK = Path(__file__).resolve().parent
src = next(ROOT.glob("开题任务书_*.docx"))
pdf = WORK / "preview.pdf"
convert(str(src), str(pdf))

out = WORK / "preview"
out.mkdir(exist_ok=True)
for old in out.glob("*.png"):
    old.unlink()
doc = fitz.open(pdf)
for i, page in enumerate(doc):
    page.get_pixmap(dpi=80).save(out / f"page_{i + 1:02d}.png")
print("pages:", len(doc))
