image_name=rmv_network
#
# Run rmv server in dev mode
# ä
dev_mode:
	uv run fastmcp dev rmv_stdio.py
#
# Run defined tests. Do not swalllow stdio
#
test:
	uv run pytest -s 

#
# Run server in network mode.
#   [Read this before using it besides development](https://gofastmcp.com/deployment/running-server#http-transport-streamable)
#
run_rmv_network:
	uv run rmv_network.py

#
# Run server in stdio mode - for local execution
run_rmv_stdio:
	uv run rmv_stdio.py

# or
run_rmv_stdio_fastmcp:
	uv run fastmcp run main.py
