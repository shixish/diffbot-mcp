from typing import Annotated, Literal, Optional

from ..app import READ_ONLY, mcp
from ..dql import run

DESCRIPTION = (
    "Runs one raw DQL query against the Diffbot Knowledge Graph. Use for entity types and shapes the typed tools "
    "do not cover: products, patents, job posts, facet aggregations, cross-entity queries, or an id filter from "
    "resolve_entities. Use search_organizations, search_people, search_news, search_places, or search_deals when "
    "they can express the question, and search_web or extract for page text. Each typed tool returns the DQL it "
    "ran, which can be refined here. Conditions on one nested object go inside one {} block, e.g. "
    "employments.{employer.name:X isCurrent:true}. Confirm field paths and taxonomy spellings with dql_ontology; "
    "an unknown path is silently ignored. Check hit counts with dql_probe before pulling rows. Do not add a sort "
    "unless ordering is the question. For a CSV file, do not page rows through this tool: GET "
    "https://kg.diffbot.com/kg/v3/dql?token=..&format=csv&size=<hits>&exportspec=<fields>&query=<DQL>. "
    "Needs a Diffbot token only when called."
    " API docs: https://www.diffbot.com/docs/dql/"
)


@mcp.tool(name="dql", title="Run DQL Query", description=DESCRIPTION, annotations=READ_ONLY)
async def dql(
    query: Annotated[str, "DQL starting with type:X. Unknown field paths are silently ignored. Co-constrain one nested object inside {}"],
    size: Annotated[int, "Max rows or buckets"] = 10,
    offset: Annotated[int, "Rows to skip"] = 0,
    fields: Annotated[Optional[str], "CSV columns as 'path,Label;path,Label'; default per entity type"] = None,
    format: Annotated[Literal["csv", "json"], "'json' for full records; add get:a,b to query to limit"] = "csv",
    hits_only: Annotated[bool, "True: hit count only, no rows. To compare several queries, use dql_probe"] = False,
) -> dict:
    return await run(query, size=size, offset=offset, fields=fields, format=format, hits_only=hits_only)
