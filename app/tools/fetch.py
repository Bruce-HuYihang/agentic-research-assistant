import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify as md


_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Safari/605.1.15",
]


async def fetch_page(url: str) -> str | None:
    """
    爬取网页并转换为 Markdown 格式。
    返回 Markdown 文本，失败返回 None。
    """
    # 尝试多个 User-Agent 避免被屏蔽
    for ua in _USER_AGENTS:
        headers = {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }

        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
            break  # 成功，跳出重试
        except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.ConnectError) as e:
            # 遇到非致命错误，换 UA 重试
            if ua == _USER_AGENTS[-1]:
                # 最后一个也失败了
                print(f"[WARN] 爬取失败 {url}: {e}")
                return None
            continue
        except Exception as e:
            print(f"[WARN] 爬取失败 {url}: {e}")
            return None

    # 检测编码
    content_type = resp.headers.get("content-type", "")
    if "charset=" in content_type:
        charset = content_type.split("charset=")[-1].split(";")[0].strip()
        resp.encoding = charset
    else:
        resp.encoding = "utf-8"

    # 解析 HTML
    soup = BeautifulSoup(resp.text, "html.parser")

    # 移除无用元素
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
        tag.decompose()

    body = soup.find("body") or soup.find("html") or soup

    # 转换为 Markdown
    markdown_text = md(
        str(body),
        heading_style="ATX",
        bullets="-",
        strip=["a", "img"],
    )

    # 清理多余空行
    lines = [line.strip() for line in markdown_text.split("\n") if line.strip()]
    cleaned = "\n".join(lines)

    # 截断长度
    max_chars = 10000
    if len(cleaned) > max_chars:
        cleaned = cleaned[:max_chars] + "\n\n...[内容截断]..."

    return cleaned
