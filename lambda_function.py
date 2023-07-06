import datetime
import logging
import json
import os
from email_metrics_handler import EmailMetricsHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def run(event, context):

    # Extract the email_identity from the event payload
    email_identity = event['email_identity']
    # Retrieve the S3 bucket name from the Lambda environment variable
    bucket_name = os.environ['S3_BUCKET_NAME']

    handler = EmailMetricsHandler()
    handler.process_email_metrics(email_identity, bucket_name)

    current_time = datetime.datetime.now().time()
    name = context.function_name
    logger.info(name + " ran at " + str(current_time) + " for " + email_identity)

    # Return a response indicating successful execution
    return {
        'statusCode': 200,
        'body': f'Email metrics processed successfully at {current_time} for {email_identity}'
    }
