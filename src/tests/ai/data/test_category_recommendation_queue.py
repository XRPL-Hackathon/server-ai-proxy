import pytest
import json
from unittest.mock import MagicMock, patch
from src.main.ai.data.CategoryRecommendationQueue import CategoryRecommendationQueue


class TestCategoryRecommendationQueue:
    def setup_method(self):
        # 목업 SQS 클라이언트 생성
        self.mock_sqs_client = MagicMock()
        self.queue_url = "https://example.com/queue"
        
        # 테스트 대상 큐 생성
        self.queue = CategoryRecommendationQueue(self.mock_sqs_client, self.queue_url)
    
    def test_send_message_success(self):
        # given
        request_id = "test-request-id"
        file_id = "67dd86ac60a0a6d929904d47"
        user_id = "test-user-id"
        
        # SQS 응답 설정
        expected_response = {"MessageId": "1234567890"}
        self.mock_sqs_client.send_message.return_value = expected_response
        
        # when
        result = self.queue.send_message(request_id, file_id, user_id)
        
        # then
        expected_message_body = {
            'request_type': 'category_recommendation',
            'request_id': request_id,
            'user_id': user_id,
            'payload': {
                'file_id': file_id
            }
        }
        
        self.mock_sqs_client.send_message.assert_called_once_with(
            QueueUrl=self.queue_url,
            MessageGroupId=user_id,
            MessageDeduplicationId=request_id,
            MessageBody=json.dumps(expected_message_body)
        )
        assert result == expected_response
    
    def test_send_message_with_exception(self):
        # given
        request_id = "test-request-id"
        file_id = "67dd86ac60a0a6d929904d47"
        user_id = "test-user-id"
        
        # SQS 예외 발생 설정
        self.mock_sqs_client.send_message.side_effect = Exception("SQS error")
        
        # when/then
        with pytest.raises(Exception) as e:
            self.queue.send_message(request_id, file_id, user_id)
        
        assert "SQS error" in str(e.value)
        
        expected_message_body = {
            'request_type': 'category_recommendation',
            'request_id': request_id,
            'user_id': user_id,
            'payload': {
                'file_id': file_id
            }
        }
        
        self.mock_sqs_client.send_message.assert_called_once_with(
            QueueUrl=self.queue_url,
            MessageGroupId=user_id,
            MessageDeduplicationId=request_id,
            MessageBody=json.dumps(expected_message_body)
        ) 