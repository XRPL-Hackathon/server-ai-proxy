import os
import json
import boto3
from dotenv import load_dotenv

load_dotenv()


class CategoryRecommendationQueue:
    def __init__(self, sqs_client: boto3.client, queue_url: str):
        self.sqs = sqs_client
        self.queue_url = queue_url

    def send_message(self, request_id: str, file_id: str, user_id: str):
        try:
            message_body = {
                'request_type': 'category_recommendation',
                'request_id': request_id,
                'user_id': str(user_id),
                'payload': {
                    'file_id': file_id
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