upload-csv-to-csv-bucket:
	docker compose exec localstack awslocal s3 cp /tmp/testCsv.csv s3://csv-bucket/testCsv.csv