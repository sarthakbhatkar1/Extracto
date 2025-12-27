import boto3
from botocore.exceptions import ClientError
from extracto.common.config.config_store import ConfigStore
import os
import io


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
        self.access_key_id = os.getenv('AWS_ACCESS_KEY_ID', self.config.AWS.AWS_ACCESS_KEY_ID)
        self.secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY', self.config.AWS.AWS_SECRET_ACCESS_KEY)
        self.region = os.getenv('AWS_S3_REGION', self.config.AWS_S3.AWS_S3_REGION)
        self.bucket = os.getenv('AWS_S3_BUCKET', self.config.AWS_S3.AWS_S3_BUCKET)

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
            error_message = f"{e}"
            print(f"Exception in uploading the document in AWS S3 bucket: {e}")
            if e.response['Error']['Code'] != 'AccessDenied':
                error_message = f"Failed to enable encryption on bucket {self.bucket}: {str(e)}"
            raise Exception(f"{error_message}")

    def create(self, file_data, remote_path):
        """
        Upload file data to S3 (Create).

        Args:
            file_data (bytes or str): The content of the file to upload (e.g., bytes for binary, str for text).
            remote_path (str): Destination key in S3 (e.g., 'Extracto/documents/sample.pdf').

        Returns:
            dict: Details of the uploaded file (e.g., bucket, key).

        Raises:
            ValueError: If file_data or remote_path is empty or invalid.
            ClientError: For S3 API errors (e.g., permissions, bucket not found).
        """
        if not file_data:
            raise ValueError("file_data cannot be empty")
        if not remote_path:
            raise ValueError("remote_path must be provided")

        # Convert string to bytes if necessary
        if isinstance(file_data, str):
            file_data = file_data.encode('utf-8')

        # Create a.py file-like object from bytes
        file_obj = io.BytesIO(file_data)

        try:
            self.s3_client.upload_fileobj(
                Fileobj=file_obj,
                Bucket=self.bucket,
                Key=remote_path,
                ExtraArgs={'ServerSideEncryption': 'AES256'}
            )
            return {"bucket": self.bucket, "key": remote_path}
        except ClientError as e:
            raise Exception(f"Failed to upload data to S3 bucket {self.bucket} at {remote_path}: {str(e)}")

    def read(self, remote_path=None):
        """
        List files or download a.py file from S3 (Read).

        Args:
            remote_path (str, optional): S3 key to download or folder prefix to list (e.g., 'Extracto/').
                                        If None, lists all files in bucket.

        Returns:
            list or bytes: List of file keys if remote_path is a.py prefix or None,
                          or file content if remote_path is a.py file.

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
                        # Treat as a.py folder prefix and list objects
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
        Rename or move a.py file in S3 (Update) by copying and deleting.

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
        Delete a.py file from S3 (Delete).

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


# # Example usage (for testing, can be removed in production)
# if __name__ == "__main__":
#     manager = S3FileManager()

#     # Create: Upload file data
#     file_content = b"Test content"  # Example bytes data
#     manager.create(file_content, "extracto/test.txt")

#     # Read: List files in Extracto folder
#     files = manager.read(remote_path="extracto/")
#     print("Files in Extracto:", files)

#     # Read: Download a.py file
#     content = manager.read("extracto/test.txt")
#     print("File content:", content.decode())

#     # Update: Rename a.py file
#     manager.update("extracto/test.txt", new_name="test_updated.txt")

#     # Delete: Remove a.py file
#     # manager.delete("extracto/test_updated.txt")
