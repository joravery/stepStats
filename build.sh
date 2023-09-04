#!/bin/bash

rm -f deployment.zip &&
mkdir -p lambda_build &&
cd lambda_build &&
pip3 install --target . -r ../lambda_requirements.txt &&
zip -r ../deployment.zip ./* &&
cd ../ &&
zip -r deployment.zip util &&
zip deployment.zip lambda_function.py &&
cp deployment.zip ../ &&
rm -rf lambda_build
