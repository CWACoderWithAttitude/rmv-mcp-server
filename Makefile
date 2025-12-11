#
# Run rmv server in dev mode
# 
dev_mode:
	uv run fastmcp dev rmv_stdio.py

#
# https://gofastmcp.com/deployment/fastmcp-cloud#prerequisites
#
inspect:
	uv run fastmcp inspect rmv_stdio.py
run_stream:
	uv run fastmcp run demo.py --transport streamable-http
run_stdio:
	uv run fastmcp run demo.py

uv2pip:
	# uv pip freeze > requirements.txt
	uv pip compile pyproject.toml -o requirements.txt
