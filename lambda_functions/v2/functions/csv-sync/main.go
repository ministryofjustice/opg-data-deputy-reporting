package main

import (
	"context"
	"encoding/json"
	"fmt"
	"github.com/aws/aws-sdk-go/service/s3"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go/aws/session"
)

type EventRecord struct {
	S3 struct {
		Bucket struct {
			Name string `json:"name"`
		} `json:"bucket"`
		Object struct {
			Key string `json:"key"`
		} `json:"object"`
	} `json:"s3"`
}

type ObjectCreatedEvent struct {
	Records []EventRecord `json:"Records"`
}

func logCsv(ctx context.Context, sqsEvent events.SQSEvent) error {
	for _, message := range sqsEvent.Records {

		event := ObjectCreatedEvent{}
		json.Unmarshal([]byte(message.Body), &event)
		fmt.Println(event)

		//Get file from S3
		// Post to digideps
	}

	return nil
}

func main() {
	sess := session.Must(session.NewSession())
	s3 := s3.New(sess)

	lambda.Start(logCsv)
}

//{
//  "Records": [
//    {
//      "eventVersion": "2.1",
//      "eventSource": "aws:s3",
//      "awsRegion": "eu-west-1",
//      "eventTime": "2022-06-10T12:05:51.201Z",
//      "eventName": "ObjectCreated:Put",
//      "userIdentity": {
//        "principalId": "AIDAJDPLRKLG7UEXAMPLE"
//      },
//      "requestParameters": {
//        "sourceIPAddress": "127.0.0.1"
//      },
//      "responseElements": {
//        "x-amz-request-id": "6e0a2b39",
//        "x-amz-id-2": "eftixk72aD6Ap51TnqcoF8eFidJG9Z/2"
//      },
//      "s3": {
//        "s3SchemaVersion": "1.0",
//        "configurationId": "testConfigRule",
//        "bucket": {
//          "name": "csv-bucket",
//          "ownerIdentity": {
//            "principalId": "A3NL1KOZZKExample"
//          },
//          "arn": "arn:aws:s3:::csv-bucket"
//        },
//        "object": {
//          "key": "test.pdf",
//          "size": 4911,
//          "eTag": "\"1c32d785398e3a7eaab0e9b876903cc6\"",
//          "versionId": null,
//          "sequencer": "0055AED6DCD90281E5"
//        }
//      }
//    }
//  ]
//}
