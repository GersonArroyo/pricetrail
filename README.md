
### Project structre

**`api/`** — Jogou os `routers/` pra dentro de um módulo de API completo, com `schemas/` (Pydantic) separados para validação de entrada/saída e `dependencies.py` para injeção de dependências (conexão com DB, auth, etc).

**`scraper/`** ganhou três arquivos novos importantes: `parser.py` (lógica de parsing separada do HTTP), `session.py` (gerencia cookies, headers, rate limiting e retries) e `proxies.py` (rotação de proxies — a Kabum com certeza vai te bloquear sem isso).

**`db/`** ganhou `models.py` (SQLAlchemy ORM) e `repository.py` (padrão repository, que isola as queries do resto do código) e `migrations/` (Alembic, pra não precisar recriar tudo com `init.sql` toda vez).

**`scheduler/`** é a peça que faltava — sem ela o scraper só roda manualmente. Use APScheduler ou Celery Beat. O `jobs.py` define quando rodar cada categoria, o `config.py` define os intervalos.

**`config/`** centraliza settings com Pydantic BaseSettings (lê do `.env` automaticamente) e um `logging.yml` para ter logs estruturados desde o início.

**`tests/`** com `conftest.py` pra fixtures compartilhadas.


## PriceTrail

Web scraper que coleta preços de produtos da Kabum, armazena o histórico ao longo do tempo e expõe os dados via API REST.

## Pré-requisitos

- Docker e Docker Compose
- make (Linux/WSL: `sudo apt install make`)

## Como rodar

```bash
make run        # sobe todos os containers
make scrape     # roda o scraper manualmente
make stop       # derruba os containers
make logs       # acompanha os logs em tempo real
```

Para agendamento automático consulte [scheduler/README.md](scheduler/README.md).

## Estrutura do projeto
/api         — endpoints REST (em desenvolvimento)
/config      — configurações centralizadas e logging
/db          — schema SQL, models e queries
/pipeline    — modelos dbt para transformação de dados
/scheduler   — agendamento do scraper (APScheduler, cron, k8s)
/scraper     — coleta e persistência dos dados da Kabum
/tests       — testes automatizados
Dockerfile        — imagem do scraper
docker-compose.yml — orquestração local
k8s.yml           — manifesto para deploy em Kubernetes
Makefile          — atalhos de comandos
secrets.yml.example — template de secrets para k8s

## Stack

- Python 3.13
- PostgreSQL
- FastAPI + Hypercorn (HTTP/3)
- Docker / Docker Compose
- Kubernetes
- pgAdmin
- dbt (pipeline de transformação)
