package main

import (
	"bytes"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/aws/aws-sdk-go/service/s3/s3iface"
	"io"
	"net/http"
	"os"
)

type Lambda struct {
	s3Client       s3iface.S3API
	digidepsClient DigidepsClient
}

type DigidepsClient interface {
	Post(url, contentType string, body io.Reader) (resp *http.Response, err error)
}

func (l *Lambda) HandleEvent(event events.SQSEvent) error {
	url := os.Getenv("DIGIDEPS_API_ENDPOINT")

	if url == "" {
		return errors.New("DIGIDEPS_API_ENDPOINT environment variable not set")
	}

	input := s3.GetObjectInput{}
	parsedEvent, err := SQSMessageParsing(event)

	if err != nil {
		return errors.New(fmt.Sprintf("Unable to parse SQS Message: %s", err.Error()))
	}

	input.Bucket = aws.String(parsedEvent.S3.Bucket.Name)
	input.Key = aws.String(parsedEvent.S3.Object.Key)

	resp, _ := l.s3Client.GetObject(&input)

	defer resp.Body.Close()
	buf := new(bytes.Buffer)
	_, err = buf.ReadFrom(resp.Body)

	if err != nil {
		panic(err)
	}

	csvContents := buf.String()

	encodedCSV := base64.StdEncoding.EncodeToString([]byte(csvContents))
	postBody, _ := json.Marshal(map[string]string{
		"csv": encodedCSV,
	})
	requestBody := bytes.NewBuffer(postBody)

	_, _ = l.digidepsClient.Post(url, "application/json", requestBody)

	return nil
}

type S3EventRecord struct {
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
	S3EventRecords []S3EventRecord `json:"Records"`
}

type CSV struct {
	CSV string
}

func SQSMessageParsing(sqsEvent events.SQSEvent) (S3EventRecord, error) {
	if len(sqsEvent.Records) == 0 {
		return S3EventRecord{}, errors.New("no SQS event records")
	}

	event := ObjectCreatedEvent{}
	err := json.Unmarshal([]byte(sqsEvent.Records[0].Body), &event)

	if err != nil {
		return S3EventRecord{}, err
	}

	if len(event.S3EventRecords) == 0 {
		return S3EventRecord{}, errors.New("no S3 event records")
	}

	return event.S3EventRecords[0], nil
}

func HandleEvent(sqsEvent events.SQSEvent) (string, error) {

	//event := ObjectCreatedEvent{}
	//err := json.Unmarshal([]byte(sqsEvent.Records[0].Body), &event)
	//fmt.Println(event)
	//
	//if err != nil {
	//	log.Fatalln(err)
	//}
	//
	//sess := session.Must(session.NewSession())
	//
	//endpoint := os.Getenv("AWS_S3_ENDPOINT")
	//sess.Config.Endpoint = &endpoint
	//sess.Config.S3ForcePathStyle = aws.Bool(true)
	//
	//s3client := s3.New(sess)
	//
	//input := s3.GetObjectInput{Bucket: aws.String(event.S3EventRecords[0].S3.Bucket.Name), Key: aws.String(event.S3EventRecords[0].S3.Object.Key)}
	//
	//resp, err := s3client.GetObject(&input)
	//if err != nil {
	//	panic(err)
	//}
	//
	//defer resp.Body.Close()
	//buf := new(bytes.Buffer)
	//_, err = buf.ReadFrom(resp.Body)
	//
	//if err != nil {
	//	panic(err)
	//}
	//
	//csvContents := buf.String()
	//
	//fmt.Println(csvContents)
	//
	//sEnc := base64.StdEncoding.EncodeToString([]byte(csvContents))
	//fmt.Println(sEnc)
	//
	//// Post to digideps
	//postBody, _ := json.Marshal(map[string]string{
	//	"csv": csvContents,
	//})

	//responseBody := bytes.NewBuffer(postBody)
	//
	//digidepsEndpoint := os.Getenv("DIGIDEPS_API_ENDPOINT")
	//
	////Leverage Go's HTTP Post function to make request
	//ddResp, err := http.Post(digidepsEndpoint, "application/json", responseBody)
	//
	////Handle Error
	//if err != nil {
	//	log.Fatalf("An Error Occured %v", err)
	//}
	//
	////defer ddResp.Body.Close()
	////
	////ddBuf := new(bytes.Buffer)
	////_, err = ddBuf.ReadFrom(ddResp.Body)
	////
	////if err != nil {
	////	panic(err)
	////}
	//
	//fmt.Println(ddResp)

	return "Yay", errors.New("Boo")
}

func main() {
	lambda.Start(HandleEvent)
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
