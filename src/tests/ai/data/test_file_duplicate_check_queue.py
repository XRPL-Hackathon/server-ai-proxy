import pytest
import json
import hashlib
from unittest.mock import MagicMock, patch

from src.main.ai.data.FileDuplicateCheckQueue import FileDuplicateCheckQueue


class TestFileDuplicateCheckQueue:
    def setup_method(self):
        # 목업 SQS 클라이언트 생성
        self.mock_sqs = MagicMock()
        self.test_queue_url = "https://sqs.ap-northeast-2.amazonaws.com/123456789012/file-duplicate-check-queue.fifo"
        
        # 테스트 대상 큐 생성
        self.queue = FileDuplicateCheckQueue(self.mock_sqs, self.test_queue_url)
        
        # 테스트 공통 데이터
        self.test_request_id = "6123456789abcdef01234567"
        self.test_user_id = "12345678-1234-5678-1234-567812345678"
        self.test_s3_bucket = "test-bucket"
        self.test_s3_key = "example.pdf"
    
    def test_send_message_success(self):
        # given
        expected_message_body = {
            'request_type': 'file_duplicate_check_embedding_file',
            'request_id': self.test_request_id,
            'user_id': self.test_user_id,
            'payload': {
                's3_bucket': self.test_s3_bucket,
                's3_key': self.test_s3_key
            }
        }
        
        expected_deduplication_id = hashlib.md5(str(self.test_request_id).encode()).hexdigest()
        
        expected_response = {"MessageId": "12345"}
        self.mock_sqs.send_message.return_value = expected_response
        
        # when
        response = self.queue.send_message(
            request_id=self.test_request_id,
            user_id=self.test_user_id,
            s3_bucket=self.test_s3_bucket,
            s3_key=self.test_s3_key
        )
        
        # then
        self.mock_sqs.send_message.assert_called_once_with(
            QueueUrl=self.test_queue_url,
            MessageGroupId=self.test_user_id,
            MessageDeduplicationId=expected_deduplication_id,
            MessageBody=json.dumps(expected_message_body)
        )
        assert response == expected_response
    
    def test_send_message_exception(self):
        # given
        self.mock_sqs.send_message.side_effect = Exception("SQS Error")
        
        # when & then
        with pytest.raises(Exception) as exc_info:
            self.queue.send_message(
                request_id=self.test_request_id,
                user_id=self.test_user_id,
                s3_bucket=self.test_s3_bucket,
                s3_key=self.test_s3_key
            )
        
        assert str(exc_info.value) == "SQS Error" 