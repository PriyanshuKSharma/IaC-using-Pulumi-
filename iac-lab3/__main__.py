import pulumi
import pulumi_aws as aws
import json

# Load IAM user details from config.json
with open("config.json", "r") as f:
    config = json.load(f)

iam_username = config.get("iam_username")

# Create an AWS IAM User
iam_user = aws.iam.User(iam_username, name=iam_username)

# Store the IAM credentials securely in AWS Secrets Manager
secret = aws.secretsmanager.Secret(
    f"{iam_username}-secret",
    name=f"{iam_username}-credentials"
)

# Create a secret version with IAM user details (password must be set externally)
secret_version = aws.secretsmanager.SecretVersion(
    f"{iam_username}-secret-version",
    secret_id=secret.id,
    secret_string=pulumi.Output.json_dumps({
        "username": iam_username
    })
)

# Export IAM User ARN and Secret ARN
pulumi.export("iam_user_arn", iam_user.arn)
pulumi.export("iam_secret_arn", secret.arn)
