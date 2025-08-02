from fastapi import APIRouter, Query
import requests
from bs4 import BeautifulSoup

router = APIRouter()

@router.get("/api/history")
def get_place_history(place: str = Query(..., min_length=2)):
    try:
        # 1. Search Wikipedia
        search_url = f"https://en.wikipedia.org/w/api.php"
        search_params = {
            "action": "query",
            "list": "search",
            "srsearch": place,
            "format": "json"
        }
        res = requests.get(search_url, params=search_params).json()
        page_title = res["query"]["search"][0]["title"]

        # 2. Get page extract
        extract_url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + page_title
        summary = requests.get(extract_url).json()

        return {
            "title": summary.get("title"),
            "description": summary.get("extract"),
            "image": summary.get("thumbnail", {}).get("source", None),
            "url": summary.get("content_urls", {}).get("desktop", {}).get("page", "")
        }

    except Exception as e:
        return {"error": str(e), "message": "No history found."}
