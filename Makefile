run:
	python scraper.py

install:
	pip install -r requirements.txt

db:
	docker-compose up -d postgres

logs:
	docker-compose logs -f