init-db:
	python database/init_db.py
	alembic upgrade head

start-dashboard:
	python core/dashboard_server/tn_web_dashboard.py

start-register:
	python core/register/tn_ios_register.py

start-cs:
	python core/customer_service/tn_customer_service.py

format-code:
	black .
	flake8 .

lint-check:
	flake8 .

deploy-up:
	docker-compose up -d

deploy-down:
	docker-compose down
