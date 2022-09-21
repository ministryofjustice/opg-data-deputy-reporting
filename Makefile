upload-csv-to-csv-bucket:
	docker-compose exec localstack awslocal s3 cp /tmp/testCsv.csv s3://csv-bucket/testCsv.csv

rebuild-csv-copier:
	docker-compose build --no-cache localstack csv-copier-function && docker-compose up -d localstack csv-copier-function