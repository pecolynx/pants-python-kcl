
`poetry run python venv/lib/python3.10/site-packages/samples/amazon_kclpy_helper.py --print_command --java /usr/bin/java --properties app.properties --log-configuration logback.xml`
```
aws configure --profile=localstack
AWS Access Key ID [None]: dummy
AWS Secret Access Key [None]: dummy
Default region name [None]: ap-northeast-1
Default output format [None]: json

```


https://docs.localstack.cloud/user-guide/aws/kinesis/



```
awslocal kinesis create-stream \
  --stream-name lambda-stream \
  --shard-count 1 \
  --region ap-northeast-1
```

```
awslocal kinesis describe-stream \
  --stream-name lambda-stream \
  --region ap-northeast-1
```
https://docs.localstack.cloud/user-guide/aws/dynamodb/
<!-- ```
awslocal dynamodb create-table \
    --table-name APPLICATION_NAME \
    --key-schema AttributeName=id,KeyType=HASH \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --billing-mode PAY_PER_REQUEST \
    --region ap-northeast-1
``` -->

```
awslocal dynamodb describe-table \
    --table-name APPLICATION_NAME \
    --query 'Table.ItemCount' \
    --region ap-northeast-1
```
```
awslocal dynamodb scan \
    --table-name APPLICATION_NAME \
    --region ap-northeast-1
```

```
export AWS_ACCESS_KEY_ID=dummy
export AWS_SECRET_ACCESS_KEY=dummy
export AWS_PROFILE=localstack
export AWS_ENDPOINT_URL=http://127.0.0.1:4566
`poetry run python venv/lib/python3.10/site-packages/samples/amazon_kclpy_helper.py --print_command --java /usr/bin/java --properties app.properties`
`poetry run python venv/lib/python3.10/site-packages/scamples/amazon_kclpy_helper.py --print_command --java /usr/bin/java --properties app.properties --log-configuration logback.xml`
```


awslocal dynamodb get-item \
    --key '{"leaseKey": {"S": "shardId-000000000000"}}' \
    --table-name APPLICATION_NAME \
    --region ap-northeast-1



awslocal kinesis put-record --stream-name lambda-stream --partition-key 123 --region ap-northeast-1 --data "ZGF0YTAwMQ=="
awslocal kinesis put-record --stream-name lambda-stream --partition-key 123 --region ap-northeast-1 --data "ZGF0YTAwMg=="
awslocal kinesis put-record --stream-name lambda-stream --partition-key 123 --region ap-northeast-1 --data "ZGF0YTAwMw=="
awslocal kinesis put-record --stream-name lambda-stream --partition-key 123 --region ap-northeast-1 --data "ZGF0YTAwNA=="
awslocal kinesis put-record --stream-name lambda-stream --partition-key 123 --region ap-northeast-1 --data "ZGF0YTAwNQ=="


JAVA_LOG_LEVEL=INFO ./run.sh


awslocal dynamodb create-table \
    --table-name APPLICATION_NAME \
    --key-schema AttributeName=leaseKey,KeyType=HASH \
    --attribute-definitions AttributeName=leaseKey,AttributeType=S \
    --billing-mode PAY_PER_REQUEST \
    --region ap-northeast-1


```
awslocal dynamodb describe-table \
    --table-name APPLICATION_NAME \
    --region ap-northeast-1
```

manual
```
{
    "Table": {
        "AttributeDefinitions": [
            {
                "AttributeName": "leaseKey",
                "AttributeType": "S"
            }
        ],
        "TableName": "APPLICATION_NAME",
        "KeySchema": [
            {
                "AttributeName": "leaseKey",
                "KeyType": "HASH"
            }
        ],
        "TableStatus": "ACTIVE",
        "CreationDateTime": "2024-03-05T11:34:27.255000+09:00",
        "ProvisionedThroughput": {
            "LastIncreaseDateTime": "1970-01-01T09:00:00+09:00",
            "LastDecreaseDateTime": "1970-01-01T09:00:00+09:00",
            "NumberOfDecreasesToday": 0,
            "ReadCapacityUnits": 0,
            "WriteCapacityUnits": 0
        },
        "TableSizeBytes": 0,
        "ItemCount": 0,
        "TableArn": "arn:aws:dynamodb:ap-northeast-1:000000000000:table/APPLICATION_NAME",
        "TableId": "61f655d9-df6c-414e-ace5-1bdc03a9ddcb",
        "BillingModeSummary": {
            "BillingMode": "PAY_PER_REQUEST",
            "LastUpdateToPayPerRequestDateTime": "2024-03-05T11:34:27.255000+09:00"
        },
        "Replicas": [],
        "DeletionProtectionEnabled": false
    }
}
```

zidou
```
{
    "Table": {
        "AttributeDefinitions": [
            {
                "AttributeName": "leaseKey",
                "AttributeType": "S"
            }
        ],
        "TableName": "APPLICATION_NAME",
        "KeySchema": [
            {
                "AttributeName": "leaseKey",
                "KeyType": "HASH"
            }
        ],
        "TableStatus": "ACTIVE",
        "CreationDateTime": "2024-03-03T10:51:02.874000+09:00",
        "ProvisionedThroughput": {
            "LastIncreaseDateTime": "1970-01-01T09:00:00+09:00",
            "LastDecreaseDateTime": "1970-01-01T09:00:00+09:00",
            "NumberOfDecreasesToday": 0,
            "ReadCapacityUnits": 0,
            "WriteCapacityUnits": 0
        },
        "TableSizeBytes": 280,
        "ItemCount": 1,
        "TableArn": "arn:aws:dynamodb:ap-northeast-1:000000000000:table/APPLICATION_NAME",
        "TableId": "97980971-2af6-4a01-a0b3-08e5fa00f4a8",
        "BillingModeSummary": {
            "BillingMode": "PAY_PER_REQUEST",
            "LastUpdateToPayPerRequestDateTime": "2024-03-03T10:51:02.874000+09:00"
        },
        "Replicas": [],
        "DeletionProtectionEnabled": false
    }
}
```