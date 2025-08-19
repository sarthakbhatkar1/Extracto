import boto3
from botocore.exceptions import ClientError
from extracto.common.config.config_store import ConfigStore
import os
from pathlib import Path


class S3FileManager:
    def __init__(self, config_store=None):
        """
        Initialize the S3 file manager with credentials from ConfigStore or environment variables.

        Args:
            config_store (ConfigStore, optional): Instance of ConfigStore to retrieve AWS credentials.
        """
        # Initialize ConfigStore if not provided
        self.config = config_store or ConfigStore()

        # Get AWS credentials (prefer environment variables over config file)
        self.access_key_id = os.getenv('AWS_ACCESS_KEY_ID', self.config.AWS.ACCESS_KEY_ID)
        self.secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY', self.config.AWS.SECRET_ACCESS_KEY)
        self.region = os.getenv('AWS_REGION', self.config.AWS.REGION)
        self.bucket = os.getenv('S3_BUCKET', self.config.AWS.S3_BUCKET)

        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            region_name=self.region
        )

        # Ensure bucket has server-side encryption
        try:
            self.s3_client.put_bucket_encryption(
                Bucket=self.bucket,
                ServerSideEncryptionConfiguration={
                    'Rules': [{'ApplyServerSideEncryptionByDefault': {'SSEAlgorithm': 'AES256'}}]
                }
            )
        except ClientError as e:
            if e.response['Error']['Code'] != 'AccessDenied':
                raise Exception(f"Failed to enable encryption on bucket {self.bucket}: {str(e)}")

    def create(self, local_path, remote_path=None):
        """
        Upload a file to S3 (Create).

        Args:
            local_path (str): Path to the local file to upload.
            remote_path (str, optional): Destination key in S3 (e.g., 'Extracto/documents/sample.pdf').
                                        Defaults to file name.

        Returns:
            dict: Details of the uploaded file (e.g., bucket, key).

        Raises:
            FileNotFoundError: If local_path doesn't exist.
            ClientError: For S3 API errors (e.g., permissions, bucket not found).
        """
        local_path = Path(local_path)
        if not local_path.exists():
            raise FileNotFoundError(f"Local file {local_path} not found")

        remote_path = remote_path or local_path.name

        try:
            self.s3_client.upload_file(
                Filename=str(local_path),
                Bucket=self.bucket,
                Key=remote_path,
                ExtraArgs={'ServerSideEncryption': 'AES256'}
            )
            return {"bucket": self.bucket, "key": remote_path}
        except ClientError as e:
            raise Exception(f"Failed to upload {local_path} to S3 bucket {self.bucket}: {str(e)}")

    def read(self, remote_path=None):
        """
        List files or download a file from S3 (Read).

        Args:
            remote_path (str, optional): S3 key to download or folder prefix to list (e.g., 'Extracto/').
                                        If None, lists all files in bucket.

        Returns:
            list or bytes: List of file keys if remote_path is a prefix or None,
                          or file content if remote_path is a file.

        Raises:
            ClientError: For S3 API errors (e.g., file not found, permissions).
        """
        try:
            if remote_path:
                try:
                    # Attempt to download the file
                    response = self.s3_client.get_object(Bucket=self.bucket, Key=remote_path)
                    return response['Body'].read()
                except ClientError as e:
                    if e.response['Error']['Code'] == 'NoSuchKey':
                        # Treat as a folder prefix and list objects
                        response = self.s3_client.list_objects_v2(
                            Bucket=self.bucket,
                            Prefix=remote_path.rstrip('/')
                        )
                        return [obj['Key'] for obj in response.get('Contents', [])]
                    raise Exception(f"Failed to read {remote_path} from S3 bucket {self.bucket}: {str(e)}")
            else:
                # List all files in bucket
                response = self.s3_client.list_objects_v2(Bucket=self.bucket)
                return [obj['Key'] for obj in response.get('Contents', [])]
        except ClientError as e:
            raise Exception(f"Failed to read from S3 bucket {self.bucket}: {str(e)}")

    def update(self, remote_path, new_name=None, new_path=None):
        """
        Rename or move a file in S3 (Update) by copying and deleting.

        Args:
            remote_path (str): Current S3 key of the file (e.g., 'Extracto/documents/sample.pdf').
            new_name (str, optional): New file name (stays in same folder).
            new_path (str, optional): New S3 key (full path) to move the file to.

        Returns:
            dict: Details of the updated file (e.g., bucket, new key).

        Raises:
            ClientError: For S3 API errors (e.g., file not found, permissions).
            ValueError: If neither new_name nor new_path is provided.
        """
        if not (new_name or new_path):
            raise ValueError("Either new_name or new_path must be provided")

        try:
            # Verify the source file exists
            self.s3_client.head_object(Bucket=self.bucket, Key=remote_path)

            # Determine new key
            if new_name:
                prefix = remote_path.rsplit('/', 1)[0] if '/' in remote_path else ''
                new_key = f"{prefix}/{new_name}" if prefix else new_name
            else:
                new_key = new_path

            # Copy to new key with encryption
            self.s3_client.copy_object(
                Bucket=self.bucket,
                CopySource={'Bucket': self.bucket, 'Key': remote_path},
                Key=new_key,
                ServerSideEncryption='AES256'
            )
            # Delete original file
            self.s3_client.delete_object(Bucket=self.bucket, Key=remote_path)

            return {"bucket": self.bucket, "key": new_key}
        except ClientError as e:
            raise Exception(f"Failed to update {remote_path} in S3 bucket {self.bucket}: {str(e)}")

    def delete(self, remote_path):
        """
        Delete a file from S3 (Delete).

        Args:
            remote_path (str): S3 key of the file to delete (e.g., 'Extracto/documents/sample.pdf').

        Returns:
            bool: True if deletion was successful.

        Raises:
            ClientError: For S3 API errors (e.g., file not found, permissions).
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=remote_path)
            return True
        except ClientError as e:
            raise Exception(f"Failed to delete {remote_path} from S3 bucket {self.bucket}: {str(e)}")


# Example usage (for testing, can be removed in production)
if __name__ == "__main__":
    manager = S3FileManager()

    # Create: Upload a file
    with open("test.txt", "w") as f:
        f.write("Test content")
    manager.create("test.txt", "Extracto/test.txt")

    # Read: List files in Extracto folder
    files = manager.read("Extracto/")
    print("Files in Extracto:", files)

    # Read: Download a file
    content = manager.read("Extracto/test.txt")
    print("File content:", content.decode())

    # Update: Rename a file
    manager.update("Extracto/test.txt", new_name="test_updated.txt")

    # Delete: Remove a file
    manager.delete("Extracto/test_updated.txt")