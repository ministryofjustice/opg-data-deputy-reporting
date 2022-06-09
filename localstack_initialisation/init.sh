#! /usr/bin/env sh

set -e

awslocal secretsmanager create-secret --name local/jwt-key --secret-string "topsecret" --region eu-west-1

awslocal s3 mb s3://pa-uploads-branch-replication
awslocal s3 cp /tmp/test.pdf s3://pa-uploads-branch-replication/test.pdf

awslocal s3 mb s3://csv-bucket

awslocal sqs create-queue --queue-name csv-sync-queue

#GOOS=linux CGO_ENABLED=0 go build -ldflags "-s -w" -o main ../lambda_functions/v2/functions/csv-sync/main.go

zip main.zip /tmp/main

awslocal lambda create-function --function-name csv-sync --handler main --runtime go1.x --role create-role --zip-file fileb://main.zip

awslocal lambda create-event-source-mapping --function-name csv-sync --batch-size 1 --event-source-arn arn:aws:sqs:eu-west-1:000000000000:csv-sync-queue


awslocal s3api list-buckets

awslocal s3api put-bucket-notification-configuration --bucket csv-bucket --notification-configuration '{ "QueueConfigurations": [{"QueueArn": "arn:aws:sqs:eu-west-1:000000000000:csv-sync-queue","Events": ["s3:ObjectCreated:*"]}]}'
