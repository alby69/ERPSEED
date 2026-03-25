.PHONY: help build up down logs restart init clean ps

help: ## Mostra questo aiuto
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

# Development
up: ## Avvia tutti i servizi (dev mode con volumes)
	docker-compose up -d
	@echo "✅ Servizi avviati!"
	@echo "   Backend: http://localhost:5000"
	@echo "   Frontend: http://localhost:5173"
	@echo "   Swagger: http://localhost:5000/swagger-ui"

down: ## Ferma tutti i servizi
	docker-compose down

build: ## Build delle immagini Docker
	docker-compose build

logs: ## Mostra i log
	docker-compose logs -f

logs-backend: ## Mostra i log del backend
	docker-compose logs -f backend

restart: down up ## Riavvia tutti i servizi

ps: ## Mostra i servizi attivi
	docker-compose ps

# Database
init: ## Inizializza il database con i seed
	docker-compose run --rm init-db
	@echo "✅ Database inizializzato!"

db-reset: ## Reset completo del database
	docker-compose down -v
	docker-compose up -d db
	sleep 3
	docker-compose run --rm init-db
	@echo "✅ Database resettato!"

# Cleanup
clean: ## Rimuovi container, volumi e immagini non usate
	docker-compose down -v --rmi local
	docker system prune -f

# Production
prod-build: ## Build per produzione
	docker build -t erpseed-backend .

prod-run: ## Avvia in produzione
	docker run -d -p 5000:5000 \
		-e DATABASE_URL=postgresql://user:pass@host:5432/erpseed \
		-e JWT_SECRET_KEY=your-secret-key \
		erpseed-backend

# Debug
shell-backend: ## Accedi al shell del backend
	docker-compose exec backend /bin/bash

db-shell: ## Accedi al database PostgreSQL
	docker-compose exec db psql -U postgres -d erpseed

# Testing
test: ## Esegui i test
	docker-compose exec backend pytest

# Utils
status: ## Mostra status dei servizi
	@echo "=== Container ==="
	@docker-compose ps
	@echo ""
	@echo "=== Immagini ==="
	@docker images | grep erpseed
