# Project Goals & Monetization Strategy

## Current Architecture: Unified Codebase
We have merged the Web and Local versions into a single `app.py` that adapts its behavior based on the environment.

### 1. Web Version (Hosted)
- **Target Audience:** New users, mobile users, and quick demonstrations.
- **Data Privacy:** **Ephemeral.** Data exists only in RAM. Refreshing the page wipes the session.
- **Storage:** Users must manually **Import** their CSV at the start and **Export** it before leaving.
- **Settings:** No persistence. Theme/Settings reset on refresh.
- **Configuration:** Defaults to `IS_LOCAL_MODE = False`.

### 2. Local Version (Open Source / Downloadable)
- **Target Audience:** Power users, privacy advocates, and desktop users.
- **Persistence:** **Permanent.** The app automatically creates and manages a CSV file (default: `purchase_history.csv`).
- **Configuration:**
    - Controlled by setting `PURCHASE_TRACKER_LOCAL=true` in environment variables.
    - **Settings.json:** Stores user preferences like `accent_color`, `csv_path`, and custom categories/methods.
- **Convenience:** 
    - **Auto-Load:** Starts immediately with user data.
    - **Auto-Save:** Transactions are written to disk instantly.

## Long-term Vision
The end goal is to evolve this "Purchase Tracker" from a local-only tool into a premium, hosted SaaS product.

## Monetization Model
- **Premium Subscription (Small Fee):** Users pay to create an account.
- **Key Features:**
    - **Cloud Sync:** Data stored securely on the server, syncing across multiple devices (desktop, mobile).
    - **Hosting:** No need for users to manage CSV files manually; data is hosted by the service.

## Community & Perks (Patreon-style)
- **Discord Access:** Subscribers gain access to a private Discord server for the creator's channel and projects.
- **Direct Support:**
    - Priority troubleshooting.
    - Direct channel for feature requests and feedback.
