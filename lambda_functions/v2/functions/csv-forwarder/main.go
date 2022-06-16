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
	"github.com/aws/aws-sdk-go/aws/session"
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

func (l *Lambda) HandleEvent(event events.SQSEvent) (string, error) {
	url := os.Getenv("DIGIDEPS_API_ENDPOINT")

	if url == "" {
		return "", errors.New("DIGIDEPS_API_ENDPOINT environment variable not set")
	}

	input := s3.GetObjectInput{}
	parsedEvent, err := SQSMessageParser(event)

	if err != nil {
		return "", errors.New(fmt.Sprintf("Unable to parse SQS Message: %s", err.Error()))
	}

	input.Bucket = aws.String(parsedEvent.S3.Bucket.Name)
	input.Key = aws.String(parsedEvent.S3.Object.Key)

	resp, _ := l.s3Client.GetObject(&input)

	defer resp.Body.Close()
	buf := new(bytes.Buffer)
	_, err = buf.ReadFrom(resp.Body)

	if err != nil {
		return "", errors.New(fmt.Sprintf("Unable to read file from S3: %s", err.Error()))
	}

	csvContents := buf.String()

	encodedCSV := base64.StdEncoding.EncodeToString([]byte(csvContents))
	postBody, err := json.Marshal(map[string]string{
		"csv": encodedCSV,
	})

	if err != nil {
		return "", errors.New(fmt.Sprintf("Unable to marshal string to JSON: %s", err.Error()))
	}

	requestBody := bytes.NewBuffer(postBody)

	response, err := l.digidepsClient.Post(url, "application/json", requestBody)

	if err != nil {
		return "", errors.New(fmt.Sprintf("Unable to post to Digideps: %s", err.Error()))
	}

	if response.StatusCode != 202 {
		return "", errors.New(fmt.Sprintf(
			`Received unexpected status code from Digideps: %d
			Response Body: %s`, response.StatusCode, response.Body))
	}

	return "Successfully POSTed CSV", nil
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

func SQSMessageParser(sqsEvent events.SQSEvent) (S3EventRecord, error) {
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

func InitLambda(sess *session.Session) Lambda {
	newSession := session.Must(session.NewSession())
	return Lambda{
		s3Client:       s3.New(newSession),
		digidepsClient: &http.Client{},
	}
}

func main() {

	l := Lambda{
		s3Client:       nil,
		digidepsClient: nil,
	}

	lambda.Start(l.HandleEvent)
}
