Disclaimer
--------

This script is to be used for informative purposes only. I highly
recommend consulting an accountant when preparing your taxes.

Determine States for Stripe Charges
=====================

This Python script will write an annotated CSV of all charges from
a Stripe account. You will need an Internet connection and all of
your Stripe data as a SQLite DB.

It attempts to find the US state for each charge from each of these
sources (most preferred first):

* US state associated with the charge's zipcode, as returned by the API at getziptastic.com.
* The US state entered in the address field for the charge, if available.
* The "zip code" for the charge, if the customer accidentally entered a state code in that field.

Usage
------

1. Pull this repo.
2. Have your .db file ready.
3. Install the python "requests" library, for example `pip install requests`
4. Run the script with `python main.py my_stripe_db.db output.csv`

A small percentage of charges will not match for customers who input address data incorrectly.
Most of these can be determined by hand by looking up the charge ID on Stripe dashboard.

Possible Modifications
-----------

It should be fairly easy to edit this script to take a CSV export as a data source, or
to use a local map of zipcodes instead of the Ziptastic API.
