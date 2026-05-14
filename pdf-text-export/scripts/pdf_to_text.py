#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import fitz
import pytesseract
import requests
from PIL import Image
from pypdf import PdfReader


def clean_name(value: str) -> str:
    value = re.sub(r"[\\/:*?\"<>|]+", "-", value).strip()
    return value or "document"


def guess_name_from_url(url: str, index: int) -> str:
    tail = url.rstrip("/").split("/")[-1].strip() or f"downloaded-{index}.pdf"
    if not tail.lower().endswith(".pdf"):
        tail += ".pdf"
    return clean_name(tail)


def load_password_map(path: str | None) -> dict[str, str]:
    merged: dict[str, str] = {}

    raw = os.getenv("PDF_PASSWORD_MAP_JSON", "").strip()
    if raw:
        merged.update(json.loads(raw))

    if path:
        merged.update(json.loads(Path(path).read_text(encoding="utf-8")))

    return merged


def resolve_passwords(pdf_path: Path, password_map: dict[str, str], default_password: str | None) -> list[str]:
    candidates: list[str] = [""]
    keys = [
        str(pdf_path),
        pdf_path.name,
        pdf_path.stem,
    ]
    for key in keys:
        value = password_map.get(key)
        if value is not None and value not in candidates:
            candidates.append(value)
    if default_password is not None and default_password not in candidates:
        candidates.append(default_password)
    return candidates


@dataclass
class PageText:
    text: str
    source: str


@dataclass
class ExtractResult:
    pages: list[PageText]
    password_used: str | None
    engine: str


@dataclass
class DownloadedFile:
    url: str
    path: Path
    size: int


@dataclass
class ConvertedFile:
    source_pdf: Path
    md_path: Path
    txt_path: Path
    engine: str
    password_used: bool
    used_ocr: bool
    page_count: int
    char_count: int


def extract_with_pypdf(pdf_path: Path, passwords: list[str]) -> ExtractResult | None:
    last_error: Exception | None = None
    for password in passwords:
        try:
            reader = PdfReader(str(pdf_path))
            if reader.is_encrypted:
                result = reader.decrypt(password)
                if result == 0:
                    continue
            pages = []
            for page in reader.pages:
                text = page.extract_text() or ""
                pages.append(PageText(text=text, source="text-layer"))
            return ExtractResult(pages=pages, password_used=password or None, engine="pypdf")
        except Exception as exc:  # pragma: no cover - defensive
            last_error = exc
    if last_error:
        print(f"[warn] pypdf failed for {pdf_path.name}: {last_error}", file=sys.stderr)
    return None


def extract_with_pymupdf(pdf_path: Path, passwords: list[str]) -> ExtractResult | None:
    last_error: Exception | None = None
    for password in passwords:
        try:
            doc = fitz.open(pdf_path)
            if doc.needs_pass:
                ok = doc.authenticate(password)
                if not ok:
                    doc.close()
                    continue
            pages = []
            for page in doc:
                text = page.get_text("text") or ""
                pages.append(PageText(text=text, source="text-layer"))
            doc.close()
            return ExtractResult(pages=pages, password_used=password or None, engine="pymupdf")
        except Exception as exc:  # pragma: no cover - defensive
            last_error = exc
    if last_error:
        print(f"[warn] pymupdf failed for {pdf_path.name}: {last_error}", file=sys.stderr)
    return None


def render_page_for_ocr(page: fitz.Page, dpi: int) -> Image.Image:
    scale = dpi / 72.0
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    mode = "RGB" if pix.n < 4 else "RGBA"
    return Image.frombytes(mode, [pix.width, pix.height], pix.samples)


def ensure_ocr_ready() -> None:
    if shutil.which("tesseract") is None:
        raise RuntimeError("tesseract is not installed, but OCR fallback was requested")


