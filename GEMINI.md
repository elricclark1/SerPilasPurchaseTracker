# Serpilas Purchase Tracker

**Project Type:** Python / Streamlit Application
**Primary File:** `app.py`

## Project Overview

"Serpilas Purchase Tracker" is a privacy-first financial dashboard designed to track expenses without a database. It operates in two distinct modes using a single unified codebase:

1.  **Web Mode (Ephemeral):**
    *   **Default behavior.**
    *   Data exists only in RAM.
    *   Users must manually Import/Export CSV files.
    *   Target: Public hosting (e.g., `serpilas.com`).

2.  **Local Mode (Persistent):**
    *   **Activated by:** `PURCHASE_TRACKER_LOCAL=true`.
    *   **Persistence:** Automatically saves transactions to a local CSV.
    *   **Configuration:** Uses `settings.json` to store user preferences (Accent Color, Categories, CSV Path).

## Key Files

*   `app.py`: The main application logic. Contains both Web and Local mode logic, switched via environment variable.
*   `settings.json`: Configuration file for Local Mode (created automatically if missing in Local Mode).
*   `requirements.txt`: Python dependencies (`streamlit`, `pandas`, `plotly`).
*   `deploy.sh`: Deployment script for the remote server.
*   `PROJECT_USERGUIDE.md`: Detailed feature documentation and monetization strategy.
*   `CHANGELOG.txt`: Log of project updates and features.

## Setup & Running

### 1. Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Running in Web Mode (Default)
```bash
streamlit run app.py
```

### 3. Running in Local Mode
To enable persistence and settings:
```bash
export PURCHASE_TRACKER_LOCAL=true
streamlit run app.py
```

## Deployment

**Target Server:** Aylan (`100.99.70.10`)
**URL:** `http://serpilas.com/PurchaseTracker/`

To deploy changes:
1.  Ensure you have SSH access to `aylan`.
2.  Run the deployment script:
    ```bash
    ./deploy.sh
    ```
    *This script creates a tarball of the current directory (excluding venv/git), uploads it to the server, extracts it, and restarts the systemd service.*

## Development Conventions

*   **UI Style:** "HabitKit" aesthetic. Pitch Black (`#000000`) background, high-contrast dark gray cards (`#121212`), and vibrant chart colors.
*   **Data Schema:** 
    *   Columns: `Date`, `Description`, `Amount`, `Necessity`, `Method`, `Category`, `Tag`, `More info`.
    *   **Note:** The legacy `N` (ID) column has been removed. Row management is handled internally by DataFrame index.
*   **Time Filters:** The app supports "Custom Days" lookback in addition to standard presets.
*   **Privacy:** No external database. User owns the CSV file.
