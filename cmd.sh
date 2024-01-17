#!/bin/sh

########################################
# Required env vars:
# * GIT_USER_NAME
# * GIT_USER_EMAIL
# * GIT_PRIVATE_KEY
# * GIT_REPO_HOST
# * GIT_REPO_URL
# * LEDGER_FILE_NAME
# * GETMAIL_PW
########################################

mkdir ~/.ssh
printf '%s\n' "$GIT_PRIVATE_KEY" > ~/.ssh/id_rsa
ssh-keyscan -t rsa $GIT_REPO_HOST >> ~/.ssh/known_hosts
chmod -R 700 ~/.ssh

git config --global user.name $GIT_USER_NAME
git config --global user.email $GIT_USER_EMAIL
git clone $GIT_REPO_URL accounting

export LEDGER_FILE="/home/hledger/accounting/$LEDGER_FILE_NAME"
echo $GETMAIL_PW > /tmp/getmailpw
mkdir -p ~/accounting/email_importer/mail/new ~/accounting/email_importer/mail/tmp
cd ~/accounting

set -o pipefail
./email_importer/app/main.py &&
(git add . && git commit -m "Email alerts import $(date -Iseconds)" && git push) || true
