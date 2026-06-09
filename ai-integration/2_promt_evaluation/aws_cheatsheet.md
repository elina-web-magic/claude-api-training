# AWS S3 CLI Cheat Sheet

## 1. List S3 Buckets and Contents

**Description:** View your S3 buckets or list objects within a specific bucket.

```bash
# List all buckets
aws s3 ls

# List contents of a bucket
aws s3 ls s3://your-bucket-name/

# List with detailed info (size, date)
aws s3 ls s3://your-bucket-name/ --recursive --human-readable --summarize
```

## 2. Copy Files Between Local and S3

**Description:** Upload files to S3 or download files from S3.

```bash
# Upload a file to S3
aws s3 cp myfile.txt s3://your-bucket-name/

# Download a file from S3
aws s3 cp s3://your-bucket-name/myfile.txt ./myfile.txt

# Sync entire directory (upload)
aws s3 sync ./local-folder s3://your-bucket-name/folder/

# Sync from S3 (download)
aws s3 sync s3://your-bucket-name/folder/ ./local-folder
```

## 3. Remove Objects from S3

**Description:** Delete files or entire buckets from S3.

```bash
# Delete a single object
aws s3 rm s3://your-bucket-name/myfile.txt

# Delete all objects in a folder
aws s3 rm s3://your-bucket-name/folder/ --recursive

# Delete an empty bucket
aws s3 rb s3://your-bucket-name

# Delete bucket with contents
aws s3 rb s3://your-bucket-name --force
```
