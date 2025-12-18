.PHONY: help install migrate run test clean docker docker-up docker-down

help:
	@echo "GymPro - نظام إدارة الصالة الرياضية"
	@echo ""
	@echo "الأوامر المتاحة:"
	@echo "  make install      - تثبيت المتطلبات"
	@echo "  make migrate      - تطبيق الترحيلات"
	@echo "  make run          - تشغيل الخادم"
	@echo "  make test         - تشغيل الاختبارات"
	@echo "  make clean        - حذف الملفات المؤقتة"
	@echo "  make docker       - بناء صورة Docker"
	@echo "  make docker-up    - تشغيل Docker Compose"
	@echo "  make docker-down  - إيقاف Docker Compose"
	@echo ""

install:
	pip install -r requirements.txt

migrate:
	python manage.py migrate

makemigrations:
	python manage.py makemigrations

run:
	python manage.py runserver

superuser:
	python manage.py createsuperuser

test:
	pytest

test-coverage:
	pytest --cov=apps --cov-report=html

lint:
	black apps/ config/
	flake8 apps/ config/

celery-worker:
	celery -A config worker --loglevel=info --pool=solo

celery-beat:
	celery -A config beat --loglevel=info

collectstatic:
	python manage.py collectstatic --noinput

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

docker:
	docker build -t gym-management:latest .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

shell:
	python manage.py shell_plus

format:
	black apps/ config/

lint-check:
	flake8 apps/ config/ --count --select=E9,F63,F7,F82 --show-source --statistics
	black --check apps/ config/

security:
	pip install safety
	safety check

requirements-update:
	pip list --outdated

dump-data:
	python manage.py dumpdata > data.json

load-data:
	python manage.py loaddata data.json

reset-db:
	python manage.py flush --no-input
	python manage.py migrate
	python manage.py createsuperuser
