#!/bin/bash

rm deployment.zip
mkdir -p lambda_build
cd lambda_build
cp ../lambda_function.py .
pip3 install --target . -r ../lambda_requirements.txt
zip -r ../deployment.zip ./*
cd ../
zip -r deployment.zip util
zip -r deployment.zip lambda_function.py
cp deployment.zip ../
cd ../
rm -rf lambda_build
