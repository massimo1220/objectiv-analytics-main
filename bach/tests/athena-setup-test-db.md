# Initialize database - Testing
Below are instructions for setting up Athena and S3 for functional tests.

**Important** - All descriptions, code fragments, and configuration in this section assume that:
1. The aws-account-id is `123456789012`
2. The s3 staging bucket (to be created) is named `obj-automated-tests`

When setting up a new Athena/S3 environment make sure to edit those values appropriately.


## Create Athena DataCatalog, Athena WorkGroup, and S3 bucket

```bash
aws --region eu-west-1 athena create-data-catalog \
    --name automated_tests \
    --type GLUE \
    --description "DataCatalog for automated tests" \
    --parameters catalog-id=123456789012


aws --region eu-west-1 athena create-work-group \
    --name automated_tests_work_group

aws --region eu-west-1 s3api create-bucket \
    --bucket obj-automated-tests \
    --create-bucket-configuration LocationConstraint=eu-west-1
```

## Create Policies

Added manually using web interface. TODO: add commands here

### s3-obj-automated-tests-readwrite
name: `s3-obj-automated-tests-readwrite`
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:ListBucket",
                "s3:DeleteObject",
                "s3:GetBucketLocation"
            ],
            "Resource": [
                "arn:aws:s3:::obj-automated-tests",
                "arn:aws:s3:::obj-automated-tests/*"
            ]
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": "s3:ListAllMyBuckets",
            "Resource": "*"
        }
    ]
}

```

### athena-objectiv-automated-tests
name: `athena-objectiv-automated-tests`
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "athena:UpdateDataCatalog",
                "athena:GetTableMetadata",
                "athena:StartQueryExecution",
                "athena:GetQueryResults",
                "athena:GetDatabase",
                "athena:GetDataCatalog",
                "athena:DeleteNamedQuery",
                "athena:DeletePreparedStatement",
                "athena:GetNamedQuery",
                "athena:ListQueryExecutions",
                "athena:GetWorkGroup",
                "athena:UpdateNamedQuery",
                "athena:StopQueryExecution",
                "athena:BatchGetPreparedStatement",
                "athena:CreatePreparedStatement",
                "athena:GetQueryResultsStream",
                "athena:UpdatePreparedStatement",
                "athena:GetPreparedStatement",
                "athena:ListTagsForResource",
                "athena:ListNamedQueries",
                "athena:CreateNamedQuery",
                "athena:ListDatabases",
                "athena:GetQueryExecution",
                "athena:ListTableMetadata",
                "athena:BatchGetNamedQuery",
                "athena:ListPreparedStatements",
                "athena:BatchGetQueryExecution"
            ],
            "Resource": [
                "arn:aws:athena:eu-west-1:123456789012:workgroup/automated_tests_work_group",
                "arn:aws:athena:eu-west-1:123456789012:datacatalog/automated_tests"
            ]
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "athena:ListEngineVersions",
                "athena:ListDataCatalogs",
                "athena:ListWorkGroups"
            ],
            "Resource": "*"
        }
    ]
}
```

## Add User and Attach Policies
user: objectiv-automated-tests
```bash
aws --region eu-west-1 iam create-user \
    --user-name objectiv-automated-tests

aws --region eu-west-1 iam attach-user-policy \
    --user-name objectiv-automated-tests \
    --policy-arn arn:aws:iam::${AWS_ACCOUNT_ID}:policy/s3-obj-automated-tests-readwrite

aws --region eu-west-1 iam attach-user-policy \
    --user-name objectiv-automated-tests \
    --policy-arn arn:aws:iam::${AWS_ACCOUNT_ID}:policy/athena-objectiv-automated-tests

```


## Create Database
```sql
CREATE DATABASE automated_tests.bach_test;
```
