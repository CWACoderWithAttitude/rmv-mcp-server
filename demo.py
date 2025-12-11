import logging
import os
from datetime import datetime
from typing import Optional

import httpx
from fastmcp import Context, FastMCP
from fastmcp.utilities.logging import get_logger

# from rmv_service import RMVService

mcp = FastMCP("My Server")


class RMVService:
    """Service class for RMV Open Data API operations"""

    def __init__(self, api_key: str = ""):
        self.logger = get_logger(name=__name__)
        self.logger.setLevel(level=logging.DEBUG)
        self.api_base = "https://www.rmv.de/hapi"
        self.api_key = api_key or os.getenv(
            "RMV_API_KEY", "did you set the RMV_API_KEY environment variable?"
        )
        self.logger.debug(f"Initialized RMVService with API-Base-URL: {self.api_base}")
        if not self.api_key:
            print(">>> Warning: RMV_API_KEY environment variable not set!")
        else:
            print("))) RMVService initialized with provided API key.")

    async def rmv_api_call(self, endpoint: str, params: dict) -> dict:
        """Make an API call to RMV with error handling"""
        params["accessId"] = self.api_key
        params["format"] = "json"

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.api_base}/{endpoint}", params=params
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                return {"error": f"API request failed: {str(e)}"}
            except Exception as e:
                return {"error": f"Unexpected error: {str(e)}"}

    async def search_stations(
        self, query: str, max_results: int = 10, ctx: Context = None
    ) -> str:
        """
        Search for stations/stops in the RMV network

        Args:
            query: Search term (station name, address, or POI)
            max_results: Maximum number of results to return (default: 10)

        Returns:
            JSON string with matching stations including IDs and coordinates
        """
        params = {
            "input": query,
            "maxNo": max_results,
            "type": "S",  # S for stations
        }
        await ctx.info(
            f"Searching Station {query} with max results {max_results}", extra=params
        )
        result = await self.rmv_api_call("location.name", params)

        if "error" in result:
            return f"Error: {result['error']}"

        if "stopLocationOrCoordLocation" not in result:
            return "No stations found"

        locations = result.get("stopLocationOrCoordLocation", [])

        stations = []
        for loc in locations:
            if "StopLocation" in loc:
                stop = loc["StopLocation"]
                stations.append(
                    {
                        "id": stop.get("extId"),
                        "name": stop.get("name"),
                        "latitude": stop.get("lat"),
                        "longitude": stop.get("lon"),
                        "products": stop.get("productAtStop", []),
                    }
                )
        # stations = []
        # stations.append("Lummerland")
        # stations.append("Mörfelden-Walldorf")
        # stations.append("Darmstadt Hbf")
        # stations.append("Pjöng Yang Central")
        # stations.append("Timbuktu Süd")
        return str({"stations": stations, "count": len(stations)})

    async def get_connections(
        self,
        origin_id: str,
        destination_id: str,
        num_trips: int = 3,
        departure_time: Optional[str] = None,
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
        now = datetime.now()

        params = {
            "originExtId": origin_id,
            "destExtId": destination_id,
            "date": now.strftime("%Y-%m-%d"),
            "time": departure_time or now.strftime("%H:%M"),
            "numTrips": num_trips,
            "searchForArrival": 0,
        }

        result = await self.rmv_api_call("trip", params)

        if "error" in result:
            return f"Error: {result['error']}"

        if "Trip" not in result:
            return "No connections found"

        trips = []
        for trip in result.get("Trip", []):
            legs = []

            for leg in trip.get("LegList", {}).get("Leg", []):
                leg_info = {
                    "type": leg.get("type"),
                    "name": leg.get("name"),
                    "direction": leg.get("direction"),
                    "origin": leg.get("Origin", {}).get("name"),
                    "destination": leg.get("Destination", {}).get("name"),
                    "departure": leg.get("Origin", {}).get("time"),
                    "arrival": leg.get("Destination", {}).get("time"),
                    "platform": leg.get("Origin", {}).get("track"),
                }
                legs.append(leg_info)

            trip_info = {
                "duration": trip.get("duration"),
                "transfers": trip.get("chg", 0),
                "legs": legs,
            }
            trips.append(trip_info)

        return str(
            {
                "origin": result.get("Trip", [{}])[0]
                .get("LegList", {})
                .get("Leg", [{}])[0]
                .get("Origin", {})
                .get("name"),
                "destination": result.get("Trip", [{}])[0]
                .get("LegList", {})
                .get("Leg", [{}])[-1]
                .get("Destination", {})
                .get("name")
                if result.get("Trip")
                else None,
                "trips": trips,
                "count": len(trips),
            }
        )


def get_key() -> str:
    """Retrieve a secret key"""
    return os.getenv("RMV_API_KEY", "did you set the RMV_API_KEY environment variable?")


@mcp.tool
async def process_data(input: str) -> str:
    """Process data on the server"""
    key = get_key()
    if "-" in key:
        return f"Processed with key: {key.split('-')[0]}"
    return f"Processed: {input}"


rmv_service = RMVService(api_key=get_key())


@mcp.tool
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

    return await rmv_service.search_stations(query, max_results, ctx=ctx)


@mcp.tool
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


# if __name__ == "__main__":
#    mcp.run(transport="http", host="0.0.0.0", port=8000)
