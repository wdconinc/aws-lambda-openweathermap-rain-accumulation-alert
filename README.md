# AWS Lambda OpenWeatherMap Rain Accumulation Forecast and Alert

## Deployment

This microservice requires an Amazon Web Services account and some knowledge of AWS and/or IAM. You will also need to have `aws-cli` installed to be able to use the associated publish.sh script.

### AWS SSM Parameter Store
You will need to setup the following parameters in the AWS SSM Parameter Store:
- /GhentDogPark/Weather/APIKey: OpenWeatherMap API key
- /GhentDogPark/Weather/RainAccumulation: Current rain accumulation (in mm)
- /GhentDogPark/Weather/RainDryingFactor: Rain drying factor (in mm / hour)
- /GhentDogPark/Weather/RainMaxAllowed: Maximum accumulated rain allowed (in mm)
- /GhentDogPark/Weather/EmailFrom: From-address for alert emails
- /GhentDogPark/Weather/EmailTo: To-address for alert emails

```
aws ssm put-parameter --name /GhentDogPark/Weather/APIKey --value 01234 --type String
aws ssm put-parameter --name /GhentDogPark/Weather/RainAccumulation --value 0 --type String
aws ssm put-parameter --name /GhentDogPark/Weather/RainDryingFactor --value 1 --type String
aws ssm put-parameter --name /GhentDogPark/Weather/RainMaxAllowed --value 5 --type String
aws ssm put-parameter --name /GhentDogPark/Weather/EmailFrom --value wdconinc@gmail.com --type String
aws ssm put-parameter --name /GhentDogPark/Weather/EmailTo --value board@ghentdogpark.org --type String
```

### AWS Lambda Function
You will want to setup an AWS Lambda Function with a CloudWatch event trigger at a rate of once every 3 hours.

```
zip archive.zip * -r -x .git/\* \*.sh \*.md \*.zip
aws lambda update-function-code --function-name $lambda --zip-file fileb://archive.zip --publish
```

### AWS SES Email Verification
You will need to verify the From-address with AWS SES to be authorized to send emails.

```
aws ses verify-email-identity --email-address wdconinc@gmail.com
```
