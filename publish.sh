#!/bin/bash

if [ "$#" -ne 1 ]; then
  echo "Usage : $0 lambda-name";
  exit 1;
fi

lambda=${1}

echo "Checking that aws-cli is installed"
which aws
if [ $? -eq 0 ]; then
  echo "aws-cli is installed, continuing..."
else
  echo "You need aws-cli to deploy this lambda. Google 'aws-cli install'"
  exit 1
fi

echo "Removing old zip"
rm -f archive.zip

echo "Creating a new zip file"
zip archive.zip * -r -x .git/\* \*.sh \*.md \*.zip

echo "Uploading $lambda"
aws lambda update-function-code --function-name $lambda --zip-file fileb://archive.zip --publish

if [ $? -eq 0 ]; then
  echo "!! Upload successful !!"
else
  echo "Upload failed"
  echo "If the error was a 400, check that there are no slashes in your lambda name"
  echo "Lambda name = $lambda"
  exit 1;
fi
