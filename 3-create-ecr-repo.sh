
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com
aws ecr create-repository --repository-name python-workers --image-scanning-configuration scanOnPush=true --region ${AWS_DEFAULT_REGION}