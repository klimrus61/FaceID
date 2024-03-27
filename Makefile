# ============================================VARIABLES===========================================

compose_directory = docker/compose
docker_v2 = docker compose

main_container = -f $(compose_directory)/main.yaml
app_container = -f $(compose_directory)/app.yaml
db_container = -f $(compose_directory)/db.yaml
migrations_container = -f $(compose_directory)/migrations.yaml
tests_container = -f $(compose_directory)/tests.yaml


capture_exit_code = --abort-on-container-exit --exit-code-from
#exit_code_population = db_population
exit_code_migrations = db_migrations
exit_code_tests = tests


compose_application := $(docker_v2) $(main_container) $(db_container) $(app_container) --env-file .env
compose_migrations := $(docker_v2) $(main_container) $(db_container) $(migrations_container) --env-file .env
compose_tests := $(docker_v2) $(main_container) $(db_container) $(tests_container) --env-file .env


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
	#$(compose_population) down

.PHONY: restart
restart:
	$(compose_application) stop
	$(compose_application) up

.PHONY: logs
logs:
	$(compose_application) logs -f

.PHONY: destroy
destroy:
	$(compose_application) down -v
	$(compose_migrations) down -v
	$(compose_population) down -v
#	$(compose_tests) down -v
#	$(con)


.PHONY: prune
prune:
	docker system prune --all --force --volumes

# ===================================DOCKER(MANAGE APPLICATION)===================================

# ========================================DOCKER(MIGRATIONS)======================================

.PHONY: migrations
migrations:
	$(compose_migrations) up $(capture_exit_code) $(exit_code_migrations)

# ========================================DOCKER(MIGRATIONS)======================================

# ==========================================DOCKER(TESTS)=========================================

.PHONY: build-tests
build-tests:
	$(compose_tests) build

.PHONY: tests
tests:
	$(compose_tests) up $(capture_exit_code) $(exit_code_tests)

# ==========================================DOCKER(TESTS)=========================================
