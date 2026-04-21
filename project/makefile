run:
	@echo "Checking for local database..."
	@if [ ! -f data/cinebase.db ]; then \
		echo "Initializing local SQLite database..."; \
		source venv/bin/activate && python scripts/setup_local_db.py; \
	fi
	@echo "Starting CineBase Web Application..."
	@source venv/bin/activate && python app.py

setup:
	@echo "Initializing local SQLite database..."
	@source venv/bin/activate && python scripts/setup_local_db.py