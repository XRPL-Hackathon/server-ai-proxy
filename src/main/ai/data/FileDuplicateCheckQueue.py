class FileDuplicateCheckQueue:
    def __init__(self, sqs_client, queue_url):
        self.sqs_client = sqs_client
        self.queue_url = queue_url
    
    def send_message(self, message: str):
        """SQS 큐에 메시지를 전송합니다."""
        response = self.sqs_client.send_message(
            QueueUrl=self.queue_url,
            MessageBody=message
        )
        
        return response 