"""
RMV Open Data MCP Server
Provides access to RMV (Rhein-Main-Verkehrsverbund) public transport data
"""

import os
from typing import Optional

from fastmcp import Context, FastMCP

from rmv_service import RMVService

# Initialize FastMCP server
mcp = FastMCP("RMV Transit Info")
print(f">>> mcp: {mcp}")
api_key: str = os.getenv(
    "RMV_API_KEY", "did you set the RMV_API_KEY environment variable?"
)
# Initialize RMV service
rmv_service = RMVService(api_key=api_key)


@mcp.tool()
async def search_stations(
    query: str, max_results: int = 10, ctx: Optional[Context] = None
) -> str:
    """
    Search for stations/stops in the RMV network

    Args:
        query: Search term (station name, address, or POI)
        max_results: Maximum number of results to return (default: 10)

    Returns:
        JSON string with matching stations including IDs and coordinates
    """
    # Log a message to the client if context is available
    if ctx:
        await ctx.info(f"Searching station {query}...")

    return await rmv_service.search_stations(query, max_results)


@mcp.tool()
async def get_connections(
    origin_id: str,
    destination_id: str,
    num_trips: int = 3,
    departure_time: str = None,
    ctx: Optional[Context] = None,
) -> str:
    """
    Get journey connections between two stations

    Args:
        origin_id: RMV station ID of origin (use search_stations)
        destination_id: RMV station ID of destination
        num_trips: Number of trip options to return (default: 3)
        departure_time: Departure time in HH:MM format (default: now)

    Returns:
        JSON string with journey options including transfers and duration
    """

    if ctx:
        await ctx.info(f"Searching Connection from {origin_id} to {destination_id}...")
    return await rmv_service.get_connections(
        origin_id, destination_id, num_trips, departure_time
    )


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
