The S3 bucket name has been shortened to use:

1. AWS Account ID
2. First part of the region (e.g., 'ap' from 'ap-southeast-1')
3. Unix timestamp

This creates shorter names like "123456789012-ap-1742892760" instead of "123456789012-ap-southeast-1-idea-management-stack-artifacts-1742892760"

This should resolve the "InvalidBucketName" error while still ensuring globally unique bucket names.