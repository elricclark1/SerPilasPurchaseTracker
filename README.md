# Purchase Tracker

A self-hosted, local-first financial dashboard built with Python and Streamlit. This application allows you to track expenses, visualize spending habits, and manage your budget without external servers or databases.

## Prerequisites

- **Python 3.8+** installed on your system.
- **Linux** (or any OS that supports Python/Streamlit).

## Setup & Installation

The project uses a Python virtual environment to manage dependencies.

1.  **Navigate to the project directory:**
    ```bash
    cd /home/elric/purchase-tracker
    ```

2.  **Create a virtual environment (if not already present):**
    ```bash
    python3 -m venv .venv
    ```

3.  **Activate the virtual environment:**
    ```bash
    source .venv/bin/activate
    ```

4.  **Install dependencies:**
    ```bash
    pip install streamlit pandas plotly
    ```

## How to Run

There are two ways to start the application.

### Option 1: Activate Environment First (Recommended)
This is standard practice for Python development.

```bash
cd /home/elric/purchase-tracker
source .venv/bin/activate
streamlit run app.py
```

### Option 2: Direct Execution
You can run the Streamlit executable directly from the virtual environment without activating it globally in your shell.

```bash
cd /home/elric/purchase-tracker
./.venv/bin/streamlit run app.py
```

## Features

- **Data Management:** Upload your existing CSV history or start fresh. Export data at any time.
- **Manage History:** View your full transaction log and delete entries as needed.
- **Mobile-Friendly:** Responsive UI for logging transactions on the go.
- **Analytics:** Visualize spending by category, monthly trends, and necessity.
- **Privacy:** All data is processed locally in your browser session.

## Data Schema

The app expects (and creates) a CSV with the following columns:
`N`, `Date`, `Description`, `Amount`, `Necessity`, `Method`, `Category`, `Tag`, `More info`