def ocr_pdf(
    pdf_path: Path,
    passwords: list[str],
    existing_pages: list[PageText] | None,
    ocr_languages: str,
    dpi: int,
    min_page_chars: int,
) -> ExtractResult:
    ensure_ocr_ready()
    last_error: Exception | None = None
    for password in passwords:
        try:
            doc = fitz.open(pdf_path)
            if doc.needs_pass:
                ok = doc.authenticate(password)
                if not ok:
                    doc.close()
                    continue
            merged_pages: list[PageText] = []
            for index, page in enumerate(doc):
                existing = existing_pages[index] if existing_pages and index < len(existing_pages) else None
                if existing and len(existing.text.strip()) >= min_page_chars:
                    merged_pages.append(existing)
                    continue
                image = render_page_for_ocr(page, dpi=dpi)
                text = pytesseract.image_to_string(image, lang=ocr_languages)
                merged_pages.append(PageText(text=text, source="ocr"))
            doc.close()
            return ExtractResult(pages=merged_pages, password_used=password or None, engine="ocr")
        except Exception as exc:  # pragma: no cover - defensive
            last_error = exc
    raise RuntimeError(f"OCR failed for {pdf_path.name}: {last_error}")


def total_chars(pages: Iterable[PageText]) -> int:
    return sum(len(page.text.strip()) for page in pages)


def write_outputs(output_dir: Path, pdf_path: Path, pages: list[PageText]) -> tuple[Path, Path]:
    stem = clean_name(pdf_path.stem)
    md_path = output_dir / f"{stem}.md"
    txt_path = output_dir / f"{stem}.txt"

    md_parts = [f"# {pdf_path.stem}", "", f"> Extracted from `{pdf_path.name}`.", ""]
    txt_parts = [pdf_path.stem, ""]

    for page_number, page in enumerate(pages, start=1):
        md_parts.append(f"## Page {page_number}")
        md_parts.append("")
        md_parts.append(page.text.rstrip())
        md_parts.append("")

        txt_parts.append(f"===== Page {page_number} =====")
        txt_parts.append("")
        txt_parts.append(page.text.rstrip())
        txt_parts.append("")

    md_path.write_text("\n".join(md_parts).rstrip() + "\n", encoding="utf-8")
    txt_path.write_text("\n".join(txt_parts).rstrip() + "\n", encoding="utf-8")
    return md_path, txt_path


def parse_url_list(urls_raw: str | None, urls_file: str | None) -> list[str]:
    urls: list[str] = []
    if urls_raw:
        for line in urls_raw.splitlines():
            line = line.strip()
            if line:
                urls.append(line)
    if urls_file:
        for line in Path(urls_file).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                urls.append(line)
    deduped: list[str] = []
    seen: set[str] = set()
    for url in urls:
        if url not in seen:
            deduped.append(url)
            seen.add(url)
    return deduped


def download_pdfs(urls: list[str], input_dir: Path) -> list[DownloadedFile]:
    input_dir.mkdir(parents=True, exist_ok=True)
    downloaded: list[DownloadedFile] = []
    name_counts: dict[str, int] = {}
    headers = {"User-Agent": "pdf-text-export/1.0"}

    for index, url in enumerate(urls, start=1):
        response = requests.get(url, headers=headers, timeout=120)
        response.raise_for_status()
        name = guess_name_from_url(url, index)
        stem = Path(name).stem
        suffix = Path(name).suffix or ".pdf"
        count = name_counts.get(name, 0)
        name_counts[name] = count + 1
        final_name = name if count == 0 else f"{stem}-{count + 1}{suffix}"
        out_path = input_dir / final_name
        out_path.write_bytes(response.content)
        downloaded.append(DownloadedFile(url=url, path=out_path, size=out_path.stat().st_size))
    return downloaded


