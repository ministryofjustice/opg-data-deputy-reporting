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

func assumeRoleWithChaining(baseRoleToAssume, finalRoleToAssume string) *aws.Config {
	// Create a session to assume the base role
	sess := session.Must(session.NewSession())
	baseCreds := stscreds.NewCredentials(sess, baseRoleToAssume)

	// If no final role is provided, return config with base role credentials
	if finalRoleToAssume == "" {
		return &aws.Config{
			Credentials: baseCreds,
			Region:      aws.String("eu-west-1"),
		}
	}

	// Otherwise, create a chained session using the base role credentials
	chainedSess := session.Must(session.NewSession(&aws.Config{
		Credentials: baseCreds,
	}))

	// Assume the final role using the chained session
	finalCreds := stscreds.NewCredentials(chainedSess, finalRoleToAssume)

	return &aws.Config{
		Credentials: finalCreds,
		Region:      aws.String("eu-west-1"),
	}
}

func signRequest(httpRequest *http.Request, cfg *aws.Config) error {
	sess := session.Must(session.NewSession(cfg))
	signer := v4.NewSigner(sess.Config.Credentials)
	_, err := signer.Sign(httpRequest, nil, "execute-api", *cfg.Region, time.Now())
	return err
}

func TestHealthCheck(t *testing.T) {
	environmentPrefix := os.Getenv("ENVIRONMENT_PREFIX")

	siriusAccountId := os.Getenv("SIRIUS_ACCOUNT")
	baseRole := os.Getenv("BASE_ROLE")

	digidepsAccountId := os.Getenv("DIGIDEPS_ACCOUNT")
	finalRole := os.Getenv("FINAL_ROLE")

	baseRoleToAssume := fmt.Sprintf("arn:aws:iam::%s:role/%s", siriusAccountId, baseRole)

	finalRoleToAssume := ""
	if finalRole != "" {
		finalRoleToAssume = fmt.Sprintf("arn:aws:iam::%s:role/%s", digidepsAccountId, finalRole)
	}
	// URL for the health check endpoint
	url := fmt.Sprintf("https://%sdeputy-reporting.api.opg.service.justice.gov.uk/v2/healthcheck", environmentPrefix)

	cfg := assumeRoleWithChaining(baseRoleToAssume, finalRoleToAssume)
	httpRequest, err := http.NewRequest(http.MethodGet, url, nil)
	if err != nil {
		fmt.Printf("Failed to create request: (%v)\n", err)
	}

	// Sign the request with the assumed role credentials
	err = signRequest(httpRequest, cfg)
	if err != nil {
		fmt.Printf("Failed to sign request: (%v)\n", err)
	}

	apiGatewayResponse, err := http.DefaultClient.Do(httpRequest)
	if err != nil {
		fmt.Printf("Failed to call remote service: (%v)\n", err)
	}
	defer apiGatewayResponse.Body.Close()

	assert.Equal(t, 200, apiGatewayResponse.StatusCode)

	bytesBuffer := new(bytes.Buffer)
	bytesBuffer.ReadFrom(apiGatewayResponse.Body)
	responseBody := bytesBuffer.String()
	fmt.Println(responseBody)
}
