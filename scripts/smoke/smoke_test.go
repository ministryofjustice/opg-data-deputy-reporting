package main

import (
	"bytes"
	"fmt"
	"net/http"
	"os"
	"testing"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/credentials/stscreds"
	"github.com/aws/aws-sdk-go/aws/session"
	v4 "github.com/aws/aws-sdk-go/aws/signer/v4"
	"github.com/stretchr/testify/assert"
)

// Function to assume an AWS role and return the credentials
func assumeRole(roleToAssume string) *aws.Config {
	sess := session.Must(session.NewSession())
	creds := stscreds.NewCredentials(sess, roleToAssume)
	return &aws.Config{
		Credentials: creds,
		Region:      aws.String("eu-west-1"),
	}
}

// Function to sign an HTTP request using AWS credentials
func signRequest(httpRequest *http.Request, cfg *aws.Config) error {
	sess := session.Must(session.NewSession(cfg))
	signer := v4.NewSigner(sess.Config.Credentials)
	_, err := signer.Sign(httpRequest, nil, "execute-api", *cfg.Region, time.Now())
	return err
}

func TestHealthCheck(t *testing.T) {
	environmentPrefix := os.Getenv("ENVIRONMENT_PREFIX")
	accountId := os.Getenv("ACCOUNT")
	role := os.Getenv("ROLE")

	roleToAssume := fmt.Sprintf("arn:aws:iam::%s:role/%s", accountId, role)
	url := fmt.Sprintf("https://%sdeputy-reporting.api.opg.service.justice.gov.uk/v2/healthcheck", environmentPrefix)

	cfg := assumeRole(roleToAssume)
	httpRequest, err := http.NewRequest(http.MethodGet, url, nil)
	if err != nil {
		fmt.Printf("Failed to create request: (%v)\n", err)
	}

	err = signRequest(httpRequest, cfg)
	if err != nil {
		fmt.Printf("Failed to sign request: (%v)\n", err)
	}

	apiGatewayResponse, err := http.DefaultClient.Do(httpRequest)
	if err != nil {
		fmt.Printf("Failed to call remote service: (%v)\n", err)
	}
	defer apiGatewayResponse.Body.Close()

	assert.Equal(t, apiGatewayResponse.StatusCode, 200)

	bytesBuffer := new(bytes.Buffer)
	bytesBuffer.ReadFrom(apiGatewayResponse.Body)
	responseBody := bytesBuffer.String()
	fmt.Println(responseBody)
}
