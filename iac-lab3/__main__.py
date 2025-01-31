"""An AWS Python Pulumi program"""

import pulumi
from pulumi_aws import aws
import json

#Load IAM user credentials from config.json
with open("config.json", "r") as f:
  config=json.load(f)


iam_username=config.get("iam_username")
iam_password=config.get("iam_password")

# Create an AWS IAM user
iam_user=aws.iam.USer(iam_usernamm, name=iam_username)

#Create a login profile with an externally provided password
login_profile = aws.iam.UserLoginProfile(
    f"{iam_username}-login",
    user=iam_user.name,
    password=iam_password,
    password_reset_required=True
)

# Export IAM User ARN as an output
pulumi.export("iam_user_arn", iam_user.arn)


# Create a login profile with an externally provided password
login_profile = aws.iam.UserLoginProfile(
    f"{iam_username}-login",
    user=iam_user.name,
    password=iam_password,
    password_reset_required=True
)

# Export IAM User ARN as an output
pulumi.export("iam_user_arn", iam_user.arn)