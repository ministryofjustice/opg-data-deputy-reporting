#! /usr/bin/env sh

set -e

awslocal secretsmanager create-secret --name local/jwt-key --secret-string "topsecret" --region eu-west-1

awslocal s3 mb s3://pa-uploads-branch-replication
awslocal s3 cp /tmp/test.pdf s3://pa-uploads-branch-replication/test.pdf

awslocal s3 mb s3://csv-bucket

awslocal s3api put-bucket-policy \
    --policy '{ "Statement": [ { "Sid": "DenyUnEncryptedObjectUploads", "Effect": "Deny", "Principal": { "AWS": "*" }, "Action": "s3:PutObject", "Resource": "arn:aws:s3:::csv-bucket/*", "Condition":  { "StringNotEquals": { "s3:x-amz-server-side-encryption": "AES256" } } }, { "Sid": "DenyUnEncryptedObjectUploads", "Effect": "Deny", "Principal": { "AWS": "*" }, "Action": "s3:PutObject", "Resource": "arn:aws:s3:::csv-bucket/*", "Condition":  { "Bool": { "aws:SecureTransport": false } } } ] }' \
    --bucket "csv-bucket"

awslocal sqs create-queue --queue-name csv-sync-queue

#awslocal ecr create-repository --repository-name csv-upload-trigger
#$existing_repository_uri=$(awslocal ecr describe-repositories --repository-names csv-upload-trigger --query "repositories[0].repositoryUri" --output text)



# function name must be 'function' due to localstack weirdness
awslocal lambda create-function \
          --function-name function \
          --code ImageUri=csv-forwarder-function:latest \
          --role arn:aws:iam::000000000:role/lambda-ex \

awslocal lambda create-event-source-mapping \
         --function-name function \
         --batch-size 1 \
         --event-source-arn arn:aws:sqs:eu-west-1:000000000000:csv-sync-queue

awslocal s3api put-bucket-notification-configuration \
         --bucket csv-bucket \
         --notification-configuration '{ "QueueConfigurations": [{"QueueArn": "arn:aws:sqs:eu-west-1:000000000000:csv-sync-queue","Events": ["s3:ObjectCreated:*"]}]}'

#awslocal s3 cp /tmp/test.pdf s3://csv-bucket/test.pdf

