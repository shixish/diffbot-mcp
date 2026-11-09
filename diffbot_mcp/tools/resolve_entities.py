from typing import Annotated, Optional

from ..api import request, resolve_token
from ..app import READ_ONLY, mcp

NLP_ENDPOINT = "https://nl.diffbot.com/v1/"

DESCRIPTION = (
    "Finds people, organizations, places, and products mentioned in plain text and links each to a Knowledge "
    "Graph id, with confidence, salience, and sentiment. Use to ground a passage before looking entities up. "
    "The response includes dql_filter, an id:or(...) clause for dql to fetch the full records. Entities with no "
    "id were recognized but not matched. If you already have a name, use search_organizations, search_people, "
    "or search_places instead. Does not return full records. Needs a Diffbot token only when called."
    " API docs: https://www.diffbot.com/docs/natural-language/"
)


def entity_id(entity: dict) -> Optional[str]:
    uri = entity.get("id") or entity.get("diffbotUri") or ""
    return uri.rstrip("/").rsplit("/", 1)[-1] or None


@mcp.tool(name="resolve_entities", title="Resolve Entities", description=DESCRIPTION, annotations=READ_ONLY)
async def resolve_entities(
    text: Annotated[str, "Plain text to analyze"],
    lang: Annotated[Optional[str], "ISO code, e.g. en; default auto"] = None,
) -> dict:
    params = {"token": resolve_token(), "fields": "entities,sentiment"}
    payload = [{"lang": lang or "auto", "format": "plain text", "content": text}]

    data = await request(NLP_ENDPOINT, method="POST", params=params, json_body=payload)
    # the NLP API answers with one result object per submitted document
    if isinstance(data, list):
        data = data[0] if data else {}

    entities = []
    for entity in data.get("entities", []):
        entities.append({
            "name": entity.get("name"),
            "types": [t.get("name") for t in entity.get("allTypes") or [] if t.get("name")],
            "confidence": entity.get("confidence"),
            "salience": entity.get("salience"),
            "sentiment": entity.get("sentiment"),
            "id": entity_id(entity),
            "mentions": len(entity.get("mentions") or []),
        })

    ids = [e["id"] for e in entities if e["id"]]
    return {
        "sentiment": data.get("sentiment"),
        "entities": entities,
        "dql_filter": "id:or(" + ",".join(f'"{i}"' for i in ids) + ")" if ids else None,
    }
