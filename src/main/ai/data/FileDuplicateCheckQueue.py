import json
import hashlib

class FileDuplicateCheckQueue:
    def __init__(self, sqs_client, queue_url):
        self.sqs_client = sqs_client
        self.queue_url = queue_url
    
    def send_message(self, request_id: str, user_id: str, s3_bucket: str, s3_key: str):
        """SQS 큐에 메시지를 전송합니다."""
        message_body = {
            'request_type': 'file_duplicate_check_embedding_file',
            'request_id': request_id,
            'user_id': user_id,
            'payload': {
                's3_bucket': s3_bucket,
                's3_key': s3_key
            }
        }
        
        # MessageDeduplicationId는 알파벳, 숫자, 구두점만 포함 가능하므로 
        # request_id를 MD5 해시로 변환하여 사용합니다.
        deduplication_id = hashlib.md5(str(request_id).encode()).hexdigest()
        
        response = self.sqs_client.send_message(
            QueueUrl=self.queue_url,
            MessageGroupId=str(user_id),
            MessageDeduplicationId=deduplication_id,
            MessageBody=json.dumps(message_body),
        )
        
        return response 