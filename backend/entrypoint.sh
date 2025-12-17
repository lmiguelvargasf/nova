#!/bin/sh
set -e
uv run piccolo migrations forward all
exec uv run litestar run --host 0.0.0.0
