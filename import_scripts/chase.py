from datetime import datetime
import lxml.html
import re

CHASE_SUBJECT_RE = "^Your(.+)transaction with(.+)$"
ACCOUNTS_IMPORT_FILES = {
    "United Explorer": "chase_united.csv",
    "Chase Credit": "chase_united.csv",
    "Chase Freedom Unlimited": "chase_freedom.csv",
}

def parse_email(email_msg):
    subject = email_msg.get("Subject")
    if not re.match(CHASE_SUBJECT_RE, subject):
        return (None, None)

    raw_html = email_msg.get_payload(decode=True)
    html = lxml.html.fromstring(raw_html)

    table_td_data = html.xpath("//td[@class='font14']/text()")
    account = table_td_data[2]
    desc = table_td_data[5].strip().replace(',', ' ')
    amount = re.sub("\$", "-", table_td_data[7]).replace(',', '')
    raw_date = html.xpath("//td[@class='font14']/span/a/text()")[0]
    date_str = ' '.join(raw_date.split(' ')[0:3])

    try:
        date = datetime.strptime(date_str, "%b %d, %Y").strftime("%m/%d/%Y")
    except:
        raise AssertionError(f"Invalid date for Chase: {date_str}")

    assert(re.match('^-?(\d+\.\d{2})$', amount)), f"Invalid amount for Chase: {amount}"

    import_filename = ACCOUNTS_IMPORT_FILES.get(account)
    assert(import_filename), f"Unknown account for Chase: {account}"

    csv_row = ','.join(('', date, desc, '', '', amount, ''))

    return (import_filename, [csv_row])
