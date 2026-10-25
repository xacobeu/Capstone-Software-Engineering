#!/bin/sh
# Network installation occurs only with an explicit caller flag.
set -eu
if [ "${1:-}" != '--allow-network' ]; then
  printf '%s\n' 'Usage: sh benchmarks/capstone-performance/src/prepare-build.sh --allow-network' >&2
  exit 2
fi
baseline=85aca163f6c73ac6ce380b5447359146b8adcae4
if [ "$(git rev-parse HEAD)" != "$baseline" ]; then
  printf '%s\n' 'Baseline SHA mismatch; no checkout is changed.' >&2
  exit 1
fi
task_copy=$(mktemp -d /private/tmp/gemini-capstone-build-XXXXXX)
git archive "$baseline" | tar -x -C "$task_copy"
mkdir -p "$task_copy/isolated-home" "$task_copy/isolated-cache"
: > "$task_copy/isolated-home/user.npmrc"
: > "$task_copy/isolated-home/global.npmrc"
export HOME="$task_copy/isolated-home"
export npm_config_cache="$task_copy/isolated-cache"
export npm_config_userconfig="$task_copy/isolated-home/user.npmrc"
export npm_config_globalconfig="$task_copy/isolated-home/global.npmrc"
cd "$task_copy"
npm ci --ignore-scripts --no-audit --no-fund > install.log 2>&1
GIT_COMMIT="$baseline" node scripts/generate-git-commit-info.js > build.log 2>&1
npm run build --workspace @google/gemini-cli-core >> build.log 2>&1
npm run build --workspace @google/gemini-cli-devtools >> build.log 2>&1
npm run build --workspace packages/cli >> build.log 2>&1
printf '%s\n' "$task_copy"
