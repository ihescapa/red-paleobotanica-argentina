# Walkthrough: Professional Paleobotany Platform (v4.0)

I have transformed the genealogical tree into a fully-featured **Professional Web Platform** ready for hosting.

## 🌟 Key Features Implemented

### 1. Infrastructure Upgrade (SQLite + Auth)
-   **Database**: Migrated from flat YAML files to **SQLite** (`genealogy.db`). This ensures data integrity and supports complex queries.
-   **Security**: Implemented **user authentication** with hashed passwords. Users must log in to edit data.
-   **Audit Trail**: Every action (Create Node, Link Node) is logged in the database with the user's ID and timestamp.

### 2. "High Design" UI
-   **Aesthetics**: Replaced standard Streamlit components with custom CSS (Serif fonts, minimalist cards, distinct color palette).
-   **Interactive Timeline**: Graph nodes now display **Activity Decades** (e.g., 1966-2014) researched from bibliographies.
-   **Advanced Visualization**: 
    -   Switch between showing only Primary (Thesis) connections or showing Secondary (Co-direction) as dashed lines.

### 3. Research & Data Enrichment
-   **Activity Ranges**: Conducted deep research to find the first and last publications of 15 key researchers (Archangelsky, Volkheimer, Herbst, etc.) and populated this data into the system.
-   **Verified Schools**: Confirmed relationships for Artabe, Brea, Gnaedinger, and Prámparo schools.

### 4. Reliability
-   **Backup System**: Created `backup.py` to auto-snapshot the database daily.

## How to Deploy
1.  Upload the **`genealogia_paleobotanica`** folder to a GitHub repository.
2.  Connect the repository to **Streamlit Community Cloud**.
3.  The system will automatically install dependencies from `requirements.txt`.
4.  Run Command: `streamlit run app.py` (Streamlit does this automatically on the cloud).

> [!TIP]
> **Locally**: Para correrlo ahora, usá:
> `cd genealogia_paleobotanica && streamlit run app.py`
