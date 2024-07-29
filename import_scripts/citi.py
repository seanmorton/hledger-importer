from datetime import datetime
import lxml.html
import re

CITI_SUBJECT_RE = "^A(.+)transaction was made on your account$"
IMPORT_FILENAME = "citi_aa.csv"

def parse_email(email_msg):
    subject = email_msg.get("Subject")
    if not re.match(CITI_SUBJECT_RE, subject):
        return (None, None)

    html_parts = [part for part in email_msg.walk() if part.get_content_type() == "text/html"]
    assert(len(html_parts) == 1), f"Unknown Payload for Citi!"

    raw_html = html_parts[0].get_payload(decode=True)
    html = lxml.html.fromstring(raw_html)

    amount_str = html.xpath("//span[@class='TS-ActionSummaryV2-Title']/text()")[0]
    values = html.xpath("//span[@class='TS-ActionSummaryV2-Value']/text()")
    amount = re.sub("\$", "", amount_str.split(':')[1].strip())
    desc = values[1].strip().replace(',', ' ')
    date = values[2]

    try:
        datetime.strptime(date, "%m/%d/%Y")
    except:
        raise AssertionError(f"Invalid date for Citi: {date_str}")

    assert(re.match('^-?(\d+\.\d{2})$', amount)), f"Invalid amount for Citi: {amount}"

    if float(amount) > 0:
        csv_row = ','.join(('', date, desc, amount, ''))
    else:
        csv_row = ','.join(('', date, desc, '', amount))

    return (IMPORT_FILENAME, [csv_row])
