import boto3

def list_s3_buckets():
    """List all S3 buckets in the AWS account."""
    s3_client = boto3.client('s3')
    response = s3_client.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    return buckets