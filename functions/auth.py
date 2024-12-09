import boto3.exceptions
from botocore.exceptions import ClientError
import os
from .download import bucket_handler


def bucket_versioning_func(s3_client, args, bucket):
    try:
        bucket_versioning = s3_client.get_bucket_versioning(Bucket=bucket)
        print(bucket_versioning)
    except ClientError as e:
        pass


def identity_call(sts_client, args):  # Queries and outputs information about the current account
    username = None
    arn = None
    # try:
    identity = sts_client.get_caller_identity()
    if identity:
        print(f"\nSecurity Token Service (STS) information")
        print("-" * 80)
    userid = identity.get("UserId")
    print(userid)
    account = identity.get("Account")
    arn = identity.get("Arn")
    print(f"UserId: {userid}")
    print(f"Account: {account}")
    print(f"Arn: {identity.get('Arn')}")
    username = arn.split("user/")[1]
    print(f"Username: {username}")
    return username, arn
    # except Exception as e:
    #     print(e)
    #     print('here in exception')
    #     return None, None


def bucket_region_enum(directory_name, s3_client, file_number, file_val, session, args, arn, bucket):
    bucket_name_dict = []  # Queries and outputs information about the current bucket
    try:
        region_response = s3_client.head_bucket(Bucket=bucket)
        if region_response:
            print("\nAWS S3 Bucket Region Information")
            print("-" * 80)
            region = region_response["ResponseMetadata"]["HTTPHeaders"].get(
                "x-amz-bucket-region", None
            )
            print("Bucket region identified")
            print(f"x-amz-bucket-region: {region}\n")
            return region
        try:
            bucket_acl_check = s3_client.get_bucket_acl(Bucket=bucket)
            if bucket_acl_check:
                print("AWS S3 Bucket ACL Information")
                print("-" * 80)
                print(bucket_acl_check)
        except Exception:
            pass
    except Exception:
        pass
    try:
        bucket_policy = s3_client.get_bucket_policy(Bucket=bucket)
        if bucket_policy:
            print(f"\nAttempting to list buckets owned by {arn}")
            print("-" * 80)
            print(bucket_policy(["Policy"]))
    except Exception:
        pass
    try:
        list_bucket_vals = s3_client.list_buckets()
        if list_bucket_vals:
            print(f'\n{arn} appears to have privileges to list buckets.')
            print(f"\nAttempting to list buckets owned by {arn}")
            print("-" * 80)
            # print(list_bucket_vals)
            if "ResponseMetadata" in list_bucket_vals:
                bucket_names = [bucket['Name'] for bucket in list_bucket_vals['Buckets']]
                if bucket_names:
                    print('\nBucket(s) found')
                    print('-'*80)
                    owner_name = list_bucket_vals['Owner']['DisplayName']
                    for bucket_val in bucket_names:
                        print(f'{bucket_val} - Owner: {owner_name}')
                        bucket_name_dict.append(bucket_val)
    except Exception:
        pass
    for bucket_val_to_download in bucket_name_dict:
        download_file_val = input(f'\nDo you want to attempt to download files from {bucket_val_to_download}? (y/n) ')
        if download_file_val.lower() == 'y':
            directory_name = bucket_val_to_download
            file_number = 0
            bucket_handler(directory_name, s3_client, file_number, file_val, session, bucket_val_to_download)
        else:
            pass
def iam_policy_check(iam_client, arn, username, args):  # Queries and outputs information about IAM policies
    policy_arn_values = []
    try:
        iam_policy_response = iam_client.list_attached_user_policies(UserName=username)
        if iam_policy_response:
            print(f"Attached IAM policies for {arn}")
            print("-" * 80)
        if "AttachedPolicies" in iam_policy_response:
            for policy in iam_policy_response["AttachedPolicies"]:
                policy_name = policy.get("PolicyName")
                policy_arn = policy.get("PolicyArn")
                print(f"Policy Name: {policy_name}")
                print(f"Policy Arn: {policy_arn}")
                policy_arn_values.append(policy_arn)

    except Exception as e:
        pass


