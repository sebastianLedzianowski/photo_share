import boto3
from botocore.exceptions import ClientError
import json
from dotenv import load_dotenv
import os
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

class SecretsManager:
    @staticmethod
    def create_client():
        """
        Creates and returns a boto3 client for AWS Secrets Manager.

        Returns:
            client: A boto3 client for AWS Secrets Manager.
        """
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
        return client
    @staticmethod
    def get_secret(key):
        """
        Retrieve a secret value by key from AWS Secrets Manager.

        Parameters:
            key (str): The key for the secret value to retrieve.

        Returns:
            str: The secret value associated with the provided key if found, otherwise None.

        Raises:
            ClientError: An error occurred while trying to retrieve the secret from AWS Secrets Manager.
        """
        secret_name = os.getenv("SECRET_NAME")
        client = SecretsManager.create_client()

        try:
            get_secret_value_response = client.get_secret_value(SecretId=secret_name)
            secret = get_secret_value_response['SecretString']
            parsed_secret = json.loads(secret)
            value = parsed_secret.get(key)
            if value is not None:
                return value
            else:
                logging.info(f"Key '{key}' not found in the secret.")
                return None
        except ClientError as e:
            logging.error(f"Error retrieving secret: {e}")
            raise e
