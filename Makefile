
run:
	docker compose up -d

scrape:
	docker compose run --rm pricetrail

stop:
	docker compose down

clean:
	docker compose down -v

logs:
	docker compose logs -f

logs-db:
	docker compose logs -f postgres

logs-scraper:
	docker compose logs -f pricetrail

logs-pgadmin:
	docker compose logs -f pgadmin4

db:
	docker compose up -d postgres

images:
	docker image ls
	
containers:
	docker container ls

build:
	docker compose build --no-cache

pr:
	gh pr create --base main

merge:
	gh pr merge --merge

commit:
	git add . && git commit -m "$(m)"


# always gets the current branch name, if it exists doesnt matter it still works
push:
	git push --set-upstream origin HEAD

install:
	pip install -r requirements.txt