def secrets_manager_check(iam_client, arn, region, args):  # Queries and outputs SecretsManager information if available
    try:
        secrets_manager_session = boto3.Session(aws_access_key_id=args.accesskey,aws_secret_access_key=args.secretkey,region_name=region,)
        secrets_manager_client = secrets_manager_session.client("secretsmanager")
        secret_response = secrets_manager_client.list_secrets()
        if secret_response:
            print("Secrets Manager List(s)")
            print("-" * 80)
        if "SecretList" in secret_response:
            for secret in secret_response["SecretList"]:
                name = secret.get("Name")
                description = secret.get("Description")
                arn = secret.get("ARN")
                try:
                    secret_value_response = secrets_manager_client.get_secret_value(
                        SecretId=name
                    )
                    secret_value = secret_value_response.get("SecretString")
                    print(f"Name: {name}")
                    print(f"Description: {description}")
                    print(f"ARN: {arn}")
                    try:
                        policy_arn_info = iam_client.get_policy(PolicyArn=arn)
                        print(policy_arn_info)
                    except Exception:
                        pass
                    print(f"Value: {secret_value}")
                    print("-" * 80 + "\n")
                except Exception as e:
                    pass
        else:
            print("No secrets found.")
    except Exception:
        pass


def auth_func(args, bucket):
    if bucket:
        directory_name = bucket
    else:
        directory_name = ''
    file_number = 0
    file_val = 0
    session = ""
    region = ""
    username = ""
    arn = ""
    bucket = ""

    try:
        if args.region:
            region = args.region
        if args.sesstoken:
            session = boto3.Session(
                aws_access_key_id=args.accesskey,
                aws_secret_access_key=args.secretkey,
                aws_session_token=args.sesstoken,
            )
        else:
            session = boto3.Session(
                aws_access_key_id=args.accesskey, aws_secret_access_key=args.secretkey
            )
            # s3_client = session.client("s3", config=botocore.config.Config(signature_version=botocore.UNSIGNED))
        # if args.unsigned:
        #     s3_client = session.client(
        #         "s3", config=botocore.config.Config(signature_version=botocore.UNSIGNED)
        #     )
        #     sts_client = session.client(
        #         "sts", config=botocore.config.Config(signature_version=botocore.UNSIGNED)
        #     )
        #     iam_client = session.client(
        #         "iam", config=botocore.config.Config(signature_version=botocore.UNSIGNED)
        #     )
        # else:
        s3_client = session.client("s3")
        sts_client = session.client("sts")
        iam_client = session.client("iam")
        username, arn = identity_call(sts_client, args)
        region = bucket_region_enum(directory_name, s3_client, file_number, file_val, session, args, arn, bucket)
        iam_policy_check(iam_client, arn, username, args)
        secrets_manager_check(iam_client, arn, region, args)
        if bucket:
            # try:
            bucket_versioning_func(s3_client, args, bucket)
            os.makedirs(directory_name, exist_ok=True)
            os.chdir(directory_name)
            file_number = bucket_handler(directory_name, s3_client, file_number, file_val, session, args, bucket)
    except ClientError as e:
        if e.response["Error"]["Code"] == "403":
            print("[error] You do not have privileges to access this bucket.")
            pass
        elif e.response["Error"]["Code"] == "404":
            print("[error] The S3 bucket does not exist.")
            quit()
        elif e.response["Error"]["Code"] == "400":
            print("[error] A bad request was made to the server.")
            quit()
        elif e.response["Error"]["Code"] == "AccessDenied":
            print("[error] Invalid permissions for this task.")
        elif e.response["Error"]["Code"] == "ExpiredToken":
            print("[error] The security token used has expired.")
        elif e.response["Error"]["Code"] == "MissingAuthenticationToken":
            print("Missing authentication token.")
        elif e.response["Error"]["Code"] == "InvalidClientTokenId":
            print("[error] The Client Token ID is invalid.")
        elif e.response == TypeError:
            print("[error] Some error prevented enumeration.")
        else:
            print("[error] Some error occurred that prevented you from accessing the bucket.")
            print(e.response)
    except KeyboardInterrupt:
        print("You either fat fingered this, or something else. Either way, quitting!")
