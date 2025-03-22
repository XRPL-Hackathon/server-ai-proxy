class FileDuplicateCheckQueue:
    def __init__(self, sqs_client, queue_url):
        self.sqs_client = sqs_client
        self.queue_url = queue_url
    
    def send_message(self, message: str, user_id: str, request_id: str):
        """SQS 큐에 메시지를 전송합니다."""
        print(message)
        response = self.sqs_client.send_message(
            QueueUrl=self.queue_url,
            MessageGroupId=str(user_id),
                MessageDeduplicationId=str(request_id),
            MessageBody=message,

        )
        
        
        return response 