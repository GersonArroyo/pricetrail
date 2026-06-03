
run:
	docker compose up -d

scrape:
	docker compose run --rm pricetrail

stop:
	docker compose down

logs:
	docker compose logs -f

install:
	pip install -r requirements.txt

db:
	docker compose up -d postgres

images:
	docker image ls
	
containers:
	docker container ls