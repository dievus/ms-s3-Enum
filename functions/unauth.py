import os
import requests
import re
from .download import unauth_download_func1, unauth_download_func2


def unauth_func(args, bucket):
    directory_name = bucket
    prefix = ""
    if args.recursive:
        url = f"https://{bucket}?list-type=2&prefix=&encoding-type=url"
        new_url = f"https://{bucket}?list-type=2&prefix={prefix}&encoding-type=url"
    else:
        url = (
            f"https://{bucket}?list-type=2&prefix=&delimiter=%2F&encoding-type=url"
        )
        new_url = f"https://{bucket}?list-type=2&prefix={prefix}&delimiter=%2F&encoding-type=url"
    file_number = 0
    try:
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            verify_url = f"https://{bucket}"
            verify_response = requests.head(verify_url, verify=False)
            for header, value in verify_response.headers.items():
                if "x-amz-bucket-region" in header:
                    print("Bucket region identified")
                    print(f"{header}: {value}\n")
            os.makedirs(directory_name, exist_ok=True)
            os.chdir(directory_name)
            xml_content = response.text
            prefixes = re.findall(r"<Prefix>(.*?)</Prefix>", xml_content)
            print("Directories discovered:")
            print("-" * 80)
            for prefix in prefixes:
                if prefix == "":
                    print("/")
                else:
                    print(prefix)
            for prefix in prefixes:
                if prefix == "":
                    print(f"\nChecking / directory for accessible files")
                    print("-" * 80)
                    response = requests.get(new_url, verify=False)
                    error_message = re.findall(
                        r"<Message>(.*?)</Message>", response.text
                    )
                    if error_message:
                        for error in error_message:
                            print(f"{prefix} - {error}\n")
                            pass
                    else:
                        keys = re.findall(r"<Key>(.*?)</Key>", response.text)
                        if keys:
                            for key in keys:
                                print(f"[info] File Discovered - {key}")
                            for key in keys:
                                file_number = unauth_download_func1(
                                    key, file_number, directory_name, args
                                )
                else:
                    print(f"Checking {prefix} directory for accessible files")
                    print("-" * 80)
                    new_url = f"https://{bucket}?list-type=2&prefix={prefix}&delimiter=%2F&encoding-type=url"
                    response = requests.get(new_url, verify=False)
                    error_message = re.findall(
                        r"<Message>(.*?)</Message>", response.text
                    )
                    if error_message:
                        for error in error_message:
                            print(f"{prefix} - {error}\n")
                            pass
                    else:
                        keys = re.findall(r"<Key>(.*?)</Key>", response.text)
                        if keys:
                            for key in keys:
                                print(f"[info] File Discovered - {key}")
                            for key in keys:
                                file_number = unauth_download_func2(
                                    key, file_number, directory_name, args
                                )
            print(
                f"\n[info] Downloading complete. {file_number} files downloaded to the {directory_name} directory."
            )
            if file_number < 5 and not args.recursive:
                print(
                    f"Recommend using the -rc flag to check for recursivity in the bucket."
                )
        elif response.status_code == 403:
            verify_url = f"https://{bucket}"
            verify_response = requests.head(verify_url, verify=False)
            for header, value in verify_response.headers.items():
                if "x-amz-bucket-region" in header:
                    print("Bucket region identified")
                    print(f"{header}: {value}")
            print("\nYou do not have privileges to access this bucket.")
            if not args.recursive:
                print(
                    "Consider checking for recursivity using the -rc flag and try again."
                )
            quit()
        elif response.status_code == 404:
            print("The S3 bucket does not exist.")
            quit()
        else:
            print("Some error occurred that prevented you from accessing the bucket.")
            print(response.status_code)
    except KeyboardInterrupt:
        print("You either fat fingered this, or something else. Either way, quitting!")
