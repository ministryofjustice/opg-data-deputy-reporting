package main

import (
	"errors"
	"fmt"
	"github.com/aws/aws-lambda-go/events"
	"github.com/stretchr/testify/assert"
	"testing"
)

func TestSQSMessageParsing(t *testing.T) {
	//Parse the event
	t.Run("Parse incoming SQS Message into an EventRecord", func(t *testing.T) {
		sqsEvent := generateValidSQSEvent("csv-bucket", "test.csv")

		actual, _ := SQSMessageParsing(sqsEvent)

		expected := EventRecord{}

		expected.S3.Bucket.Name = "csv-bucket"
		expected.S3.Object.Key = "test.csv"

		assert.Equal(t, expected, actual)
	})

	//Parse the event
	t.Run("Parse incoming SQS Message into an EventRecord", func(t *testing.T) {
		sqsEvent := generateValidSQSEvent("pdf-bucket", "test.pdf")

		actual, _ := SQSMessageParsing(sqsEvent)

		expected := EventRecord{}

		expected.S3.Bucket.Name = "pdf-bucket"
		expected.S3.Object.Key = "test.pdf"

		assert.Equal(t, actual, expected)
	})

	t.Run("Returns error when parsing invalid JSON", func(t *testing.T) {
		sqsEvent := generateInvalidSQSEvent("{Invalid JSON}")

		_, err := SQSMessageParsing(sqsEvent)

		assert.Error(t, err)
	})

	t.Run("Returns error when there are no records", func(t *testing.T) {
		sqsEvent := generateInvalidSQSEvent(`{"Records":[]}`)

		_, err := SQSMessageParsing(sqsEvent)

		assert.Error(t, err)
	})
}

func generateValidSQSEvent(bucketName string, objectKey string) events.SQSEvent {
	sqsMessageBody := `{
		  "Records":[
		     {
		        "eventVersion":"2.1",
		        "eventSource":"aws:s3",
		        "awsRegion":"eu-west-1",
		        "eventTime":"2022-06-10T12:05:51.201Z",
		        "eventName":"ObjectCreated:Put",
		        "userIdentity":{
		           "principalId":"AIDAJDPLRKLG7UEXAMPLE"
		        },
		        "requestParameters":{
		           "sourceIPAddress":"127.0.0.1"
		        },
		        "responseElements":{
		           "x-amz-request-id":"6e0a2b39",
		           "x-amz-id-2":"eftixk72aD6Ap51TnqcoF8eFidJG9Z/2"
		        },
		        "s3":{
		           "s3SchemaVersion":"1.0",
		           "configurationId":"testConfigRule",
		           "bucket":{
		              "name":"%s",
		              "ownerIdentity":{
		                 "principalId":"A3NL1KOZZKExample"
		              },
		              "arn":"arn:aws:s3:::csv-bucket"
		           },
		           "object":{
		              "key":"%s",
		              "size":4911,
		              "eTag":"\"1c32d785398e3a7eaab0e9b876903cc6\"",
		              "versionId":null,
		              "sequencer":"0055AED6DCD90281E5"
		           }
		        }
		     }
		  ]
		}`

	sqsMessageBody = fmt.Sprintf(sqsMessageBody, bucketName, objectKey)

	sqsMessage := events.SQSMessage{
		MessageId:              "",
		ReceiptHandle:          "",
		Body:                   sqsMessageBody,
		Md5OfBody:              "",
		Md5OfMessageAttributes: "",
		Attributes:             nil,
		MessageAttributes:      nil,
		EventSourceARN:         "",
		EventSource:            "",
		AWSRegion:              "",
	}

	records := []events.SQSMessage{sqsMessage}
	sqsEvent := events.SQSEvent{Records: records}
	return sqsEvent
}

func generateInvalidSQSEvent(sqsMessageBody string) events.SQSEvent {
	sqsMessage := events.SQSMessage{
		MessageId:              "",
		ReceiptHandle:          "",
		Body:                   sqsMessageBody,
		Md5OfBody:              "",
		Md5OfMessageAttributes: "",
		Attributes:             nil,
		MessageAttributes:      nil,
		EventSourceARN:         "",
		EventSource:            "",
		AWSRegion:              "",
	}

	records := []events.SQSMessage{sqsMessage}
	sqsEvent := events.SQSEvent{Records: records}
	return sqsEvent
}

func TestHandleEvent(t *testing.T) {
	t.Run("Returns feedback when the function runs successfully", func(t *testing.T) {

		var records []events.SQSMessage
		sqsEvent := events.SQSEvent{Records: records}

		response, _ := HandleEvent(sqsEvent)
		expected := "Yay"
		assert.Equal(t, response, expected)
	})

	t.Run("Throws an error when the function runs unsuccessfully", func(t *testing.T) {

		var records []events.SQSMessage
		sqsEvent := events.SQSEvent{Records: records}

		_, err := HandleEvent(sqsEvent)
		expectedError := errors.New("Boo")

		assert.Equal(t, expectedError, err)
	})

	//Request to s3 endpoint is valid (testing env variable)

	//Valid input to s3 request

	//Test the csv is base64 encoded

	//Request to digideps endpoint is valid (testing env variable)

	//Test valid string response is returned
	//	sqsMessageBody := `{
	//   "Records":[
	//      {
	//         "eventVersion":"2.1",
	//         "eventSource":"aws:s3",
	//         "awsRegion":"eu-west-1",
	//         "eventTime":"2022-06-10T12:05:51.201Z",
	//         "eventName":"ObjectCreated:Put",
	//         "userIdentity":{
	//            "principalId":"AIDAJDPLRKLG7UEXAMPLE"
	//         },
	//         "requestParameters":{
	//            "sourceIPAddress":"127.0.0.1"
	//         },
	//         "responseElements":{
	//            "x-amz-request-id":"6e0a2b39",
	//            "x-amz-id-2":"eftixk72aD6Ap51TnqcoF8eFidJG9Z/2"
	//         },
	//         "s3":{
	//            "s3SchemaVersion":"1.0",
	//            "configurationId":"testConfigRule",
	//            "bucket":{
	//               "name":"csv-bucket",
	//               "ownerIdentity":{
	//                  "principalId":"A3NL1KOZZKExample"
	//               },
	//               "arn":"arn:aws:s3:::csv-bucket"
	//            },
	//            "object":{
	//               "key":"test.pdf",
	//               "size":4911,
	//               "eTag":"\"1c32d785398e3a7eaab0e9b876903cc6\"",
	//               "versionId":null,
	//               "sequencer":"0055AED6DCD90281E5"
	//            }
	//         }
	//      }
	//   ]
	//}`
	//
	//	sqsMessage := events.SQSMessage{
	//		MessageId:              "",
	//		ReceiptHandle:          "",
	//		Body:                   sqsMessageBody,
	//		Md5OfBody:              "",
	//		Md5OfMessageAttributes: "",
	//		Attributes:             nil,
	//		MessageAttributes:      nil,
	//		EventSourceARN:         "",
	//		EventSource:            "",
	//		AWSRegion:              "",
	//	}
	//
	//	records := []events.SQSMessage{sqsMessage}
	//	sqsEvent := events.SQSEvent{Records: records}
	//	response := HandleEvent(sqsEvent)

}
