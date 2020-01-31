package main

import (
	"bytes"
	"fmt"
	"net/http"
	"time"

	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/aws"
	v4 "github.com/aws/aws-sdk-go/aws/signer/v4"
	"github.com/aws/aws-sdk-go/aws/credentials/stscreds"

)

func main() {

	mysession := session.Must(session.NewSession())

	digidepcreds := stscreds.NewCredentials(mysession, "arn:aws:iam::248804316466:role/operator")

	cfg := aws.Config{Credentials: digidepcreds,Region: aws.String("eu-west-1")}

	sess := session.Must(session.NewSession(&cfg))
	signer := v4.NewSigner(sess.Config.Credentials)

	req, _ := http.NewRequest(http.MethodGet, "https://api-deputy-reporting.dev.sirius.opg.digital/v1/deputy-reporting/healthcheck", nil)

	_, err := signer.Sign(req, nil, "execute-api", *cfg.Region, time.Now())
	if err != nil {
		fmt.Printf("failed to sign request: (%v)\n", err)
	}

	res, err := http.DefaultClient.Do(req)
	if err != nil {
		fmt.Printf("failed to call remote service: (%v)\n", err)
	}

	defer res.Body.Close()
	if res.StatusCode != 200 {
		fmt.Printf("ERROR: (%d): (%s)\n", res.StatusCode, res.Status)
	}

	buf := new(bytes.Buffer)
	buf.ReadFrom(res.Body)
	newStr := buf.String()

	fmt.Println(newStr)
}
