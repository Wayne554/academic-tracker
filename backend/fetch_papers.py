"""
从 OpenAlex API 抓取期刊论文信息
OpenAlex 是免费、无需 Key 的学术数据源，覆盖所有主流期刊。
文档：https://docs.openalex.org/
"""
import time
import httpx
from sqlalchemy.orm import Session
from .config import get_settings
from . import models, crud

settings = get_settings()
OPENALEX = settings.OPENALEX_BASE_URL


def _get(url: str, params: dict = None, retries: int = 3) -> dict:
    """带重试的 GET 请求"""
    for i in range(retries):
        try:
            r = httpx.get(url, params=params, timeout=30)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if i == retries - 1:
                print(f"[ERROR] 请求失败 {url}: {e}")
                return {}
            time.sleep(2 ** i)
    return {}


# ========== 根据 ISSN 查找期刊 ==========
def find_journal_by_issn(db: Session, issn: str):
    return db.query(models.Journal).filter(models.Journal.openalex_issn == issn).first()


# ========== 从 OpenAlex 获取某期刊的最新论文 ==========
def fetch_papers_for_journal(journal: models.Journal, db: Session, max_results: int = 50):
    """
    根据期刊名称或 ISSN 从 OpenAlex 获取最新论文。
    journal: Journal ORM 对象
    """
    if not journal.openalex_issn:
        print(f"[SKIP] 期刊 [{journal.name}] 未设置 ISSN，跳过")
        return 0

    # 用 ISSN 查询 OpenAlex 的 journal 实体
    issn = journal.openalex_issn.replace("-", "")
    url = f"{OPENALEX}/journals/issn:{issn}"
    j_data = _get(url)
    if not j_data or "id" not in j_data:
        print(f"[WARN] 未找到期刊 [{journal.name}] 的 OpenAlex 记录")
        return 0

    openalex_journal_id = j_data["id"]  # 如 https://openalex.org/S123456

    # 查询该 journal 下的论文，按发表日期排序
    papers_url = f"{OPENALEX}/works"
    params = {
        "filter": f"primary_location.source.id:{openalex_journal_id}",
        "sort": "publication_date:desc",
        "per_page": max_results,
        "select": "id,title,authorships,abstract_inverted_index,publication_date,doi,type",
    }
    data = _get(papers_url, params)
    results = data.get("results", [])
    count = 0

    for work in results:
        # 构建作者列表
        authors = []
        for a in work.get("authorships", []):
            if a.get("author", {}).get("display_name"):
                authors.append(a["author"]["display_name"])
        authors_str = ", ".join(authors) if authors else None

        # 将 inverted index 还原为摘要文本
        abstract = _inverted_index_to_text(work.get("abstract_inverted_index"))

        paper_data = {
            "openalex_id": work.get("id", "").replace("https://openalex.org/", ""),
            "journal_id": journal.id,
            "title": work.get("title", "No Title"),
            "authors": authors_str,
            "abstract": abstract,
            "publication_date": work.get("publication_date"),
            "doi": work.get("doi"),
            "url": f"https://doi.org/{work['doi']}" if work.get("doi") else None,
        }

        crud.create_paper(db, paper_data)
        count += 1
        time.sleep(0.1)  # 避免请求过快

    print(f"[OK] 期刊 [{journal.name}] 获取 {count} 篇论文")
    return count


def _inverted_index_to_text(index: dict) -> str:
    """将 OpenAlex 的 inverted_index 还原为可读文本"""
    if not index:
        return ""
    try:
        words = sorted(index.items(), key=lambda x: int(x[1][0]))
        return " ".join(w[0] for w in words)
    except Exception:
        return ""


# ========== 抓取所有活跃期刊的论文 ==========
def fetch_all_journals(db: Session, max_per_journal: int = 50):
    journals = db.query(models.Journal).filter(models.Journal.is_active == True).all()
    total = 0
    for j in journals:
        total += fetch_papers_for_journal(j, db, max_per_journal)
        time.sleep(0.5)
    print(f"\n[完成] 共获取 {total} 篇论文")
    return total


# ========== 命令行入口 ==========
if __name__ == "__main__":
    from .database import SessionLocal, engine
    from . import models
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        fetch_all_journals(db)
    finally:
        db.close()
