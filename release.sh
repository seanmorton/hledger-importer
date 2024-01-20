#!/bin/bash
docker tag smorton517/hledger-importer:latest smorton517/hledger-importer:"$1" &&
docker push smorton517/hledger-importer:"$1" &&
git tag "$1" &&
git push --tags
