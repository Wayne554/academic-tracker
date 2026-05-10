from fastapi import APIRouter, HTTPException
import httpx
import logging
import time

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/search")
async def search_journals(query: str, limit: int = 10):
    """
    通过 OpenAlex API 搜索期刊
    """
    start_time = time.time()
    try:
        logger.info(f"收到搜索请求: query={query}, limit={limit}")
        
        # OpenAlex API 端点
        url = "https://api.openalex.org/sources"
        params = {
            "search": query,
            "filter": "type:journal",
            "per_page": limit
        }
        
        logger.info(f"请求 OpenAlex API: {url}")
        logger.info(f"参数: {params}")
        
        api_start = time.time()
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        api_end = time.time()
        logger.info(f"OpenAlex API 调用耗时: {api_end - api_start:.2f}秒")
        
        logger.info(f"OpenAlex API 返回结果数: {len(data.get('results', []))}")
        
        # 转换结果格式
        journals = []
        for result in data.get("results", []):
            openalex_id = result.get("id", "").replace("https://openalex.org/", "")
            journals.append({
                "openalex_id": openalex_id,
                "name": result.get("display_name", ""),
                "issn": result.get("issn", []),
                "publisher": result.get("publisher", ""),
                "works_count": result.get("works_count", 0),
                "cited_by_count": result.get("cited_by_count", 0),
                "homepage_url": result.get("homepage_url", ""),
                "url": f"https://doi.org/{openalex_id}"
            })
        
        total_time = time.time() - start_time
        logger.info(f"返回 {len(journals)} 个期刊，总耗时: {total_time:.2f}秒")
        
        return {
            "success": True,
            "count": len(journals),
            "journals": journals
        }
    
    except httpx.HTTPError as e:
        logger.error(f"OpenAlex API HTTP 错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OpenAlex API 错误: {str(e)}")
    except Exception as e:
        logger.error(f"搜索失败: {str(e)}")
        import traceback
        logger.error(f"详细错误:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/{journal_id}")
async def get_journal_by_id(journal_id: str):
    """
    通过 OpenAlex ID 获取期刊详细信息
    支持 Source ID (S前缀) 和 Work ID (W前缀)
    """
    try:
        logger.info(f"请求期刊详情: journal_id={journal_id}")
        
        # 判断 ID 类型
        if journal_id.upper().startswith('W'):
            # Work ID - 先获取论文信息，再获取期刊信息
            logger.info(f"检测到 Work ID，先获取论文信息")
            work_url = f"https://api.openalex.org/works/{journal_id}"
            async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                work_response = await client.get(work_url)
                work_response.raise_for_status()
                work_data = work_response.json()
            
            # 从论文信息中提取期刊 ID
            source_id = None
            if work_data.get("primary_location") and work_data["primary_location"].get("source"):
                source_id = work_data["primary_location"]["source"]["id"]
            
            if not source_id:
                raise HTTPException(status_code=404, detail="该论文没有关联的期刊信息")
            
            logger.info(f"从论文中提取到期刊 ID: {source_id}")
            journal_id = source_id.replace("https://openalex.org/", "")
        
        # 获取期刊详细信息
        url = f"https://api.openalex.org/sources/{journal_id}"
        
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            result = response.json()
        
        # 安全地处理 URL
        openalex_id = result.get("id", "").replace("https://openalex.org/", "")
        journal = {
            "openalex_id": openalex_id,
            "name": result.get("display_name", ""),
            "issn": result.get("issn", []),
            "publisher": result.get("publisher", ""),
            "works_count": result.get("works_count", 0),
            "cited_by_count": result.get("cited_by_count", 0),
            "homepage_url": result.get("homepage_url", ""),
            "country": result.get("country_code", ""),
            "type": result.get("type", ""),
            "is_oa": result.get("is_oa", False),
            "url": f"https://doi.org/{openalex_id}"
        }
        
        logger.info(f"返回期刊: {journal['name']}")
        
        return {
            "success": True,
            "journal": journal
        }
    
    except httpx.HTTPError as e:
        logger.error(f"OpenAlex API HTTP 错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OpenAlex API 错误: {str(e)}")
    except Exception as e:
        logger.error(f"获取期刊信息失败: {str(e)}")
        import traceback
        logger.error(f"详细错误:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"获取期刊信息失败: {str(e)}")
