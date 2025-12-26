#!/usr/bin/env bash

set -euo pipefail

# Stop any running containers before rebuilding the frontend.
docker compose down

pushd frontend >/dev/null
npm install
npm run build
popd >/dev/null

docker compose up -d
