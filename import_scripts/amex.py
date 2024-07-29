from datetime import datetime
#from email.header import decode_header
import lxml.html
import logging
import re

AMEX_SUBJECT = "Large Purchase Approved"
AMEX_FILENAME = "amex_blue.csv"

def parse_email(email_msg):
    subject = email_msg.get("Subject")
    #subject = decode_header(email_msg.get("Subject"))[0][0].decode('utf-8')

    if subject != AMEX_SUBJECT:
        logging.info(f"Unknown subject from AMEX: {subject}")
        return (None, None)

    html_parts = [part for part in email_msg.walk() if part.get_content_type() == "text/html"]
    assert(len(html_parts) == 1), f"Unknown Payload for AMEX!"


    raw_html = html_parts[0].get_payload(decode=True)
    html = lxml.html.fromstring(raw_html)

    data = html.xpath('//table//div//p/text()')
    desc = data[6].strip().replace(',', ' ')
    amount = re.sub("\*", "", re.sub("\$", "", data[7])).replace(',', '')
    date_str = data[8]

    try:
        date = datetime.strptime(date_str, "%a, %b %d, %Y").strftime("%m/%d/%Y")
    except:
        logging.error(f"Invalid date for AMEX: {date_str}")
        return (None, None)

    assert(re.match('^-?(\d+\.\d{2})$', amount)), f"Invalid amount for AMEX: {amount}"

    csv_row = ','.join((date,desc,amount))

    return (AMEX_FILENAME, [csv_row])
