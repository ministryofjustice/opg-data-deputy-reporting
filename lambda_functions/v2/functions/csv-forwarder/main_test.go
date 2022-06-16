package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/aws/aws-sdk-go/service/s3/s3iface"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/suite"
	"io"
	"net/http"
	"os"
	"reflect"
	"strings"
	"testing"
)

type S3ClientMock struct {
	s3iface.S3API
	mock.Mock
}

func (s *S3ClientMock) GetObject(input *s3.GetObjectInput) (*s3.GetObjectOutput, error) {
	outputs := s.Called(*input)
	return outputs.Get(0).(*s3.GetObjectOutput), outputs.Error(1)
}

type DigidepsClientMock struct {
	http.Client
	mock.Mock
}

func (d *DigidepsClientMock) Post(url, contentType string, body io.Reader) (resp *http.Response, err error) {
	outputs := d.Called(url, contentType, body)
	return outputs.Get(0).(*http.Response), outputs.Error(1)
}

func TestSQSMessageParsing(t *testing.T) {
	//Parse the event
	t.Run("Parse incoming SQS Message into an EventRecord", func(t *testing.T) {
		sqsEvent := generateValidSQSEvent("csv-bucket", "test.csv")

		actual, _ := SQSMessageParser(sqsEvent)

		expected := S3EventRecord{}

		expected.S3.Bucket.Name = "csv-bucket"
		expected.S3.Object.Key = "test.csv"

		assert.Equal(t, expected, actual)
	})

	//Parse the event
	t.Run("Parse incoming SQS Message into an EventRecord", func(t *testing.T) {
		sqsEvent := generateValidSQSEvent("pdf-bucket", "test.pdf")

		actual, _ := SQSMessageParser(sqsEvent)

		expected := S3EventRecord{}

		expected.S3.Bucket.Name = "pdf-bucket"
		expected.S3.Object.Key = "test.pdf"

		assert.Equal(t, actual, expected)
	})

	t.Run("Returns error when parsing invalid JSON", func(t *testing.T) {
		sqsEvent := generateInvalidSQSEvent("{Invalid JSON}", 1)

		_, err := SQSMessageParser(sqsEvent)

		assert.Error(t, err)
	})

	t.Run("Returns error when there are no S3EventRecords", func(t *testing.T) {
		sqsEvent := generateInvalidSQSEvent(`{"Records":[]}`, 1)

		_, err := SQSMessageParser(sqsEvent)

		assert.Error(t, err)
	})

	t.Run("Returns error when there are no records in the SQS Event", func(t *testing.T) {
		sqsEvent := generateInvalidSQSEvent("", 0)

		_, err := SQSMessageParser(sqsEvent)

		assert.Error(t, err)
	})
}

// Define the suite, and absorb the built-in basic suite
// functionality from testify - including a T() method which
// returns the current testing context
type HandleEventSuite struct {
	suite.Suite
	l            Lambda
	s3Mock       *S3ClientMock
	DDClientMock *DigidepsClientMock
}

// Make sure that VariableThatShouldStartAtFive is set to five
// before each test
func (suite *HandleEventSuite) SetupTest() {
	suite.s3Mock = new(S3ClientMock)
	suite.DDClientMock = new(DigidepsClientMock)
	suite.l = Lambda{
		s3Client:       suite.s3Mock,
		digidepsClient: suite.DDClientMock,
	}
}

func (suite *HandleEventSuite) TestHandleEvent() {
	cases := []struct {
		description          string
		bucketName, keyValue string
	}{
		{description: "Happy path with valid S3Input values", bucketName: "pdf-bucket", keyValue: "small.pdf"},
		{description: "Happy path with valid S3Input values - ensure SQS event values used in S3Input", bucketName: "csv-bucket", keyValue: "large.csv"},
	}

	for _, tt := range cases {
		suite.Suite.T().Log(tt.description)
		_ = os.Setenv("DIGIDEPS_API_ENDPOINT", "http://mock-digideps-endpoint")

		input := s3.GetObjectInput{Bucket: aws.String(tt.bucketName), Key: aws.String(tt.keyValue)}
		output := generateValidGetObjectOutput()

		suite.s3Mock.On("GetObject", input).Return(&output, nil)

		requestBody := generateValidPostRequest()
		suite.DDClientMock.On("Post", "http://mock-digideps-endpoint", "application/json", requestBody).Return(&http.Response{StatusCode: 202}, nil)

		event := generateValidSQSEvent(tt.bucketName, tt.keyValue)
		response, err := suite.l.HandleEvent(event)

		suite.Assert().Nil(err)
		suite.Assert().Equal("Successfully POSTed CSV", response)

		mock.AssertExpectationsForObjects(suite.T(), suite.s3Mock, suite.DDClientMock)

		suite.s3Mock.ExpectedCalls = nil
		suite.DDClientMock.ExpectedCalls = nil
	}
}

func (suite *HandleEventSuite) TestHandleEventDDAPIEnvVarNotSet() {
	_ = os.Unsetenv("DIGIDEPS_API_ENDPOINT")
	event := generateValidSQSEvent("pdf-bucket", "small.pdf")
	response, err := suite.l.HandleEvent(event)

	suite.Assert().Equal("", response)
	suite.Assert().Error(err, "DIGIDEPS_API_ENDPOINT environment variable not set")
}

