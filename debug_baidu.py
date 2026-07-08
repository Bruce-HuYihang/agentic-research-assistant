"""调试百度搜索的 HTML 结构"""
import httpx
from bs4 import BeautifulSoup
from urllib.parse import quote_plus


headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
}
url = f"https://www.baidu.com/s?wd={quote_plus('Python asyncio 是什么')}&ie=utf-8"

resp = httpx.get(url, headers=headers, follow_redirects=True, timeout=15)
resp.encoding = "utf-8"
soup = BeautifulSoup(resp.text, "html.parser")

# 打印所有 class 名，看看百度现在用啥结构
for i, div in enumerate(soup.find_all("div", class_=True)):
    classes = " ".join(div.get("class", []))
    text = div.get_text(strip=True)[:80]
    if text and "百度" not in text:
        print(f"[{i}] class={classes}")
        print(f"    text={text}")
        print()
