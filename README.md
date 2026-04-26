<<<<<<< HEAD
### Project structre

**`api/`** — Jogou os `routers/` pra dentro de um módulo de API completo, com `schemas/` (Pydantic) separados para validação de entrada/saída e `dependencies.py` para injeção de dependências (conexão com DB, auth, etc).

**`scraper/`** ganhou três arquivos novos importantes: `parser.py` (lógica de parsing separada do HTTP), `session.py` (gerencia cookies, headers, rate limiting e retries) e `proxies.py` (rotação de proxies — a Kabum com certeza vai te bloquear sem isso).

**`db/`** ganhou `models.py` (SQLAlchemy ORM) e `repository.py` (padrão repository, que isola as queries do resto do código) e `migrations/` (Alembic, pra não precisar recriar tudo com `init.sql` toda vez).

**`scheduler/`** é a peça que faltava — sem ela o scraper só roda manualmente. Use APScheduler ou Celery Beat. O `jobs.py` define quando rodar cada categoria, o `config.py` define os intervalos.

**`config/`** centraliza settings com Pydantic BaseSettings (lê do `.env` automaticamente) e um `logging.yml` para ter logs estruturados desde o início.

**`tests/`** com `conftest.py` pra fixtures compartilhadas.

**`Makefile`** na raiz — pequeno mas faz diferença enorme no dia a dia: `make scrape`, `make api`, `make test`, `make migrate`.

The `example.json` is how the json file cames from de url we get our response
=======
# pricetrail
Kabum price trail
>>>>>>> origin/main