func (suite *HandleEventSuite) TestHandleEventParsingSQSMessageError() {
	_ = os.Setenv("DIGIDEPS_API_ENDPOINT", "http://mock-digideps-endpoint")

	event := generateInvalidSQSEvent("{Invalid JSON}", 1)
	response, err := suite.l.HandleEvent(event)

	suite.Assert().Equal("", response)
	suite.Assert().Error(err)
}

func (suite *HandleEventSuite) TestHandleEventErrorPOSTingToDD() {
	_ = os.Setenv("DIGIDEPS_API_ENDPOINT", "http://mock-digideps-endpoint")

	input := s3.GetObjectInput{Bucket: aws.String("bucket"), Key: aws.String("key")}
	output := generateValidGetObjectOutput()

	suite.s3Mock.On("GetObject", input).Return(&output, nil)

	requestBody := generateValidPostRequest()
	suite.DDClientMock.On("Post", "http://mock-digideps-endpoint", "application/json", requestBody).Return(&http.Response{StatusCode: 202}, errors.New("something went wrong"))

	event := generateValidSQSEvent("bucket", "key")
	response, err := suite.l.HandleEvent(event)

	suite.Assert().Equal("", response)
	suite.Assert().Error(err)
}

func (suite *HandleEventSuite) TestHandleEventNon202ResponseReturnsError() {
	_ = os.Setenv("DIGIDEPS_API_ENDPOINT", "http://mock-digideps-endpoint")

	cases := []struct {
		statusCode int
	}{
		{statusCode: 200},
		{statusCode: 308},
		{statusCode: 403},
		{statusCode: 500},
	}

	for _, tt := range cases {
		suite.Suite.T().Log(tt.statusCode)

		input := s3.GetObjectInput{Bucket: aws.String("bucket"), Key: aws.String("key")}
		output := generateValidGetObjectOutput()

		suite.s3Mock.On("GetObject", input).Return(&output, nil)

		requestBody := generateValidPostRequest()
		suite.DDClientMock.On("Post", "http://mock-digideps-endpoint", "application/json", requestBody).Return(&http.Response{StatusCode: tt.statusCode}, nil)

		event := generateValidSQSEvent("bucket", "key")
		response, err := suite.l.HandleEvent(event)

		suite.Assert().Equal("", response)
		suite.Assert().Error(err)

		suite.s3Mock.ExpectedCalls = nil
		suite.DDClientMock.ExpectedCalls = nil
	}

}

func TestInitLambda(t *testing.T) {
	t.Run("Happy path initialises valid lambda", func(t *testing.T) {
		expectedSess := session.Must(session.NewSession())

		endpoint := os.Getenv("AWS_S3_ENDPOINT")
		expectedSess.Config.Endpoint = &endpoint
		expectedSess.Config.S3ForcePathStyle = aws.Bool(true)

		ddClient := http.Client{}

		expectedLambda := Lambda{
			s3Client:       s3.New(expectedSess),
			digidepsClient: &ddClient,
		}

		actualLambda := InitLambda(expectedSess)

		assert.IsTypef(t, expectedLambda, actualLambda, fmt.Sprintf("Wanted type %s. Got type %s", reflect.TypeOf(expectedLambda), reflect.TypeOf(actualLambda)))
		assert.IsTypef(
			t,
			expectedLambda.s3Client, actualLambda.s3Client,
			fmt.Sprintf("Wanted type %s. Got type %s", reflect.TypeOf(expectedLambda.s3Client), reflect.TypeOf(actualLambda.s3Client)),
		)
		assert.IsTypef(
			t,
			expectedLambda.digidepsClient, actualLambda.digidepsClient,
			fmt.Sprintf("Wanted type %s. Got type %s", reflect.TypeOf(expectedLambda.digidepsClient), reflect.TypeOf(actualLambda.digidepsClient)),
		)
	})

	t.Run("Error when not configuring session", func(t *testing.T) {
		expectedSess := session.Must(session.NewSession())

		_, err := InitLambda(expectedSess)

		assert.Error(t, err)
	})
}

// In order for 'go test' to run this suite, we need to create
// a normal test function and pass our suite to suite.Run
func TestHandleEventSuite(t *testing.T) {
	suite.Run(t, new(HandleEventSuite))
}

func generateValidGetObjectOutput() s3.GetObjectOutput {
	csv := `Header1,Header2
Value1,Value2`
	r := io.NopCloser(strings.NewReader(csv))

	return s3.GetObjectOutput{Body: r}
}

func generateValidPostRequest() *bytes.Buffer {
	encodedCSV := "SGVhZGVyMSxIZWFkZXIyClZhbHVlMSxWYWx1ZTI="
	postBody, _ := json.Marshal(map[string]string{
		"csv": encodedCSV,
	})

	return bytes.NewBuffer(postBody)
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

func generateInvalidSQSEvent(sqsMessageBody string, numOfRecords int) events.SQSEvent {

	var records []events.SQSMessage

	if numOfRecords > 0 {
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

		records = []events.SQSMessage{sqsMessage}
	}

	sqsEvent := events.SQSEvent{Records: records}
	return sqsEvent
}

//Request to s3 endpoint is valid (testing env variable)

//Valid input to s3 request

//Test the csv is base64 encoded

//Request to digideps endpoint is valid (testing env variable)

//Test valid string response is returned
