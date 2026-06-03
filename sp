#!/usr/bin/env bash
# Thin wrapper around `python3 -m safe_planner`
# Allows running Safe-Planner from anywhere: ./sp <DOMAIN> <PROBLEM> [...]

set -e

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="${REPO_ROOT}/src${PYTHONPATH:+:${PYTHONPATH}}"
exec python3 -m safe_planner "$@"