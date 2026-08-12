import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from ..models import Tool

HEADERS = {"User-Agent": "DMC/0.1 (local agent)"}

def register(registry):
    def web_search(query, max_results=5):
        url = "https://html.duckduckgo.com/html/?q=" + quote(query)
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        results = []
        for item in soup.select(".result")[:max_results]:
            a = item.select_one(".result__a")
            snippet = item.select_one(".result__snippet")
            if a:
                results.append(f"{a.get_text(' ', strip=True)}\n{a.get('href')}\n{snippet.get_text(' ', strip=True) if snippet else ''}")
        return "\n\n".join(results) or "No search results found."

    def fetch_url(url):
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text("\n", strip=True)
        return text[:30000]

    registry.register(Tool(
        "web_search",
        "Search the public internet for current information.",
        {"type": "object", "properties": {"query": {"type": "string"}, "max_results": {"type": "integer", "minimum": 1, "maximum": 10}}, "required": ["query"]},
        web_search))

    registry.register(Tool(
        "fetch_url",
        "Fetch and extract readable text from a public web page.",
        {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]},
        fetch_url))
