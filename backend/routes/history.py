# from fastapi import APIRouter, Query
# import requests
# from bs4 import BeautifulSoup

# router = APIRouter()

# @router.get("/api/history")
# def get_place_history(place: str = Query(..., min_length=2)):
#     try:
#         # 1. Search Wikipedia
#         search_url = f"https://en.wikipedia.org/w/api.php"
#         search_params = {
#             "action": "query",
#             "list": "search",
#             "srsearch": place,
#             "format": "json"
#         }
#         res = requests.get(search_url, params=search_params).json()
#         page_title = res["query"]["search"][0]["title"]

#         # 2. Get page extract
#         extract_url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + page_title
#         summary = requests.get(extract_url).json()

#         return {
#             "title": summary.get("title"),
#             "description": summary.get("extract"),
#             "image": summary.get("thumbnail", {}).get("source", None),
#             "url": summary.get("content_urls", {}).get("desktop", {}).get("page", "")
#         }

#     except Exception as e:
#         return {"error": str(e), "message": "No history found."}

from fastapi import APIRouter, Query
import requests
from urllib.parse import quote

router = APIRouter()

@router.get("/api/history")
def get_place_history(place: str = Query(..., min_length=2)):
    try:
        print("PLACE INPUTTED:", place)
        search_url = "https://en.wikipedia.org/w/api.php"
        search_params = {
            "action": "query",
            "list": "search",
            "srsearch": place,
            "format": "json",
            "origin": "*"
        }
        headers = {
            "User-Agent": "MyGeoApp/1.0 (test@example.com)"
        }
        search_resp = requests.get(search_url, params=search_params, headers=headers)
        print("WIKI SEARCH STATUS:", search_resp.status_code)
        res = search_resp.json()
        print("WIKI SEARCH RAW:", res)
        search_results = res.get("query", {}).get("search", [])
        print("WIKI SEARCH RESULTS:", search_results)
        if not search_results:
            return {"error": "No page found.", "message": "No history found."}
        
        page_title = search_results[0]["title"]
        print("PAGE TITLE:", page_title)
        page_title_encoded = quote(page_title)
        extract_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_title_encoded}"
        summary_resp = requests.get(extract_url, headers=headers)
        print("WIKI SUMMARY STATUS:", summary_resp.status_code)
        summary = summary_resp.json()
        print("WIKI SUMMARY RAW:", summary)
        return {
            "title": summary.get("title"),
            "description": summary.get("extract"),
            "image": summary.get("thumbnail", {}).get("source", None),
            "url": summary.get("content_urls", {}).get("desktop", {}).get("page", "")
        }
    except Exception as e:
        print("EXCEPTION:", e)
        return {"error": str(e), "message": "No history found."}
