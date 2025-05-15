# MIT License
#
# Copyright (c) 2025 Ryan Park
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from simple_salesforce import Salesforce
import csv
import os
import sys


_IGNORED_DATATYPES = []
_IGNORED_FIELDS = [
    "LastReferencedDate",
    "LastViewedDate",
    "UserRecordAccessId"]


def main():
    try:
        sobj = sys.argv[1]
    except:
        print(f"Usage: {sys.argv[0]} [sobject]")

    sobject_desc = get_sobject_desc(sobj)

    # TODO: some error checking

    csv_rows = []

    try:
        csv_rows = prepare_rows(sobject_desc.get('records'))
    except Exception as e:
        # TODO: better error checking

        print(f"Unable to process {sobj}...")

        from pprint import pprint

        pprint(sobject_desc)

        raise e

    for row in csv_rows:
        print(f"{row['source_field']:<50}"
              f"{row['source_datatype']:<20}"
              f"{row['destination_datatype']:<20}"
              f"{row['salesforce_datatype']:<20}")

    create_csv(sobj, csv_rows)


def create_csv(sobj, rows):
    with open(f"{sobj}.csv", 'w') as file:
        header = [
            'source_field', 'source_datatype', 'destination_datatype',
            'salesforce_datatype']

        writer = csv.DictWriter(file, fieldnames=header)

        writer.writeheader()
        writer.writerows(rows)


def get_sobject_desc(obj):
    sf = Salesforce(
        username=os.environ.get('SFDC_USERNAME'),
        password=os.environ.get('SFDC_PASSWORD'),
        security_token=os.environ.get('SFDC_SECURITYTOKEN'))

    return sf.query(
        f"""
        SELECT
            QualifiedApiName, DataType
        FROM
            FieldDefinition
        WHERE
            EntityDefinition.QualifiedApiName = '{obj}'
        """)


def ignored_row(row):
    return ((row['QualifiedApiName'] in _IGNORED_FIELDS) or
            (row['DataType'] in _IGNORED_DATATYPES))


def prepare_rows(rows):
    return [
        {
            'source_field': row['QualifiedApiName'],
            'source_datatype': xfm_source_datatype(row['DataType']),
            'destination_datatype': xfm_dest_datatype(row['DataType']),
            'salesforce_datatype': row['DataType']
        }
        for row in rows if not ignored_row(row)
    ]


def xfm_source_datatype(datatype):
    if datatype == "Address":
        return "ADDRESS"
    elif datatype.startswith("Auto Number"):
        return "STRING"
    elif datatype == "Checkbox":
        return "BOOLEAN"
    elif datatype.startswith("Content"):
        return "STRING"
    elif datatype.startswith("Currency"):
        return "CURRENCY"
    elif datatype == "Date":
        return "DATE"
    elif datatype == "Date/Time":
        return "DATETIME"
    elif datatype == "Email":
        return "EMAIL"
    elif datatype == "External Lookup":
        return "STRING"
    elif datatype == "Fax":
        return "PHONE"
    elif datatype.startswith("Formula"):
        try:
            return xfm_source_datatype(
                datatype[datatype.index('(')+1:datatype.index(')')])
        except:
            return "REPLACE_ME"
    elif datatype == "Geolocation":
        return "LOCATION"
    elif datatype == "Hierarchy":
        return "REFERENCE"
    elif datatype.startswith("Long Text Area"):
        return "TEXTAREA"
    elif datatype.startswith("Lookup"):
        return "REFERENCE"
    elif datatype.startswith("Master-Detail"):
        return "REFERENCE"
    elif datatype == "Name":
        return "STRING"
    elif datatype.startswith("Number"):
        return "NUMBER"
    elif datatype.startswith("Percent"):
        return "PRECENT"
    elif datatype.startswith("Picklist"):
        return "PICKLIST"
    elif datatype == "Picklist (Multi-Select)":
        return "MULTIPICKLIST"
    elif datatype == "Phone":
        return "PHONE"
    elif datatype == "Record Type":
        return "REFERENCE"
    elif datatype.startswith("Rich Text Area"):
        return "TEXTAREA"
    elif datatype.startswith("Roll-Up"):
        return "REPLACE_ME"
    elif datatype.startswith("Text Area"):
        return "TEXTAREA"
    elif datatype.startswith("Text"):
        return "STRING"
    elif datatype.startswith("URL"):
        return "URL"

    # Intentionally raising an exception to see if a value needs to be added
    # the long list of types
    raise Exception(f"Unknown Data Type {datatype}")


def xfm_dest_datatype(datatype):
    if datatype == "Address":
        return "STRING"
    elif datatype.startswith("Auto Number"):
        return "STRING"
    elif datatype == "Checkbox":
        return "BOOLEAN"
    elif datatype.startswith("Content"):
        return "STRING"
    elif datatype.startswith("Currency"):
        return "FLOAT"
    elif datatype == "Date":
        return "DATE"
    elif datatype == "Date/Time":
        return "DATETIME"
    elif datatype == "Email":
        return "STRING"
    elif datatype == "External Lookup":
        return "STRING"
    elif datatype == "Fax":
        return "STRING"
    elif datatype.startswith("Formula"):
        try:
            return xfm_dest_datatype(
                datatype[datatype.index('(')+1:datatype.index(')')])
        except:
            return "REPLACE_ME"
    elif datatype == "Geolocation":
        return "STRING"
    elif datatype == "Hierarchy":
        return "STRING"
    elif datatype.startswith("Long Text Area"):
        return "STRING"
    elif datatype.startswith("Lookup"):
        return "STRING"
    elif datatype.startswith("Master-Detail"):
        return "STRING"
    elif datatype == "Name":
        return "STRING"
    elif datatype.startswith("Number"):
        return "NUMBER"
    elif datatype.startswith("Percent"):
        return "FLOAT"
    elif datatype.startswith("Picklist"):
        return "STRING"
    elif datatype == "Picklist (Multi-Select)":
        return "STRING"
    elif datatype == "Phone":
        return "STRING"
    elif datatype == "Record Type":
        return "STRING"
    elif datatype.startswith("Rich Text Area"):
        return "STRING"
    elif datatype.startswith("Roll-Up"):
        return "REPLACE_ME"
    elif datatype.startswith("Text Area"):
        return "STRING"
    elif datatype.startswith("Text"):
        return "STRING"
    elif datatype.startswith("URL"):
        return "STRING"

    raise Exception(f"Unknown Data Type {datatype}")


if __name__ == "__main__":
    main()
