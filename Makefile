upload-csv-to-csv-bucket:
	docker compose exec localstack awslocal s3 cp /tmp/testCsv.csv s3://csv-bucket/testCsv.csv

unit-tests:
	docker compose up unit-tests

build:
	docker compose build deputy-reporting-lambda localstack mock-sirius

up:
	docker compose up -d deputy-reporting-lambda

down:
	docker compose down