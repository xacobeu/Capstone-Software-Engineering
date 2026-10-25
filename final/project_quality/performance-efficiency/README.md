# Gemini CLI performance reproduction

Pinned upstream commit: `85aca163f6c73ac6ce380b5447359146b8adcae4`.
Use Node 24.10.0, npm 11.6.0 and the recorded macOS arm64 environment
(Apple M1, 16 GiB, macOS 26.6.2). Other hosts are unvalidated.
The complete pinned upstream checkout supplies all CLI source, workspace
manifests and npm dependencies; install from its `package-lock.json`.

## Existing results and nine figures

From this package root, use Python 3.9.7 with `requirements-figures.txt`.
Its pins describe the environment that reproduced all nine PNGs byte-for-byte;
fresh installation of these pins is untested. An existing matching Python can
be used instead of creating a virtual environment.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-figures.txt
mkdir -p .work/mpl .work/cache
export MPLCONFIGDIR="$PWD/.work/mpl"
export XDG_CACHE_HOME="$PWD/.work/cache"
export PYTHONDONTWRITEBYTECODE=1
.venv/bin/python -B benchmarks/capstone-performance/analysis/scripts/plot_clt_report.py --output .work/figures
.venv/bin/python -B benchmarks/capstone-performance/analysis/scripts/plot_clt_file_count_report.py --output .work/figures
.venv/bin/python -B benchmarks/capstone-performance/analysis/scripts/plot_startup_report.py --output .work/figures
.venv/bin/python -B benchmarks/capstone-performance/analysis/scripts/plot_rss_report.py --output .work/figures
```

Start with a nonexistent `.work/figures` directory. The four unchanged plotters
produce nine PNGs plus PDF/SVG exports. `plot_clt_report.py` supplies shared
utilities and fixed source paths. They plot the retained reported summaries,
not arbitrary fresh runs. Keep generated outputs outside the 18-file publication
inventory; `.work/` and `.venv/` are local scratch directories.

Recompute all 42 primary metric distributions and their bootstrap intervals
from the retained complete raw datasets and compare them with the summaries:

```sh
node --input-type=module <<'JS'
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {stats} from './benchmarks/capstone-performance/src/common.mjs';
const base='benchmarks/capstone-performance/results/';
const runs=['integrated-full','context-size-extension-v2/full-2026-10-14T00-15-51.571Z-gKVrD3'];
let count=0;
for(const run of runs){
 const rows=fs.readFileSync(base+run+'/raw.jsonl','utf8').trim().split('\n').map(JSON.parse);
 const summary=JSON.parse(fs.readFileSync(base+run+'/summary.json','utf8'));
 for(const s of summary){
  const measured=rows.filter(r=>r.stage==='measured'&&r.scenario===s.scenario);
  assert.equal(measured.length,30);
  assert.ok(measured.every(r=>r.status==='ok'));
  for(const metric of ['contextMs','spawnToReadyMs','peakRSSMiB']){
   assert.deepEqual(stats(measured.map(r=>r[metric])),s[metric]);count++;
  }
 }
}
console.log('Verified '+count+' primary metric distributions.');
JS
node benchmarks/capstone-performance/analysis/context-size-extension/analyze.mjs benchmarks/capstone-performance/results/context-size-extension-v2/full-2026-10-14T00-15-51.571Z-gKVrD3 .work/extension-analysis
```

The analysis output directory must not exist; create its parent first if running
the analysis independently. The extension analyzer regenerates tables and joint
complete-block bootstrap comparisons; it uses retained `summary.json` and
`raw.jsonl`, importing `common.mjs`. Retained raw data includes warmups and original
observer trials, while primary distributions use measured rows only.

## Build and generate new measurements

Setup requires network for clone/npm ci. Equivalent individual installation/build
commands succeeded historically; the supplied wrapper implements that sequence.
Current package validation is reported separately, with each executed build or
probe distinguished from historical evidence. No full benchmark rerun is claimed.

```sh
CAPSTONE_PACKAGE="$PWD"
CAPSTONE_WORK=$(mktemp -d /private/tmp/capstone-reproduction-XXXXXX)
git clone https://github.com/google-gemini/gemini-cli.git "$CAPSTONE_WORK/original"
git -C "$CAPSTONE_WORK/original" checkout --detach 85aca163f6c73ac6ce380b5447359146b8adcae4
git clone https://github.com/google-gemini/gemini-cli.git "$CAPSTONE_WORK/extension"
git -C "$CAPSTONE_WORK/extension" checkout --detach 85aca163f6c73ac6ce380b5447359146b8adcae4
mkdir -p "$CAPSTONE_WORK/original/benchmarks/capstone-performance/src"
mkdir -p "$CAPSTONE_WORK/extension/benchmarks/capstone-performance/src"
cp "$CAPSTONE_PACKAGE/benchmarks/capstone-performance/src/common.mjs" "$CAPSTONE_PACKAGE/benchmarks/capstone-performance/src/integrated-preload.mjs" "$CAPSTONE_WORK/original/benchmarks/capstone-performance/src/"
cp "$CAPSTONE_PACKAGE/original/src/integrated-run.mjs" "$CAPSTONE_WORK/original/benchmarks/capstone-performance/src/"
cp "$CAPSTONE_PACKAGE/benchmarks/capstone-performance/src/"*.mjs "$CAPSTONE_WORK/extension/benchmarks/capstone-performance/src/"
CAPSTONE_BUILD=$(cd "$CAPSTONE_WORK/original" && sh "$CAPSTONE_PACKAGE/tools/prepare-build.sh" --allow-network)
cd "$CAPSTONE_WORK/original"
node benchmarks/capstone-performance/src/integrated-run.mjs --build "$CAPSTONE_BUILD" --pilot --probe
node benchmarks/capstone-performance/src/integrated-run.mjs --build "$CAPSTONE_BUILD" --pilot
node benchmarks/capstone-performance/src/integrated-run.mjs --build "$CAPSTONE_BUILD" --full
cd "$CAPSTONE_WORK/extension"
node benchmarks/capstone-performance/src/integrated-run.mjs --build "$CAPSTONE_BUILD" --context-size-extension --pilot --probe
node benchmarks/capstone-performance/src/integrated-run.mjs --build "$CAPSTONE_BUILD" --context-size-extension --pilot
node benchmarks/capstone-performance/src/integrated-run.mjs --build "$CAPSTONE_BUILD" --context-size-extension --full
```

Use fresh clean pinned checkouts. Shared common/preload modules are byte-identical
between historical experiments and are copied unchanged beside each driver.
Do not commit overlays: both drivers require the upstream HEAD and compare every
tracked file against the build archive. Run serially and inspect probe/pilot
failures and resource use before proceeding. To perform only a small probe, run
only each command ending in `--pilot --probe`; this selects two processes per
experiment, no warmups, and no full measurement blocks.

Save each complete printed `Results:` directory permanently: original output is
temporary; extension output is under its separate checkout. Do not overwrite
retained publication data. The build helper prints its fresh build path and keeps
`install.log`/`build.log` there; failed attempts also retain their logs under their
new `/private/tmp/gemini-capstone-build-*` directory.

Drivers generate workloads, isolated settings/homes, empty fake-response input,
raw JSONL/CSV, manifests and statistical summaries. No real key is required.
Settings and the environment whitelist are embedded in the drivers. Network/model
guards, no relaunch, disabled telemetry/usage statistics/MCP/extensions/hooks and
post-measurement validation remain unchanged. Build order is core, devtools, CLI;
the helper uses `npm ci --ignore-scripts --no-audit --no-fund` and `GIT_COMMIT`
metadata generation in a disposable archive. It never installs in the source checkout.

## Definitions and limits

Original workloads: zero control; 1/4/16/32 files at 64 KiB total; four files at
4/16/64/256 KiB. Extension: four fixed-position files at 64/256 KiB and 1/4/16 MiB.
Both use deterministic no-import ASCII and a 33-directory chain.

CLT (`contextMs`) brackets awaited original refresh inside Config initialization.
Startup (`spawnToReadyMs`) is parent spawn to verified Config/chat readiness on fd3.
Peak RSS (`peakRSSMiB`) is actual CLI PID lifetime high-water through that boundary,
before validation/inference. It is not refresh-only memory or authenticated UI
startup. File count covaries with placement/framing; 16 MiB is synthetic stress.

Seed 250102023; five warmup and 30 measured complete blocks; serial fresh processes;
30-second timeout; median, interpolated P90, IQR/MAD, range, mean/sample SD and
2,000-resample bootstrap median intervals. Original adds 20 observer pairs;
extension adds none. No filtering or session pooling. Filesystem cache and host
load are uncontrolled; total instrumentation overhead remains unquantified.
Published raw JSONL contains the complete accepted original and extension records
with path-prefix sanitization documented below. Summary JSON and historical code
are unchanged. Generated figures, temporary inputs and verification logs are not
prerequisites for the 18-file package.

## Validation on 25 October 2026

The supplied build wrapper completed a fresh isolated locked installation and
core/devtools/CLI build with Node 24.10.0 and npm 11.6.0. Both historical drivers
then passed their two-process probes: original zero-context and four-file/64-KiB
conditions; extension 64-KiB and 16-MiB conditions. All four processes passed
readiness/content validation, with no recorded network/model attempts. An initial
installation attempt failed on registry DNS access; the network-enabled retry
succeeded. No pilot or full benchmark was rerun, and probe timings are not report
estimates. The 42 retained primary metric distributions matched, extension tables
and comparisons reproduced exactly, and all nine PNGs matched report images
byte-for-byte. All original evidence and historical modules remained unchanged.
Fresh pip installation and portability to other host environments remain untested.

## Publication privacy: sanitized data copies

The two `raw.jsonl` files in this package are explicitly labeled **sanitized
publication derivatives**, not byte-identical copies of the original evidence.
The original experimental datasets remain unchanged outside this package.
Sanitization changes only string path prefixes. No records, fields or array
elements were removed or reordered; all numeric values, timings, memory values,
statistics, statuses, scenario/block identifiers and timestamps are unchanged.
Byte substitution preserves the original JSON formatting and numeric lexemes.

Three prefixes were replaced consistently, preserving relative suffixes, path
relationships, file names, directory depth and per-process `home-N` identities:

| Original prefix meaning | Publication placeholder | How the original prefix is derived |
|---|---|---|
| Personal source checkout | `<REPO_ROOT>` | `command[2]` minus `/benchmarks/capstone-performance/src/integrated-preload.mjs` |
| Original experiment temporary workspace | `<ORIGINAL_RUN_ROOT>` | Original dataset `env.TMPDIR` |
| Extension temporary workspace | `<EXTENSION_RUN_ROOT>` | Extension dataset `env.TMPDIR` |
| Shared disposable compiled build | `<BUILD_ROOT>` | `command[3]` minus `/packages/cli/dist/index.js` |

The checkout path revealed a local username and directory organization. The macOS
temporary root contained a per-user directory token. Random temporary build/run
names are otherwise harmless; normalizing them also removes machine fingerprints.
The generic Node executable `/opt/homebrew/Cellar/node/24.10.0/bin/node` and
`env.PATH=/usr/bin:/bin:/opt/homebrew/bin` remain unchanged: they disclose the
runtime/platform layout, not a username. Process IDs, timestamps and host-load
observations remain for experimental auditability. The recorded API-key value is
the synthetic, nonsecret `synthetic-not-a-real-key`.

Exact modified JSON locations and counts of changed string values:

| JSON location | Meaning | Original | Extension |
|---|---|---:|---:|
| `command[2]` | Instrumentation module | 355 | 175 |
| `command[3]` | Compiled CLI entry | 355 | 175 |
| `command[7]` | Empty fake-response input | 355 | 175 |
| `cwd` | Generated leaf workspace | 355 | 175 |
| `env.CAPSTONE_MANIFEST` | Fixture manifest | 355 | 175 |
| `env.HOME` | Isolated trial home | 355 | 175 |
| `env.GEMINI_CLI_HOME` | Isolated CLI home | 355 | 175 |
| `env.GEMINI_CLI_SYSTEM_SETTINGS_PATH` | Absent isolated system settings | 355 | 175 |
| `env.GEMINI_CLI_SYSTEM_DEFAULTS_PATH` | Absent isolated defaults | 355 | 175 |
| `env.GIT_CONFIG_GLOBAL` | Absent isolated Git config | 355 | 175 |
| `env.TMPDIR` | Generated run root | 355 | 175 |
| `events[0].loadedPaths[*]` | Loaded synthetic context files | 2,575 | 700 |
| `events[0].patched[*]` | Observed compiled modules | 1,065 | 525 |
| **Total changed strings** | | **7,545** | **3,150** |

The only remaining absolute-path locations in either dataset are `command[0]`
(the generic Node executable) and `env.PATH`. Placeholders are provenance labels,
not executable paths. No path-bearing field is read by primary-statistics
recomputation, the extension comparison analyzer or figure generation. Those
operations use numeric observations and scenario/stage/block/status fields or
the unchanged summaries. During new measurements, the unchanged drivers create
real paths/manifests and validate them normally; they do not read these historical
rows. Do not replay sanitized command arrays literally.

All 355 original and 175 extension records remain. Source and publication SHA-256
hashes identify the derivatives without disclosing original personal prefixes:

```text
Original experiment raw.jsonl:
  source:      a12b754cedf4ae55d086f8777c4b3da1bdc552cad408958da3bd36a3e732ee2e
  publication: 505a635c10d096f11d3c9255008248198fae6db87e782114b279684e4ef5a186
Extension experiment raw.jsonl:
  source:      9a4d1339f4cfde4de7dfa0ef90310afe15a2a53924e95f0eed2919ba027c0fa5
  publication: eeb62250dd18cd423d47cf9ab0049b5710d6d792f202cdd2c6d0ffc73c5cfeeb
```

The substitutions can be reproduced from each original by deriving the three
prefixes above and replacing their literal UTF-8 occurrences with the documented
placeholders. The original run root and build root are distinct from the checkout
root. Recompute hashes after substitution; do not reserialize JSON if byte-identical
publication output is required. No additional sanitization transformations apply.