def write_summary(
    summary_path: Path | None,
    input_dir: Path,
    output_dir: Path,
    downloaded: list[DownloadedFile],
    converted: list[ConvertedFile],
    failures: list[str],
) -> None:
    if summary_path is None:
        return

    lines: list[str] = []
    lines.append("# PDF 转文本结果")
    lines.append("")
    lines.append(f"- 运行时间(UTC): {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"- 输入目录: `{input_dir}`")
    lines.append(f"- 输出目录: `{output_dir}`")
    lines.append("")

    if downloaded:
        lines.append("## 本次下载文件")
        lines.append("")
        for item in downloaded:
            lines.append(f"- `{item.path.name}` | {item.size} bytes | {item.url}")
        lines.append("")

    if converted:
        lines.append("## 转换结果")
        lines.append("")
        lines.append("| PDF | 页数 | 字符数 | 引擎 | 是否用密码 | 是否含 OCR | 输出 |")
        lines.append("| --- | ---: | ---: | --- | --- | --- | --- |")
        for item in converted:
            lines.append(
                f"| `{item.source_pdf.name}` | {item.page_count} | {item.char_count} | "
                f"{item.engine} | {'是' if item.password_used else '否'} | "
                f"{'是' if item.used_ocr else '否'} | "
                f"`{item.md_path.name}`, `{item.txt_path.name}` |"
            )
        lines.append("")

    if failures:
        lines.append("## 失败记录")
        lines.append("")
        for failure in failures:
            lines.append(f"- {failure}")
        lines.append("")

    summary_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract text from PDFs with OCR fallback.")
    parser.add_argument("--input-dir", default="input", help="Directory containing PDF files")
    parser.add_argument("--output-dir", default="output", help="Directory for extracted text")
    parser.add_argument("--glob", default="**/*.pdf", help="Glob used to find PDFs under input-dir")
    parser.add_argument("--pdf-urls", help="Newline-separated PDF URLs to download before conversion")
    parser.add_argument("--pdf-urls-file", help="Text file containing one PDF URL per line")
    parser.add_argument("--password-file", help="JSON file mapping pdf path/name/stem to password")
    parser.add_argument("--default-password", default=os.getenv("PDF_PASSWORD"))
    parser.add_argument("--ocr", action="store_true", help="Enable OCR fallback")
    parser.add_argument("--ocr-languages", default="chi_sim+eng")
    parser.add_argument("--ocr-dpi", type=int, default=220)
    parser.add_argument("--min-total-chars", type=int, default=50)
    parser.add_argument("--min-page-chars", type=int, default=10)
    parser.add_argument("--summary-file", help="Markdown summary file path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = Path(args.summary_file) if args.summary_file else None

    password_map = load_password_map(args.password_file)
    urls = parse_url_list(args.pdf_urls, args.pdf_urls_file)
    downloaded: list[DownloadedFile] = []
    if urls:
        downloaded = download_pdfs(urls, input_dir)
        print("[info] downloaded PDFs:")
        for item in downloaded:
            print(f"  - {item.path.name} <- {item.url} ({item.size} bytes)")

    pdf_paths = sorted(input_dir.glob(args.glob))
    if not pdf_paths:
        print(f"[error] no PDFs found under {input_dir} with glob {args.glob}", file=sys.stderr)
        return 1

    failures: list[str] = []
    converted: list[ConvertedFile] = []
    print("[info] PDFs scheduled for conversion:")
    for pdf_path in pdf_paths:
        print(f"  - {pdf_path.name}")

    for pdf_path in pdf_paths:
        passwords = resolve_passwords(pdf_path, password_map, args.default_password)
        result = extract_with_pypdf(pdf_path, passwords) or extract_with_pymupdf(pdf_path, passwords)
        if result is None:
            if not args.ocr:
                failures.append(f"{pdf_path.name}: failed to read text layer and OCR disabled")
                continue
            result = ocr_pdf(
                pdf_path,
                passwords,
                existing_pages=None,
                ocr_languages=args.ocr_languages,
                dpi=args.ocr_dpi,
                min_page_chars=args.min_page_chars,
            )
        elif args.ocr and total_chars(result.pages) < args.min_total_chars:
            result = ocr_pdf(
                pdf_path,
                passwords,
                existing_pages=result.pages,
                ocr_languages=args.ocr_languages,
                dpi=args.ocr_dpi,
                min_page_chars=args.min_page_chars,
            )

        md_path, txt_path = write_outputs(output_dir, pdf_path, result.pages)
        password_note = "yes" if result.password_used else "no/empty"
        sources = {page.source for page in result.pages}
        converted.append(
            ConvertedFile(
                source_pdf=pdf_path,
                md_path=md_path,
                txt_path=txt_path,
                engine=result.engine,
                password_used=bool(result.password_used),
                used_ocr=("ocr" in sources),
                page_count=len(result.pages),
                char_count=total_chars(result.pages),
            )
        )
        print(
            f"[ok] {pdf_path.name} -> {md_path.name}, {txt_path.name} "
            f"(engine={result.engine}, password={password_note}, sources={','.join(sorted(sources))})"
        )

    write_summary(summary_path, input_dir, output_dir, downloaded, converted, failures)

    if failures:
        for failure in failures:
            print(f"[error] {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
