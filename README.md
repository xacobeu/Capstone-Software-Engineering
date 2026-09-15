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

## Running the Sub-Modules

Each component in the `src/` directory can be executed using `uv run`:

| Command | 
| :--- |
| `uv run collaboration` |
| `uv run activities` | 
| `uv run code_analysis` |
| `uv run contributors` |
| `uv run design_and_architecture` | 
| `uv run documentation_analysis` |
| `uv run project_overview` |
| `uv run quality_attributes` |

## Adding Project Dependencies

If you need to add a library (e.g., `pandas`, `numpy`), use the built-in `uv add` utility.

```bash
# For example:
uv add pandas
```