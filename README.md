# Capstone Software Engineering (2026 Group 2)

This project contains all the code used for the Capstone Software Engineering report by Group 2.

## Requirements
* **Python 3.12+**
* **uv**: Python package manager ([See installation instructions](https://docs.astral.sh/uv/getting-started/installation/))

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/xacobeu/Capstone-Software-Engineering.git
   cd Capstone-Software-Engineering
   ```

2. **Sync the workspace:**
   This command automatically creates a synchronized local `.venv/` and installs dependencies.
   ```bash
   uv sync
   ```

## Repository Layout

```
interim/                    code for the interim report
  activities/               activities notebook
  collaboration/            uv run collaboration
  contributors/             uv run contributors
  project_overview/         package diagram (PlantUML source + PNG)
  output/                   generated interim tables and charts
final/                      code for the final report, one folder per section
  project_health/           Section 3: scripts, data/ and figures/
  project_quality/          Section 2: put the quality analysis code here
```

## Running the Interim Modules

| Command |
| :--- |
| `uv run collaboration` |
| `uv run contributors` |

## Running the Project Health Analysis

Run from the repository root; `fetch_*` scripts need `GITHUB_TOKEN` in `.env`. The other scripts work offline on the saved data in `final/project_health/data/`.

| Step | Command |
| :--- | :--- |
| Collect census and sample | `uv run python final/project_health/fetch_data.py` |
| Collect identity data | `uv run python final/project_health/fetch_identity_data.py` |
| Collect PR branch names | `uv run python final/project_health/fetch_branch_names.py` |
| Bot / alias candidates | `uv run python final/project_health/detect_accounts.py` |
| Figures and metric summary | `uv run python final/project_health/generate_figures.py` |
| Qualitative sample dump | `uv run python final/project_health/dump_qualitative_sample.py` |

Account decisions (bots, aliases) live in `final/project_health/account_decisions.json`.

## Adding Project Dependencies

If you need to add a library (e.g., `pandas`, `numpy`), use the built-in `uv add` utility.

```bash
# For example:
uv add pandas
```

## Contributors
- Miguel F. Lebrun Ceno (2111152)
- Valērijs Višķers (2154765)
- Hyunseung Jeon (2123355)
