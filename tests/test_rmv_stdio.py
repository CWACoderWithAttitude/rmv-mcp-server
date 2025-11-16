#
# https://apidog.com/blog/fastmcp/
#
import json
from operator import contains
import re
import pytest
import asyncio
from fastmcp.client import Client


@pytest.fixture
def client():
    return Client("rmv_stdio.py")

@pytest.mark.asyncio
async def test_initialize_client(client):
    assert client.name is not None
    #assert client.tools == {}

@pytest.mark.asyncio
async def test_client_exposes_tools(client):
    async with client:
#        # https://gofastmcp.com/clients/tools
        tools = await client.list_tools()
        assert len(tools) == 2
        assert tools[0].name == "search_stations"
        assert tools[1].name == "get_connections"

@pytest.mark.asyncio
#@pytest.mark.skip(reason="Requires RMV API key and network access")
async def test_search_station_dortweil(client):
    async with client:
#        pass
        # https://gofastmcp.com/clients/tools
        
        result = await client.call_tool("search_stations", {"query": "Dortweil", "max_results": 1})
        
        # result -> CallToolResult with structured and unstructured data
        # Access structured data (automatically deserialized)
        assert(result.data) is not None
        data = result.data
        import json
        json_acceptable_string = data.replace("'", "\"")
        d = json.loads(json_acceptable_string)
        
        stations = d["stations"]
        assert (stations) is not None
        assert len(stations) >= 1
        for station in stations:
            assert "Bad Vilbel-Dortelweil Bf" in station["name"]
            assert "id" in station
            assert "latitude" in station
            assert "longitude" in station