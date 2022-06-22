package main

import (
	"bytes"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strings"

    "github.com/aws/aws-lambda-go/events"
    "github.com/aws/aws-lambda-go/lambda"
    "github.com/aws/aws-sdk-go/aws"
    "github.com/aws/aws-sdk-go/aws/session"
    "github.com/aws/aws-sdk-go/service/s3"
    "github.com/aws/aws-sdk-go/service/s3/s3iface"
)

type Lambda struct {
	s3Client       s3iface.S3API
	digidepsClient DigidepsClient
}

type DigidepsClient interface {
	Post(url, contentType string, body io.Reader) (resp *http.Response, err error)
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

func (l *Lambda) HandleEvent(event events.SQSEvent) (string, error) {
	url := os.Getenv("DIGIDEPS_API_ENDPOINT")

	if url == "" {
		msg := "DIGIDEPS_API_ENDPOINT environment variable not set"
		log.Print(msg)
		return "", errors.New(msg)
	}

	input := s3.GetObjectInput{}
	parsedEvent, err := SQSMessageParser(event)

	if err != nil {
		msg := fmt.Sprintf("unable to parse sqs message: %s", err.Error())
		log.Print(msg)
		return "", errors.New(msg)
	}

	input.Bucket = aws.String(parsedEvent.S3.Bucket.Name)
	input.Key = aws.String(parsedEvent.S3.Object.Key)

	resp, _ := l.s3Client.GetObject(&input)

	defer resp.Body.Close()
	buf := new(bytes.Buffer)
	_, err = buf.ReadFrom(resp.Body)

	if err != nil {
		msg := fmt.Sprintf("unable to read file from s3: %s", err.Error())
		log.Print(msg)
		return "", errors.New(msg)
	}

	csvContents := buf.String()

	encodedCSV := base64.StdEncoding.EncodeToString([]byte(csvContents))
	postBody, err := json.Marshal(map[string]string{
		"csv": encodedCSV,
	})

	if err != nil {
		msg := fmt.Sprintf("unable to marshal string to json: %s", err.Error())
		log.Print(msg)
		return "", errors.New(msg)
	}

	requestBody := bytes.NewBuffer(postBody)

	response, err := l.digidepsClient.Post(url, "application/json", requestBody)

	if err != nil {
		msg := fmt.Sprintf("unable to post to digideps: %s", err.Error())
		log.Print(msg)
		return "", errors.New(msg)
	}

	if response.StatusCode != 202 {
		return "", fmt.Errorf(
			`received unexpected status code from digideps: %d
			response body: %s`, response.StatusCode, response.Body)
	}

	return "successfully POSTed csv", nil
}

func SQSMessageParser(sqsEvent events.SQSEvent) (S3EventRecord, error) {
	if len(sqsEvent.Records) == 0 {
		return S3EventRecord{}, errors.New("no sqs event records")
	}

	event := ObjectCreatedEvent{}
	err := json.Unmarshal([]byte(sqsEvent.Records[0].Body), &event)

	if err != nil {
		return S3EventRecord{}, err
	}

	if len(event.S3EventRecords) == 0 {
		return S3EventRecord{}, errors.New("no s3 event records")
	}

	return event.S3EventRecords[0], nil
}

func InitLambda(sess *session.Session) (Lambda, error) {

	var sessErrors []string
	if sess.Config.Endpoint == nil {
		sessErrors = append(sessErrors, "session.Config.Endpoint to not be nil")
	}

	if !*sess.Config.S3ForcePathStyle {
		sessErrors = append(sessErrors, "session.Config.S3ForcePathStyle to be true")
	}

	if len(sessErrors) != 0 {
		errorString := "expected "
		errorString += strings.Join(sessErrors, " and ")
		return Lambda{}, errors.New(errorString)
	}

	return Lambda{
		s3Client:       s3.New(sess),
		digidepsClient: &http.Client{},
	}, nil
}

func main() {
	sess := session.Must(session.NewSession())

	endpoint := os.Getenv("AWS_S3_ENDPOINT")
	sess.Config.Endpoint = &endpoint
	sess.Config.S3ForcePathStyle = aws.Bool(true)

	l, err := InitLambda(sess)

	if err != nil {
		msg := fmt.Sprintf("error initiliasing lambda: %s", err.Error())
		log.Print(msg)
		panic(err)
	}

	lambda.Start(l.HandleEvent)
}
