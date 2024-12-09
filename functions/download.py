import os
import requests


def unauth_download_func1(key, file_number, directory_name, args, bucket):
    file_number = file_number
    download_url = f"https://{bucket}/{key}"
    print(f"[info] Downloading: {key}")
    file_response = requests.get(download_url, stream=True, verify=False)
    if file_response.status_code == 200:
        if not key.endswith("/"):
            print(f"[info] Downloading: {key}")
            file_path = os.path.join(directory_name, key)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as file:
                for data in file_response.iter_content(1024):
                    file.write(data)
            print(f"[info] Downloaded: {key}")
            file_number += 1
        else:
            pass
    else:
        pass
    return file_number


def unauth_download_func2(key, file_number, directory_name, args, bucket):
    file_number = file_number
    download_url = f"https://{bucket}/{key}"
    file_response = requests.get(download_url, stream=True, verify=False)
    if file_response.status_code == 200:
        if not key.endswith("/"):
            print(f"[info] Downloading: {key}")
            file_path = os.path.join(directory_name, key)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as file:
                for data in file_response.iter_content(1024):
                    file.write(data)
            print(f"[info] Downloaded: {key}")
            file_number += 1
    else:
        pass
    return file_number


def bucket_handler(directory_name, s3_client, file_number, file_val, session, bucket):
    s3_response = s3_client.list_objects_v2(Bucket=bucket, Delimiter="/")
    # print(s3_response)
    if "CommonPrefixes" in s3_response:
        prefixes = [prefix["Prefix"] for prefix in s3_response["CommonPrefixes"]]
        print(f"Directories discovered for {bucket}:")
        print("-" * 80)
        for prefix in prefixes:
            if prefix == "":
                print("/")
                prefix == "/"
            else:
                print(prefix)
        for prefix in prefixes:
            print(f"\nChecking {prefix} directory for accessible files")
            print("-" * 80)
            subfolder_response = s3_client.list_objects_v2(
                Bucket=bucket, Prefix=prefix
            )
            if "Contents" in subfolder_response:
                keys = [content["Key"] for content in subfolder_response["Contents"]]
                if keys:
                    for key in keys:
                        if key == prefix:
                            pass
                        # if "CloudTrail-Digest" in key:
                        #     pass
                        else:
                            print(f"[info] File Discovered - {key}")
                    for key in keys:
                        # if "CloudTrail-Digest" in key:
                        #     # file_number -= 1
                        #     pass
                    # else:
                        try:
                            file_val = 0
                            version_response = s3_client.list_object_versions(
                                Bucket=bucket, Prefix=key
                            )
                            if "Versions" in version_response:
                                for version in version_response["Versions"]:
                                    version_id = version.get("VersionId", "null")
                                    latest_id = version.get("Key")
                                    is_latest_val = version.get("IsLatest", "True")
                                    if version_id == "null":
                                        print(f"[info] Downloading: {latest_id}")
                                        if not latest_id.endswith("/"):
                                            file_path = os.path.join(
                                                directory_name,
                                                latest_id.replace("/", os.sep),
                                            )
                                            os.makedirs(
                                                os.path.dirname(file_path),
                                                exist_ok=True,
                                            )
                                            with open(file_path, "wb") as file:
                                                s3_client.download_fileobj(
                                                    bucket, latest_id, file
                                                )
                                            print(f"[info] Downloaded: {latest_id}")
                                            file_number += 1
                                    elif version_id != "null":
                                        last_modified = version["LastModified"]
                                        last_modified_str = last_modified.strftime(
                                            "%Y-%m-%d %H:%M:%S"
                                        )
                                        if not key.endswith("/"):
                                            if file_val == 0:
                                                print(
                                                    f"[info] {latest_id} file identified with multiple versions available."
                                                )
                                                file_val = 1
                                            base_name = os.path.basename(latest_id)
                                            file_name_with_version = (
                                                f"{base_name}_version_{version_id}"
                                            )
                                            directory_path = os.path.dirname(latest_id)
                                            if is_latest_val:
                                                print(
                                                    f"[info] Downloading {latest_id} - Latest Version"
                                                )
                                                file_path = os.path.join(
                                                    directory_name,
                                                    key.replace("/", os.sep),
                                                )
                                                os.makedirs(
                                                    os.path.dirname(file_path),
                                                    exist_ok=True,
                                                )
                                            else:
                                                print(
                                                    f"[info] Downloading {latest_id} file with version ID: {version_id} - Last Modified: {last_modified_str}"
                                                )
                                                file_path = os.path.join(
                                                    directory_name,
                                                    directory_path,
                                                    file_name_with_version,
                                                )
                                                # Ensure the directory structure exists
                                                os.makedirs(
                                                    os.path.dirname(file_path),
                                                    exist_ok=True,
                                                )
                                            version_response = s3_client.get_object(
                                                Bucket=bucket,
                                                Key=latest_id,
                                                VersionId=version_id,
                                            )
                                            file_content = version_response[
                                                "Body"
                                            ].read()
                                            with open(file_path, "wb") as file:
                                                file.write(file_content)
                                            if is_latest_val:
                                                print(f"[info] Downloaded: {key}")
                                            else:
                                                print(
                                                    f"[info] Downloaded: {key} saved as {file_name_with_version}"
                                                )
                                            file_number += 1
                                        else:
                                            s3_client = session.client(
                                                "s3"
                                            )  # Modified as a signed request is likely required to access deleted files
                                            if key.endswith("/"):
                                                if key == latest_id:
                                                    pass
                                                else:
                                                    print(
                                                        f"[info] {latest_id} file identified which may have been previously deleted"
                                                    )
                                                    print(
                                                        f"[info] Downloading {latest_id}\n[info] Version ID: {version_id}\n[info]Last Modified: {last_modified_str}"
                                                    )
                                                    directory_path = os.path.dirname(
                                                        latest_id
                                                    )
                                                    latest_id = str(latest_id)
                                                    version_response = (
                                                        s3_client.list_object_versions(
                                                            Bucket=bucket,
                                                            Prefix=key,
                                                        )
                                                    )
                                                    try:
                                                        file_path = os.path.join(
                                                            directory_name,
                                                            latest_id.replace(
                                                                "/", os.sep
                                                            ),
                                                        )
                                                        os.makedirs(
                                                            os.path.dirname(file_path),
                                                            exist_ok=True,
                                                        )
                                                        version_response = (
                                                            s3_client.get_object(
                                                                Bucket=bucket,
                                                                Key=latest_id,
                                                                VersionId=version_id,
                                                            )
                                                        )
                                                        file_content = version_response[
                                                            "Body"
                                                        ].read()
                                                        with open(
                                                            file_path, "wb"
                                                        ) as file:
                                                            file.write(file_content)
                                                            print(
                                                                f"[info] Downloaded: {latest_id}"
                                                            )
                                                            file_number += 1
                                                    except Exception as e:
                                                        continue

                        except Exception as e:
                            print(f"[error]Error downloading {key}: {e}")
        print(
            f"\n[info] Downloading complete. {file_number} file(s) downloaded to the {directory_name} directory.\n"
        )
    elif "CommonPrefixes" not in s3_response:
        print(f"No prefixes (directories) identified for {bucket}. Downloading files directly.")
        print("-" * 80)
        response = s3_client.list_objects_v2(Bucket=bucket)
        if "Contents" in response:
            for obj in response["Contents"]:
                key = obj["Key"]
                # List versions for the current object
                try:
                    version_response = s3_client.list_object_versions(
                        Bucket=bucket, Prefix=key
                    )
                    if "Versions" in version_response:
                        for version in version_response["Versions"]:
                            print(
                                f"Version ID: {version['VersionId']}, IsLatest: {version['IsLatest']}, LastModified: {version['LastModified']}"
                            )
                    else:
                        print("No versions found for this object.")
                except Exception:
                    pass
                print(f"[info] Downloading: {key}")
                # if not latest_id.endswith("/"):
                file_path = os.path.join(directory_name, key.replace("/", os.sep))
                os.makedirs(
                    os.path.dirname(file_path),
                    exist_ok=True,
                )
                with open(file_path, "wb") as file:
                    s3_client.download_fileobj(bucket, key, file)
                print(f"[info] Downloaded: {key}")
                file_number += 1
        print(
            f"\n[info] Downloading complete. {file_number} file(s) downloaded to the {directory_name} directory.\n"
        )
    else:
        print("No keys to process.")
