# Utility - Salesforce -> AppFlow -> Snowflake

Creating Terraform for AppFlow that moves data from Salesforce to Snowflake can
be daunting due to the large amount of fields that SObjects tend to have. This
simple utility that will generate Terraform to create the AppFlow in AWS and the
table in Snowflake.

I've created this utility to help me create a pipeline from Salesforce in to
Snowflake quickly. It is certainly not perfect but I hope others can find use
in this as well.

## Usage

### Step 1: Install Dependencies

I've tried to use as little dependencies as possible but we use
`simple-salesforce` to get the objects fields.

```sh
$ pip install -r requirements.txt
```

### Step 2: Salesforce Credentials

Set the following environment variables to access your Salesforce instance:
`SFDC_USERNAME`, `SFDC_PASSWORD`, and `SFDC_SECURITYTOKEN`.

Example:
```sh
$ export SFDC_USERNAME="username@example.com"
$ export SFDC_PASSWORD="*******"
$ export SFDC_SECURITYTOKEN="*********************"
```

### Step 3: Get Object Fields

We're going to create a CSV with all the fields of the SObject so that we can
make adjustments (if desired) before we create the Terraform.

```sh
$ python sobject.py [sobject]
```

Example:
```sh
$ python sobject.py Contact
```

### Step 4: (Optional) Make Adjustments

> [!TIP]
> This step is completely optional as you can make adjustments on the generated
> Terraform. However, I find it is easier to do in a CSV than looking through
> the many lines of Terraform configuration.

Open the object_name.csv file to make adjustments to how the Terraform and table
will be created.

The CSV should have the following columns:
* `source_field` - Do not modify. This is the API Name of the object's field.
* `source_datatype` - Data type that AppFlow expects.
* `destination_datatype` - Data type of Snowflake.
* `salesforce_datatype` - Unused but helpful while making adjustments.

1. Remove any rows you wish to exclude from the Flow.
2. Update any `source_datatype` or `destination_datatype`. Be careful as this
   may cause errors.

Supported `source_datatype` values:
* Mystery values from AWS

Supported `destination_datatype` values:
* BOOLEAN
* CURRENCY
* DATE
* DATETIME
* FLOAT
* NUMBER
* STRING
* TEXT

> [!WARNING]
> This script is unable to determine the datatype of all fields. Seach for
> "REPLACE_ME" in the `source_datatype` and `destination_datatype` column and
> manually replace. If you're unsure, `STRING` is a safe bet.

> [!CAUTION]
> Salesforce does not keep up-to-date information in Formula fields. Since these
> fields can be recreated using other fields, I recommend removing these fields
> from your AppFlow Flow. Keeping them will only frustrate your analysts and,
> therefore, eventually you.

### Step 5: Generate Terraform

Finally, we use `terraform.py` to get our Terraform configuration.

```sh
$ python terraform.py Contact.csv > contact.tf
```

> [!CAUTION]
> Your work is not done!
>
> The generated terraform is incomplete. You'll still need to update
> `source_flow_config` and `destination_flow_config` with the correct
> connectors.

We have used the following resources as placeholders for your actual
configuration:

```tf
#
# AWS AppFlow Connector Profiles
#

resource "aws_appflow_connector_profile" "salesforce_connector_profile" {
	... YOUR CONFIGURATION HERE ...
}

resource "aws_appflow_connector_profile" "snowflake_connector_profile" {
	... YOUR CONFIGURATION HERE ...
}

#
# AWS S3
#

resource "aws_s3_bucket" "staging_bucket" {
  bucket = "YOUR-UNIQUE-BUCKET-NAME-HERE-00000000000"
}

resource "aws_s3_object" "salesforce_stage_object" {
  bucket = aws_s3_bucket.staging_bucket.id
  key    = "/"
}

#
# Snowflake
#
resource "snowflake_database" "staging_database" {
  name    = "STAGING"
}

resource "snowflake_schema" "staging_salesforce_schema" {
  database = snowflake_database.staging_database.name
  name     = "SALESFORCE"
}
```
