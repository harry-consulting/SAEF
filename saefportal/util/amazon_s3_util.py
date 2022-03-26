import boto3


def get_aws_account_username(access_key_id, secret_access_key):
    account_id = boto3.client("sts", aws_access_key_id=access_key_id,
                              aws_secret_access_key=secret_access_key).get_caller_identity()["Account"]

    organizations = boto3.client("organizations", aws_access_key_id=access_key_id,
                                 aws_secret_access_key=secret_access_key)

    return organizations.describe_account(AccountId=account_id)["Account"]["Name"]
