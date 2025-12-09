import os
from encodings import undefined

from fastmcp import FastMCP

mcp = FastMCP("My Server")

key = undefined


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


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
