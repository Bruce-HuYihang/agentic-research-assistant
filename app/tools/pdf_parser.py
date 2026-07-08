"""PDF 解析工具：支持 URL 和本地路径，使用 PyMuPDF 提取文本"""

import httpx
import fitz  # PyMuPDF
from pathlib import Path
from typing import Optional

MAX_PDF_CHARS = 50000


async def parse_pdf(pdf_source: str) -> Optional[str]:
    """
    解析 PDF 内容。
    支持 URL 和本地文件路径，返回提取的文本内容。
    """
    if pdf_source.startswith(("http://", "https://")):
        return await _parse_pdf_from_url(pdf_source)
    else:
        return _parse_pdf_from_local(pdf_source)


async def _parse_pdf_from_url(url: str) -> Optional[str]:
    """从 URL 下载并解析 PDF"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            return _extract_text(resp.content, url)
    except Exception as e:
        print(f"[WARN] PDF 下载失败 {url}: {e}")
        return None


def _parse_pdf_from_local(path_str: str) -> Optional[str]:
    """从本地文件路径解析 PDF"""
    path = Path(path_str)
    if not path.exists():
        print(f"[WARN] 本地 PDF 文件不存在: {path_str}")
        return None
    try:
        data = path.read_bytes()
        return _extract_text(data, str(path))
    except Exception as e:
        print(f"[WARN] 读取本地 PDF 失败 {path_str}: {e}")
        return None


def _extract_text(pdf_bytes: bytes, source: str = "") -> Optional[str]:
    """使用 PyMuPDF 从字节数据提取文本"""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as e:
        print(f"[WARN] 打开 PDF 失败 {source}: {e}")
        return None

    text_parts = []
    for page_num in range(doc.page_count):
        try:
            page = doc.load_page(page_num)
            text = page.get_text()
            if text.strip():
                text_parts.append(f"--- 第 {page_num + 1} 页 ---\n{text}")
        except Exception as e:
            print(f"[WARN] 提取第 {page_num+1} 页文本失败: {e}")
            continue

        # 防止超大 PDF 耗光内存
        if sum(len(t) for t in text_parts) > MAX_PDF_CHARS:
            text_parts.append("\n\n[内容截断：超过 50,000 字符限制]...")
            break

    doc.close()

    full_text = "\n\n".join(text_parts)
    if not full_text.strip():
        print(f"[WARN] PDF 未提取到任何文本: {source}")
        return None

    print(f"[INFO] PDF 解析完成: {source} ({len(full_text)} 字符)")
    return full_text
