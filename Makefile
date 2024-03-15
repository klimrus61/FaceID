# ============================================VARIABLES===========================================

compose_directory = docker/compose
docker_v2 = docker compose

main_container = -f $(compose_directory)/main.yaml
app_container = -f $(compose_directory)/app.yaml
db_container = -f $(compose_directory)/db.yaml

compose_application := $(docker_v2) $(main_container) $(db_container) $(app_container) --env-file .env

# ============================================VARIABLES===========================================


# ===================================DOCKER(MANAGE APPLICATION)===================================

.PHONY: build
build:
	$(compose_application) build

.PHONY: app
app:
	$(compose_application) up

.PHONY: down
down:
	$(compose_application) down
	$(compose_population) down

.PHONY: restart
restart:
	$(compose_application) stop
	$(compose_application) up

.PHONY: logs
logs:
	$(compose_application) logs -f

.PHONY: prune
prune:
	docker system prune --all --force --volumes



# ===================================DOCKER(MANAGE APPLICATION)===================================

