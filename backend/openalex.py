import requests
import time
from typing import List, Dict, Optional

OPENALEX_BASE_URL = "https://api.openalex.org"


def search_journals(query: str) -> List[Dict]:
    """
    搜索 OpenAlex 期刊
    """
    start_time = time.time()
    print(f"开始搜索期刊: {query}")
    url = f"{OPENALEX_BASE_URL}/sources"
    params = {
        "search": query,
        "per_page": 20
    }
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        results = []
        for item in data.get("results", []):
            results.append({
                "id": item.get("id", "").replace("https://openalex.org/", ""),
                "display_name": item.get("display_name", ""),
                "issn": item.get("issn_l", ""),
                "publisher": item.get("publisher", "")
            })
        elapsed = round(time.time() - start_time, 2)
        print(f"搜索完成，找到 {len(results)} 个结果，耗时 {elapsed} 秒")
        return results
    except Exception as e:
        print(f"搜索期刊失败: {e}")
        elapsed = round(time.time() - start_time, 2)
        print(f"失败耗时 {elapsed} 秒")
        return []


def rebuild_abstract(inverted_index: Optional[Dict]) -> str:
    """
    从 abstract_inverted_index 重建纯文本摘要
    """
    if not inverted_index:
        return ""
    max_index = 0
    for word, positions in inverted_index.items():
        if positions:
            max_index = max(max_index, max(positions))
    abstract = [""] * (max_index + 1)
    for word, positions in inverted_index.items():
        for pos in positions:
            if pos <= max_index:
                abstract[pos] = word
    return " ".join([word for word in abstract if word])


def fetch_papers_from_journal(openalex_source_id: str, per_page: int = 50) -> List[Dict]:
    """
    从 OpenAlex 获取指定期刊的最新论文
    """
    start_time = time.time()
    print(f"开始获取期刊 {openalex_source_id} 的论文")
    source_id = openalex_source_id
    if not source_id.startswith("S"):
        source_id = f"S{source_id}"
    url = f"{OPENALEX_BASE_URL}/works"
    params = {
        "filter": f"primary_location.source.id:{source_id}",
        "sort": "publication_date:desc",
        "per_page": per_page
    }
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        papers = []
        for item in data.get("results", []):
            work_id = item.get("id", "").replace("https://openalex.org/", "")
            authorships = item.get("authorships", [])
            authors = []
            for auth in authorships:
                author = auth.get("author", {})
                authors.append({
                    "name": author.get("display_name", ""),
                    "id": author.get("id", "")
                })
            biblio = item.get("biblio", {})
            abstract_inverted = item.get("abstract_inverted_index", None)
            abstract = rebuild_abstract(abstract_inverted)
            primary_location = item.get("primary_location", {})
            landing_page_url = primary_location.get("landing_page_url", "")
            if not landing_page_url:
                doi = item.get("doi", "")
                if doi:
                    landing_page_url = doi
            papers.append({
                "openalex_work_id": work_id,
                "title": item.get("title", ""),
                "doi": item.get("doi", ""),
                "publication_date": item.get("publication_date", ""),
                "volume": biblio.get("volume", ""),
                "issue": biblio.get("issue", ""),
                "authors": authors,
                "abstract": abstract,
                "landing_page_url": landing_page_url
            })
        elapsed = round(time.time() - start_time, 2)
        print(f"获取论文完成，找到 {len(papers)} 篇，耗时 {elapsed} 秒")
        return papers
    except Exception as e:
        print(f"获取论文失败: {e}")
        elapsed = round(time.time() - start_time, 2)
        print(f"失败耗时 {elapsed} 秒")
        return []
