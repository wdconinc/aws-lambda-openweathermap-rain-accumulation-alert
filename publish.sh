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
rm -f function.zip

echo "Installing dependencies"
rm -f *.whl
mkdir -p package
pip install --upgrade -t ./package/ matplotlib pytz
rm -r package/*.dist-info package/__pycache__

echo "Getting AWS Lambda AMI"
mkdir -p lambda_build
pushd lambda_build
sudo docker run -v $(pwd):/outputs --rm -it amazonlinux:latest
popd

echo "Adding dependencies to zip file"
pushd package
zip -r ../function.zip .
popd

echo "Creating a new zip file with dependencies"
zip -g function.zip * -r -x .git/\* package/\* \*.sh \*.md \*.zip \*.png \*.whl

echo "Uploading $lambda"
aws lambda update-function-code --function-name $lambda --zip-file fileb://function.zip --publish

if [ $? -eq 0 ]; then
  echo "!! Upload successful !!"
else
  echo "Upload failed"
  echo "If the error was a 400, check that there are no slashes in your lambda name"
  echo "Lambda name = $lambda"
  exit 1;
fi
