#! /usr/bin/env sh

set -e

awslocal secretsmanager create-secret --name local/jwt-key --secret-string "topsecret" --region eu-west-1

awslocal s3 mb s3://pa-uploads-branch-replication
awslocal s3 cp /tmp/test.pdf s3://pa-uploads-branch-replication/test.pdf