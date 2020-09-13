#!/bin/bash -e
export LAMBDA_NAME=arn:aws:lambda:us-east-1:112482396000:function:ask-localschool-melissa-default-1600022005772
ask deploy -p melissa --ignore-hash
aws --profile melissa lambda update-function-configuration --function-name $LAMBDA_NAME --timeout 60