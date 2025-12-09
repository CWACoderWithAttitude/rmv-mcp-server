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
