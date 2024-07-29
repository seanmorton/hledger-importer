#! /usr/bin/env python3
import email
import logging
import os
import re
import sys

import amex
import chase
import citi
import discover
import ftf

HL_IMPORT_DIR = "../../import"
MAIL_DIR = "../mail"
NEW_MAIL_DIR = MAIL_DIR + "/new"
CUR_MAIL_DIR = MAIL_DIR + "/cur"
DATA_MAIL_DIR = MAIL_DIR + "/data"

AMEX_FROM = "American Express <AmericanExpress@welcome.americanexpress.com>"

def import_email_alerts(dry_run):
    os.system(f"getmail --getmaildir={DATA_MAIL_DIR}")
    new_mail = os.listdir(NEW_MAIL_DIR)
    import_filenames = set()

    for mail_filename in new_mail:
        mail_file_path = NEW_MAIL_DIR + '/' + mail_filename
        fp = open(mail_file_path)
        email_msg = email.message_from_file(fp)
        fp.close()
        (import_filename, csv_rows) = parse_email(email_msg)

        if not import_filename or not csv_rows:
            from_header = email_msg.get('From')
            subject_header = email_msg.get('Subject')
            logging.info(f"Skipping email: From: {from_header}, Subject: {subject_header}, File: {mail_filename}")
            if not dry_run:
                os.system(f"mv {mail_file_path} {CUR_MAIL_DIR}/")
            continue

        import_filenames.add(import_filename)
        if not dry_run:
            import_file = open(f"{HL_IMPORT_DIR}/{import_filename}", "a")
            import_file.write('\n' + '\n'.join(csv_rows))
            import_file.close()
            os.system(f"mv {mail_file_path} {CUR_MAIL_DIR}/")
        else:
            for csv_row in csv_rows:
                logging.debug(f"{import_filename}: {csv_row}")

    if import_filenames:
        if not dry_run:
            logging.info(f"Running import for {', '.join(import_filenames)}")
            for import_filename in import_filenames:
                hledger_result = os.system(f"hledger import {HL_IMPORT_DIR}/{import_filename}")
                if hledger_result == 1:
                    raise AssertionError(f"hledger import failed for {import_filename}")
    else:
        logging.info("No new email; exiting.")
        exit(1)

def parse_email(email_msg):
    from_header = re.sub("\"", "", email_msg.get('From')) # AMEX started adding quotes to subject..

    if from_header == AMEX_FROM:
        return amex.parse_email(email_msg)
    else:
        logging.warning(f"Unknown sender: {from_header}")
        return (None, None)

if __name__=="__main__":
    dry_run = False
    if len(sys.argv) > 1:
        if sys.argv[1] == '--dry-run':
            dry_run = True
        else:
            print("Only supported argument is --dry-run")
            exit(1)

    logging.basicConfig(
            format="%(asctime)s %(levelname)s %(message)s",
            level=logging.DEBUG)

    orig_dir = os.getcwd()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    logging.info(f"Importing email alert transactions..")
    try:
        import_email_alerts(dry_run)
    except AssertionError as msg:
        logging.error(msg)
        exit(1)

    os.chdir(orig_dir)
