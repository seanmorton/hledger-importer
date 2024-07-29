from datetime import datetime
import re

DISCOVER_SUBJECT = "Transaction Alert"
IMPORT_FILENAME = "discover_it.csv"

def parse_email(email_msg):
    subject = email_msg.get("Subject")
    if subject != DISCOVER_SUBJECT:
        return (None, None)

    text_parts = [part for part in email_msg.walk() if part.get_content_type() == "text/plain"]
    assert(len(text_parts) == 1), f"Unknown Payload for Discover!"
    raw_text = text_parts[0].get_payload(decode=True).decode()

    date_str = None
    desc = None
    amount = None
    for line in raw_text.split('\n'):
        if line.startswith("Transaction Date"):
            date_str = line.split(':')[2].strip()
        if line.startswith("Merchant"):
            desc = line.split(':')[1].strip().replace(',', ' ')
        if line.startswith("Amount"):
            amount = re.sub('\$', '', line.split(':')[1].strip())

    assert(date_str and desc and amount), "Missing data from Discover scrape!"

    try:
        date = datetime.strptime(date_str, "%B %d, %Y").strftime("%m/%d/%Y")
    except:
        raise AssertionError(f"Invalid date for Discover: {date_str}")

    assert(re.match('^-?(\d+\.\d{2})$', amount)), f"Invalid amount for Discover: {amount}"

    csv_row = ','.join(('', date, desc, amount, ''))

    return (IMPORT_FILENAME, [csv_row])
