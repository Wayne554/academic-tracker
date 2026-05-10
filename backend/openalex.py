from fastapi import APIRouter, HTTPException
import httpx

router = APIRouter()

@router.get("/search")
async def search_journals(query: str, limit: int = 10):
    """
    通过 OpenAlex API 搜索期刊
    """
    try:
        # OpenAlex API 端点
        url = "https://api.openalex.org/sources"
        params = {
            "search": query,
            "filter": "type:journal",
            "per_page": limit,
            "select": "id,display_name,issn,works_count,cited_by_count,homepage_url,publisher"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()
        
        # 转换结果格式
        journals = []
        for result in data.get("results", []):
            journal = {
                "openalex_id": result.get("id", "").replace("https://openalex.org/", ""),
                "name": result.get("display_name", ""),
                "issn": result.get("issn", []),
                "publisher": result.get("publisher", ""),
                "works_count": result.get("works_count", 0),
                "cited_by_count": result.get("cited_by_count", 0),
                "homepage_url": result.get("homepage_url", ""),
                "url": f"https://doi.org/{result.get('id', '').replace('https://openalex.org/', '')}"
            }
            journals.append(journal)
        
        return {
            "success": True,
            "count": len(journals),
            "journals": journals
        }
    
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"OpenAlex API 错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")

@router.get("/{journal_id}")
async def get_journal_by_id(journal_id: str):
    """
    通过 OpenAlex ID 获取期刊详细信息
    """
    try:
        url = f"https://api.openalex.org/sources/{journal_id}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            result = response.json()
        
        journal = {
            "openalex_id": result.get("id", "").replace("https://openalex.org/", ""),
            "name": result.get("display_name", ""),
            "issn": result.get("issn", []),
            "publisher": result.get("publisher", ""),
            "works_count": result.get("works_count", 0),
            "cited_by_count": result.get("cited_by_count", 0),
            "homepage_url": result.get("homepage_url", ""),
            "country": result.get("country_code", ""),
            "type": result.get("type", ""),
            "is_oa": result.get("is_oa", False),
            "url": f"https://doi.org/{result.get('id', '').replace('https://openalex.org/', '')}"
        }
        
        return {
            "success": True,
            "journal": journal
        }
    
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"OpenAlex API 错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取期刊信息失败: {str(e)}")
