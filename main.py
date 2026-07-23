from typing import List, Optional
import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel, HttpUrl

app = FastAPI(
    title="Enterprise Web Crawler API",
    description="Asynchronously crawls web pages and extracts structured text for AI / RAG processing."
)


# --- 1. PYDANTIC SCHEMAS ---

# Outbound Schema: Clean, validated response structure
class WebScrapeResponse(BaseModel):
    success: bool
    url: str
    title: str
    main_heading: Optional[str] = None
    paragraphs: List[str] = []
    total_paragraphs_found: int


# --- 2. FASTAPI CRAWLER ROUTE ---

@app.get(
    "/crawl",
    response_model=WebScrapeResponse,
    status_code=status.HTTP_200_OK,
    summary="Crawl a web page and extract clean text"
)
async def crawl_webpage(
    url: HttpUrl = Query(
        ...,
        description="The target website URL to crawl (must include http:// or https://)",
        example="https://example.com"
    )
):
    url_str = str(url)

    # Set custom headers to mimic a real desktop browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        # 1. Fetch raw HTML asynchronously
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url_str, headers=headers)

        # Handle target server error HTTP status codes
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Target website returned error status code: {response.status_code}"
            )

    except httpx.RequestError as exc:
        # Connection timeouts or DNS resolution failures
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect to the external web host: {str(exc)}"
        )

    # 2. Parse HTML text with BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # 3. Safely extract metadata and text elements
    page_title = (
        soup.title.string.strip()
        if soup.title and soup.title.string
        else "No Title Found"
    )

    # Get first <h1> tag or None
    h1_tag = soup.find("h1")
    main_heading = h1_tag.get_text(strip=True) if h1_tag else None

    # Get all paragraph texts
    all_paragraphs = [
        p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)
    ]

    # 4. Return structured dictionary (FastAPI validates against WebScrapeResponse)
    return {
        "success": True,
        "url": url_str,
        "title": page_title,
        "main_heading": main_heading,
        "paragraphs": all_paragraphs[:5],  # Top 5 paragraphs for brevity
        "total_paragraphs_found": len(all_paragraphs)
    }