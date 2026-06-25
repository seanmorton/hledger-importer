#!/bin/bash
docker tag seanmorton/hledger-importer:latest seanmorton/hledger-importer:"$1" &&
docker push seanmorton/hledger-importer:"$1" &&
git tag "$1" &&
git push --tags
