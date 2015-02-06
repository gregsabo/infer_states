import requests
import argparse
import sqlite3
import csv

VALID_STATES = set("AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY AS DC FM GU MH MP PW PR VI".split())

zip_cache = dict()
def get_state_for_zip(in_zip):
    """Lookup zipcodes via API. Codes are cached in memory."""

    if not (in_zip in zip_cache):
        url = "http://zip.getziptastic.com/v2/US/" + str(in_zip)
        zip_cache[in_zip] = requests.get(url).json().get('state_short')
    return zip_cache[in_zip]


def dict_factory(cursor, row):
    """Allows sqlite connector to return dictionaries"""

    d = {}
    for idx, col in enumerate(cursor.description):
      try:
        d[col[0]] = str(row[idx] or '').decode("utf-8")
      except UnicodeError:
        continue
    return d

def annotate_record(charge):
    """Add an inferred_us_state record if it can be guessed."""

    if charge['card#country'] != "US":
        return # no need to annotate

    found_state = get_state_for_zip(charge["card#address_zip"])
    state_as_zip = charge["card#address_zip"].strip().upper()
    address_state = charge['card#address_state'].strip().upper()

    for i, candidate in enumerate((found_state, address_state, state_as_zip)):
      if candidate in VALID_STATES:
        charge['inferred_us_state'] = candidate
        break
    else:
        print "Warning: no US State found for charge: %s state from address was: '%s' entered zip code was: '%s'" % (charge['id'], address_state, state_as_zip)


def write_annotated_csv(stripedb, outfile):
    """Query DB from charges, annonate each, and write to csv."""

    results = stripedb.execute("""SELECT * FROM charges;""")
    writer = None
    print 'Beginning export.'
    for charge in results:
        if charge['paid'] != '1' or charge['captured'] != '1':
            continue
        if not writer:
            writer = csv.DictWriter(outfile, ['inferred_us_state'] + sorted(charge.keys()))
            writer.writeheader()
        if charge['card#country'] == "US":
            annotate_record(charge)

        writer.writerow(charge)


def make_db_connection(path):
    stripedb = sqlite3.connect(args.database[0])
    stripedb.row_factory = dict_factory
    return stripedb


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch state for charges.')
    parser.add_argument('database', metavar='DB', type=str, nargs=1, help='Your Stripe SQLite db.')
    parser.add_argument('output_file', metavar='OUTFILE', type=str, nargs=1, help='path for output file')
    args = parser.parse_args()
    stripedb = make_db_connection(args.database[0])
    with open(args.output_file[0], 'w') as outfile:
        write_annotated_csv(stripedb, outfile)
