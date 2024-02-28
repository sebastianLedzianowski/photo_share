import boto3
from botocore.exceptions import ClientError
import json
from dotenv import load_dotenv
import os

load_dotenv()

def get_secret(key):
    secret_name = os.getenv("SECRET_NAME")
    region_name = os.getenv("REGION_NAME")
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        secret = get_secret_value_response['SecretString']
        parsed_secret = json.loads(secret)
        value = parsed_secret.get(key)
        if value is not None:
            print(f"Successfully retrieved value for key '{key}'")
            return value
        else:
            print(f"Key '{key}' not found in the secret.")
            return None
    except ClientError as e:
        print(f"Error retrieving secret: {e}")
        raise e
