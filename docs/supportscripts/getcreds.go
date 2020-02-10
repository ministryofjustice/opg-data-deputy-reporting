package main

import (
	"fmt"

	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/credentials/stscreds"

)

func main() {

    roletoassume := "arn:aws:iam::248804316466:role/operator"

	mysession := session.Must(session.NewSession())
	digidepcreds := stscreds.NewCredentials(mysession, roletoassume)
	cfg := aws.Config{Credentials: digidepcreds,Region: aws.String("eu-west-1")}
	sess := session.Must(session.NewSession(&cfg))
	sessionstring, err := sess.Config.Credentials.Get()

	if err != nil {
		fmt.Println(err)
	}

	fmt.Println("Access Key:    ", sessionstring.AccessKeyID)
	fmt.Println("Secret Key:    ", sessionstring.SecretAccessKey)
	fmt.Println("Session Token: ", sessionstring.SessionToken)
	fmt.Println("Provider Name: ",sessionstring.ProviderName)

}
