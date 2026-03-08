import boto3
import json

def create_s3_buckets():
    """Create S3 buckets for RetailIQ"""
    s3 = boto3.client('s3', region_name='ap-south-1')
    
    buckets = [
        'retailiq-raw-data-varun',
        'retailiq-processed-data-varun',
        'retailiq-model-artifacts-varun'
    ]
    
    for bucket in buckets:
        try:
            s3.create_bucket(
                Bucket=bucket,
                CreateBucketConfiguration={'LocationConstraint': 'ap-south-1'}
            )
            print(f"✅ Created bucket: {bucket}")
        except Exception as e:
            print(f"⚠️  Bucket {bucket} might already exist or error: {e}")

def create_dynamodb_tables():
    """Create DynamoDB tables for RetailIQ"""
    dynamodb = boto3.client('dynamodb', region_name='ap-south-1')
    
    tables = [
        {
            'TableName': 'retailiq-metadata',
            'KeySchema': [
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'metadata_type_id', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'metadata_type_id', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        },
        {
            'TableName': 'retailiq-model-registry',
            'KeySchema': [
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'model_type_version', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'model_type_version', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        }
    ]
    
    for table in tables:
        try:
            dynamodb.create_table(**table)
            print(f"✅ Created table: {table['TableName']}")
        except Exception as e:
            print(f"⚠️  Table {table['TableName']} might already exist or error: {e}")

if __name__ == '__main__':
    print("🚀 Setting up AWS resources...")
    create_s3_buckets()
    create_dynamodb_tables()
    print("✅ AWS setup complete!")
