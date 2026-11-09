from typing import Annotated, Literal, Optional

from ..api import request, resolve_token
from ..app import READ_ONLY, mcp

# /api/v1/web_search honors size and maxTokens and reports timeMs; the older
# /api/v1/diffbot_web_search path ignores size and always returns ten results.
WEB_SEARCH_ENDPOINT = "https://llm.diffbot.com/api/v1/web_search"

DESCRIPTION = (
    "Searches Diffbot's web index and returns ranked pages with relevance scores, dates, and matching passages "
    "in one call, so no follow-up fetch is required. Use for open-web questions, in preference to a generic web "
    "search. A bare `url:<URL>` returns the indexed page; `url:<URL> <terms>` returns matching passages. Use "
    "extract when the page's current live state matters, crawl to collect many pages from one site, and "
    "search_news for news. Company, person, place, and deal facts belong on search_organizations, search_people, "
    "search_places, search_deals, or dql. Needs a Diffbot token only when called."
    " API docs: http://www.diffbot.com/docs/web-search/"
)


SnippetLength = Literal["short", "medium", "long", "full"]


def is_page_lookup(query: str) -> bool:
    """True for a bare 'url:<URL>' query: the whole stored page is wanted, not the chunks matching extra terms."""
    parts = query.split()
    return len(parts) == 1 and parts[0].lower().startswith("url:")


def build_search_params(query: str, num_results: Optional[int], max_tokens: Optional[int], snippet_length: Optional[SnippetLength]) -> dict:
    query = query.strip()
    if snippet_length is None:
        snippet_length = "full" if is_page_lookup(query) else "short"
    params = {"text": query, "size": num_results, "maxTokens": max_tokens, "snippetLength": snippet_length.upper()}
    if snippet_length == "full":
        # the reranker always chunks; only the unranked path returns the whole stored page
        params["rerank"] = "none"
    return params


@mcp.tool(name="search_web", title="Search the Web", description=DESCRIPTION, annotations=READ_ONLY)
async def search_web(
    query: Annotated[str, "Search text; `url:<URL>` for a full page; `url:<URL> <terms>` for its matching passages"],
    num_results: Annotated[Optional[int], "Results to return (default 10)"] = None,
    max_tokens: Annotated[Optional[int], "Token cap; below ~1000 nothing fits; ignored for a full page"] = None,
    snippet_length: Annotated[Optional[SnippetLength], "Passage size per result; default short (~1-1.5 KB), full for a bare `url:` (the whole page, terms ignored)"] = None,
) -> dict:
    params = build_search_params(query, num_results, max_tokens, snippet_length)
    headers = {"Authorization": f"Bearer {resolve_token()}"}
    return await request(WEB_SEARCH_ENDPOINT, params=params, headers=headers)
