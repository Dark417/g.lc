"""Create the DynamoDB table for LANGGRAPH_CHECKPOINTER=dynamodb (langgraph:memory on bedrock).

  cd backend && uv run python ../infra/aws/setup_state.py --region us-east-1

Schema expected by langgraph-checkpoint-aws DynamoDBSaver: PK (S) + SK (S), TTL on `ttl`.
Large checkpoints (>350 KB) go to S3 when S3_CHECKPOINT_BUCKET is set.
ElastiCache for Valkey (LANGGRAPH_CHECKPOINTER=valkey, REDIS_URL) is created in the console or
with `aws elasticache create-serverless-cache --engine valkey` - see infra/aws/README.md.
"""

import argparse

import boto3


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", default="us-east-1")
    parser.add_argument("--table", default="ai-sdk-checkpoints")
    args = parser.parse_args()

    ddb = boto3.client("dynamodb", region_name=args.region)
    ddb.create_table(
        TableName=args.table,
        KeySchema=[
            {"AttributeName": "PK", "KeyType": "HASH"},
            {"AttributeName": "SK", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "SK", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    ddb.get_waiter("table_exists").wait(TableName=args.table)
    ddb.update_time_to_live(
        TableName=args.table, TimeToLiveSpecification={"Enabled": True, "AttributeName": "ttl"}
    )
    print(f"DYNAMODB_CHECKPOINT_TABLE={args.table}")


if __name__ == "__main__":
    main()
