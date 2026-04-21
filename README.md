# CineBase - Cinematic Movie Database

CineBase is a modern web application for exploring a massive dataset of over 10,000 movies. It features a cinematic User Interface built with Flask and a modular database architecture supporting both remote MSSQL and local SQLite backends.

## 🚀 Getting Started

### Prerequisites
- Python 3.x
- Virtual Environment (`venv`)

### Installation & Setup
1. **Initialize the Environment**:
   ```bash
   cd project
   python -m venv venv
   source venv/bin/activate
   pip install flask pymssql  # pymssql is optional for local mode
   ```

2. **Setup Local Database**:
   If you don't have access to the university lab server, you can initialize a local SQLite database from the included dataset:
   ```bash
   make setup
   ```

3. **Run the Application**:
   ```bash
   make
   ```
   Access the UI at: **http://127.0.0.1:5001**

---

## 📂 Project Structure

- **`app.py`**: Main Flask application and API routes.
- **`db_module.py`**: Database factory that intelligently selects the connection type.
- **`config/`**: Contains `auth.cfg` for database credentials.
- **`data/`**: Stores the raw `data.csv` and the local `cinebase.db`.
- **`db/`**: Modular source code for different database implementations (MSSQL, SQLite).
- **`sql/`**: Schema definitions and raw SQL scripts.
- **`scripts/`**: Maintenance tools for data ingestion and database setup.
- **`static/` & `templates/`**: Frontend assets (CSS, JS, HTML).

---

## 🛠 Database Configuration

You can manually switch between database backends by editing **`config/auth.cfg`**:

- **For SQLite (Local)**:
  `db_type=sqlite`
- **For MSSQL (Remote Lab)**:
  `db_type=mssql`

If no `db_type` is specified, the application will automatically prefer SQLite if `data/cinebase.db` is present.

---

## 📊 Features
- **Dynamic Search**: Find movies by title, actor, or director.
- **Advanced Analytics**: Compare revenue by actor, ratings by director, and movie trends over decades.
- **Cinematic UI**: Dark-mode interface with glassmorphism and smooth transitions.
- **Dual Connection**: Seamlessly switch between local development and production lab environments.
