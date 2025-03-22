import os
import json
import boto3
from dotenv import load_dotenv

load_dotenv()


class FileDuplicateCheckQueue:
    def __init__(self, sqs_client: boto3.client, queue_url: str):
        self.sqs = sqs_client
        self.queue_url = queue_url

    def send_message(self, request_id: str, user_id: str, s3_bucket: str, s3_key: str):
        try:
            message_body = {
                'request_type': 'file_duplicate_check_embedding_file',
                'request_id': request_id,
                'user_id': str(user_id),
                'payload': {
                    's3_bucket': s3_bucket,
                    's3_key': s3_key
                }
            }
            
            response = self.sqs.send_message(
                QueueUrl=self.queue_url,
                MessageGroupId=str(user_id),
                MessageDeduplicationId=str(request_id),
                MessageBody=json.dumps(message_body)
            )
            
            return response
        except Exception as e:
            print(f"Error sending message to SQS: {e}")
            raise 