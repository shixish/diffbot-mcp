from typing import Annotated, List

from ..app import READ_ONLY, mcp
from ..dql import probe

DESCRIPTION = (
    "Returns hit counts for several DQL queries at once, and no rows. Use to compare variants before dql: a {} "
    "block versus loose clauses, or category versus descriptors. Zero hits means a bad value (check "
    "dql_ontology). A count equal to the unfiltered type:X count means a field path was ignored. Do not probe "
    "similarTo, and never probe an unfiltered type:Article. For one query's rows, use dql. Needs a Diffbot token "
    "only when called."
    " API docs: https://docs.diffbot.com/docs/dql-quickstart"
)


@mcp.tool(name="dql_probe", title="Probe DQL Hit Counts", description=DESCRIPTION, annotations=READ_ONLY)
async def dql_probe(
    queries: Annotated[List[str], "DQL queries, each starting with type:X"],
) -> dict:
    return {"results": await probe(queries)}
