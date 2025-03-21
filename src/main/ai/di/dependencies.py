import os
import boto3
from dotenv import load_dotenv

from src.main.ai.data.CategoryRecommendationRepository import CategoryRecommendationRepository
from src.main.ai.service.CategoryRecommendationService import CategoryRecommendationService
from src.main.ai.data.CategoryRecommendationQueue import CategoryRecommendationQueue
from src.main.config.mongodb import get_mongo_client

load_dotenv()


def get_category_recommendation_repository():
    client = get_mongo_client()
    return CategoryRecommendationRepository(client)


def get_category_recommendation_queue():
    if os.getenv('ENV') == 'local':
        aws_profile = os.getenv('AWS_PROFILE', 'default')
        session = boto3.Session(profile_name=aws_profile)
        sqs_client = session.client('sqs')
    else:
        sqs_client = boto3.client('sqs', region_name=os.getenv('AWS_REGION'))

    queue_url = os.getenv('SQS_REQUEST_QUEUE_URL')
    return CategoryRecommendationQueue(sqs_client, queue_url)


def get_category_recommendation_service():
    repository = get_category_recommendation_repository()
    queue = get_category_recommendation_queue()
    return CategoryRecommendationService(repository, queue)
