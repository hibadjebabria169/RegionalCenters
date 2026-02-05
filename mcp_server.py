"""MCP Server that connects Claude to the Sports Centers API."""
import json
import urllib.request
from mcp.server.fastmcp import FastMCP

API_BASE = "https://regionalcenters.onrender.com"

mcp = FastMCP("Sports Centers")


def api_call(endpoint: str) -> dict:
    """Make a call to the Sports Centers API."""
    url = f"{API_BASE}{endpoint}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


@mcp.tool()
def search_centers(query: str) -> str:
    """Search sports and health centers by keyword (name, description, or discipline)."""
    data = api_call(f"/search?q={query}")
    return json.dumps(data, ensure_ascii=False, indent=2)


@mcp.tool()
def get_all_centers(limit: int = 100, offset: int = 0) -> str:
    """Get all sports and health centers with optional pagination."""
    data = api_call(f"/centers?limit={limit}&offset={offset}")
    return json.dumps(data, ensure_ascii=False, indent=2)


@mcp.tool()
def get_center_by_id(center_id: str) -> str:
    """Get details of a specific center by its ID."""
    data = api_call(f"/centers/{center_id}")
    return json.dumps(data, ensure_ascii=False, indent=2)


@mcp.tool()
def find_by_discipline(discipline: str) -> str:
    """Find centers offering a specific sport/discipline (e.g., Tennis, Basket, Natation, Karaté)."""
    data = api_call(f"/discipline?name={discipline}")
    return json.dumps(data, ensure_ascii=False, indent=2)


@mcp.tool()
def find_by_pathology(pathology: str) -> str:
    """Find centers that handle a specific health condition (e.g., Cancer, diabète, cardiovasculaires)."""
    data = api_call(f"/pathology?name={pathology}")
    return json.dumps(data, ensure_ascii=False, indent=2)


@mcp.tool()
def find_nearby(lat: float, lng: float, radius_km: float = 50) -> str:
    """Find centers within a given radius of a location. Returns results sorted by distance."""
    data = api_call(f"/nearby?lat={lat}&lng={lng}&radius_km={radius_km}")
    return json.dumps(data, ensure_ascii=False, indent=2)


@mcp.tool()
def list_disciplines() -> str:
    """List all available sports/disciplines across all centers."""
    data = api_call("/disciplines")
    return json.dumps(data, ensure_ascii=False, indent=2)


@mcp.tool()
def list_pathologies() -> str:
    """List all health conditions/pathologies handled by centers."""
    data = api_call("/pathologies")
    return json.dumps(data, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.run()
