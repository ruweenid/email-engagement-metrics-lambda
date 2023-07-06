import boto3
import csv
from datetime import datetime, timedelta
import uuid


class EmailMetricsHandler:
    def __init__(self):
        self.vdm_client = boto3.client('sesv2')
        self.s3_client = boto3.client('s3')
        self.start_time = None
        self.end_time = None
        self.unique_id = None
        self.email_identity = None

    def generate_unique_id(self):
        self.unique_id = uuid.uuid4()

    def set_time_range(self):
        self.end_time = datetime.now()
        self.start_time = self.end_time - timedelta(days=1)

    def format_timestamps(self):
        start_time_str = self.start_time.strftime('%Y-%m-%d')
        end_time_str = self.end_time.strftime('%Y-%m-%d')
        return start_time_str, end_time_str

    def get_metric_data(self, metric):
        start_time_str, end_time_str = self.format_timestamps()
        query = {
            'Id': str(self.unique_id),
            'Namespace': 'VDM',
            'Metric': metric,
            'Dimensions': {
                'EMAIL_IDENTITY': self.email_identity,
            },
            'StartDate': start_time_str,
            'EndDate': end_time_str
        }
        response = self.vdm_client.batch_get_metric_data(Queries=[query])
        values = response['Results'][0]['Values']
        return values[0] if values else 0

    def save_values_to_csv(self, metrics, metrics_values):
        start_time_str, end_time_str = self.format_timestamps()
        output_file = f'/tmp/{self.email_identity}_{start_time_str}_{end_time_str}.csv'

        with open(output_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(metrics)
            writer.writerow(metrics_values)

        print(f'Values saved to {output_file}')

    def upload_to_s3(self, file_path, bucket_name):
        key = file_path.split('/')[-1]  # Use the file name as the S3 object key

        self.s3_client.upload_file(file_path, bucket_name, key)

        print(f'File uploaded to S3 bucket: s3://{bucket_name}/{key}')

    def process_email_metrics(self, email_identity, bucket_name):
        self.generate_unique_id()
        self.set_time_range()
        self.email_identity = email_identity

        metrics = [
            'SEND', 'OPEN', 'COMPLAINT', 'PERMANENT_BOUNCE', 'TRANSIENT_BOUNCE',
            'CLICK', 'DELIVERY', 'DELIVERY_OPEN', 'DELIVERY_CLICK', 'DELIVERY_COMPLAINT'
        ]
        metrics_values = [self.get_metric_data(metric) for metric in metrics]

        print(*metrics_values[:2], sep='\n')  

        self.save_values_to_csv(metrics, metrics_values)

        start_time_str, end_time_str = self.format_timestamps()
        output_file = f'/tmp/{self.email_identity}_{start_time_str}_{end_time_str}.csv'

        self.upload_to_s3(output_file, bucket_name)
