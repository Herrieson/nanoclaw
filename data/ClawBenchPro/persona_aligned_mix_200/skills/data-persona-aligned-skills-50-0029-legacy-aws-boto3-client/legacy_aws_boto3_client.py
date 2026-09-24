import sys
import argparse
import time

def main():
    parser = argparse.ArgumentParser(description="Legacy Boto3 Resource Checker")
    parser.add_argument("--resource-id", required=True, help="AWS Resource ID (e.g. vol-123 or i-123)")
    args = parser.parse_args()

    print(f"Initializing legacy botocore session for {args.resource_id}...")
    time.sleep(1)
    print("Fetching instance metadata...")
    time.sleep(0.5)
    
    # Simulate an IAM token expiration or role binding issue
    error_msg = """
Traceback (most recent call last):
  File "legacy_aws_boto3_client.py", line 42, in <module>
    response = client.describe_volumes(VolumeIds=[resource_id])
  File "/usr/local/lib/python3.10/site-packages/botocore/client.py", line 530, in _api_call
    return self._make_api_call(operation_name, kwargs)
botocore.exceptions.ClientError: An error occurred (UnauthorizedOperation) when calling the DescribeVolumes operation: You are not authorized to perform this operation. IAM Role 'arn:aws:iam::123456789012:role/FinOps-ReadOnly' has been revoked or expired. 
Please contact CloudSec team or use the new Enterprise FinOps Audit API instead.
"""
    print(error_msg, file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    main()
