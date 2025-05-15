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

from datetime import datetime, timedelta, timezone
import csv
import sys


_DATABASE_DATATYPE_MAPPING = {
    'BOOLEAN': 'BOOLEAN',
    'CURRENCY': 'FLOAT',
    'DATE': 'DATE',
    'DATETIME': 'TIMESTAMP_NTZ(9)',
    'FLOAT': 'FLOAT',
    'NUMBER': 'NUMBER(38,0)',
    'STRING': 'VARCHAR',
    'TEXT': 'VARCHAR',
}


def main():
    try:
        filename = sys.argv[1]
    except:
        print(f"Usage: {sys.argv[0]} [filename]")

    sobj = filename[:filename.index('.')]

    with open(filename, mode='r') as file:
        rows = list(csv.DictReader(file))

    print(generate_terraform(sobj, rows))


def generate_terraform(object_name, rows):
    output = []

    output.append(f'#')
    output.append(f'# AppFlow Flow')
    output.append(f'#')
    output.append(f'')
    output.append(f'resource "aws_appflow_flow" "salesforce_{object_name.lower()}" {{')
    output.append(f'  name = "salesforce_{object_name.lower()}"')
    output.append(f'')
    output.append(f'  source_flow_config {{')
    output.append(f'    connector_profile_name = aws_appflow_connector_profile.salesforce_connector_profile.name')
    output.append(f'    connector_type         = aws_appflow_connector_profile.salesforce_connector_profile.connector_type')
    output.append(f'')
    output.append(f'    incremental_pull_config {{')
    output.append(f'      datetime_type_field_name = "SystemModstamp"')
    output.append(f'    }}')
    output.append(f'')
    output.append(f'    source_connector_properties {{')
    output.append(f'      salesforce {{')
    output.append(f'        object                  = "{object_name}"')
    output.append(f'        include_deleted_records = true')
    output.append(f'      }}')
    output.append(f'    }}')
    output.append(f'  }}')
    output.append(f'')
    output.append(f'  destination_flow_config {{')
    output.append(f'    connector_profile_name = aws_appflow_connector_profile.snowflake_connector_profile.name')
    output.append(f'    connector_type         = aws_appflow_connector_profile.snowflake_connector_profile.connector_type')
    output.append(f'')
    output.append(f'    destination_connector_properties {{')
    output.append(f'      snowflake {{')
    output.append(f'        bucket_prefix            = aws_s3_object.salesforce_stage_object.key')
    output.append(f'        intermediate_bucket_name = aws_s3_object.salesforce_stage_object.bucket')

    # Snowflake has issues with how Terraform qualifies the name.
    # output.append(f'        object                  = snowflake_table.salesforce_{object_name.lower()}_table.qualified_name')

    output.append(f'        object                   = "STAGING.SALESFORCE.{object_name.upper()}"')

    output.append(f'')
    output.append(f'        error_handling_config {{')
    output.append(f'          fail_on_first_destination_error = false')
    output.append(f'        }}')
    output.append(f'      }}')
    output.append(f'    }}')
    output.append(f'  }}')

    for row in rows:
        output.append(f'')
        output.append(f'  task {{')
        output.append(f'    destination_field = "{row['source_field'].upper()}"')
        output.append(f'    source_fields     = ["{row['source_field']}"]')
        output.append(f'    task_type         = "Map"')
        output.append(f'')
        output.append(f'    task_properties = {{')
        output.append(f'      "DESTINATION_DATA_TYPE" = "{row['destination_datatype']}"')
        output.append(f'      "SOURCE_DATA_TYPE"      = "{row['source_datatype']}"')
        output.append(f'    }}')
        output.append(f'')
        output.append(f'    connector_operator {{')
        output.append(f'      salesforce = "NO_OP"')
        output.append(f'    }}')
        output.append(f'  }}')

    output.append(f'')
    output.append(f'  task {{')
    output.append(f'    source_fields = [')

    for row in rows:
        output.append(f'      "{row['source_field']}",')

    output.append(f'    ]')
    output.append(f'    task_type = "Filter"')
    output.append(f'')
    output.append(f'    connector_operator {{')
    output.append(f'      salesforce = "PROJECTION"')
    output.append(f'    }}')
    output.append(f'  }}')
    output.append(f'')
    output.append(f'  trigger_config {{')
    output.append(f'    trigger_type = "Scheduled"')
    output.append(f'')
    output.append(f'    trigger_properties {{')
    output.append(f'      scheduled {{')
    output.append(f'        data_pull_mode      = "Incremental"')
    output.append(f'        schedule_expression = "rate(1days)"')

    tomorrow = datetime.now(timezone.utc) + timedelta(days=1)

    output.append(f'        schedule_start_time = "{tomorrow.strftime("%Y-%m-%dT08:00:00Z")}"')

    output.append(f'      }}')
    output.append(f'    }}')
    output.append(f'  }}')
    output.append(f'}}')
    output.append(f'')
    output.append(f'#')
    output.append(f'# Snowflake Table')
    output.append(f'#')
    output.append(f'')
    output.append(f'resource "snowflake_table" "salesforce_{object_name.lower()}" {{')
    output.append(f'  database = snowflake_schema.salesforce_schema.database')
    output.append(f'  name     = "{object_name.upper()}"')
    output.append(f'  schema   = snowflake_schema.salesforce_schema.name')

    for row in rows:
        output.append(f'')
        output.append(f'  column {{')
        output.append(f'    name = "{row['source_field'].upper()}"')
        output.append(f'    type = "{_DATABASE_DATATYPE_MAPPING[row['destination_datatype'].upper()]}"')
        output.append(f'  }}')

    output.append(f'}}')

    return('\n'.join(output))


if __name__ == "__main__":
    main()
