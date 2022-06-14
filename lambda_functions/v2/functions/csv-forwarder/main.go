package main

import (
	"errors"
	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
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

type CSV struct {
	CSV string
}

func SQSMessageParsing(sqsEvent events.SQSEvent) EventRecord {
	er := EventRecord{}
	er.S3.Bucket.Name = "csv-bucket"
	er.S3.Object.Key = "test.csv"

	return er
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
	//input := s3.GetObjectInput{Bucket: aws.String(event.Records[0].S3.Bucket.Name), Key: aws.String(event.Records[0].S3.Object.Key)}
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
	////// Post to digideps
	//postBody, _ := json.Marshal(map[string]string{
	//	"type": "lay",
	//	"csv":  csvContents,
	//})
	//
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
