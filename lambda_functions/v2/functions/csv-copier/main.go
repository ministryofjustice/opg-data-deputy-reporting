package main

import (
	"fmt"
	"net/url"
	"os"

	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/aws/aws-sdk-go/service/s3/s3iface"
)

type customFunction struct {
	client s3iface.S3API
}

func (l *customFunction) HandleEvent() (string, error) {
	sirius := os.Getenv("AWS_SIRIUS_BUCKET")
	item := os.Getenv("AWS_BUCKET_ITEM")
	digiDeps := os.Getenv("AWS_DIGIDEPS_BUCKET")

	source := sirius + "/" + digiDeps
	// Copy the item
	_, err := l.client.CopyObject(&s3.CopyObjectInput{Bucket: aws.String(digiDeps), CopySource: aws.String(url.PathEscape(source)), Key: aws.String(item)})
	if err != nil {
		exitErrorf("Unable to copy item from bucket %q to bucket %q, %v", sirius, digiDeps, err)
	}

	// Wait to see if the item got copied
	err = l.client.WaitUntilObjectExists(&s3.HeadObjectInput{Bucket: aws.String(digiDeps), Key: aws.String(item)})
	if err != nil {
		exitErrorf("Error occurred while waiting for item %q to be copied to bucket %q, %v", sirius, item, digiDeps, err)
	}

	fmt.Printf("Item %q successfully copied from bucket %q to bucket %q\n", item, sirius, digiDeps)
	return "Success", nil
}

func initLambda(sess *session.Session) (*customFunction, error) {
	return &customFunction{s3.New(sess)}, nil
}

func main() {
	endpoint := os.Getenv("AWS_ENDPOINT")
	region := os.Getenv("AWS_REGION")

	fmt.Print("Hello, New World\n")

	sess := session.Must(session.NewSession())
	sess.Config.Endpoint = &endpoint
	sess.Config.S3ForcePathStyle = aws.Bool(true)
	sess.Config.Region = aws.String(region)

	l, _ := initLambda(sess)

	lambda.Start(l.HandleEvent)
}

func exitErrorf(msg string, args ...interface{}) {
	fmt.Fprintf(os.Stderr, msg+"\n", args...)
	os.Exit(1)
}
