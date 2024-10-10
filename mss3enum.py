import requests
import re
import os
import argparse
import textwrap
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def banner():
    print('┌┬┐┌─┐  ╔═╗3  ╔═╗┌┐┌┬ ┬┌┬┐')
    print('│││└─┐  ╚═╗   ║╣ ││││ ││││')
    print('┴ ┴└─┘  ╚═╝   ╚═╝┘└┘└─┘┴ ┴')
    print('Public S3 File Downloader')
    print('Another tool by Mr Mayor\n')


def arg_handler():
    opt_parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, epilog=textwrap.dedent(
        '''python3 mss3enum.py '''))
    opt_parser_target = opt_parser.add_argument_group('Target S3 Bucket')
    opt_parser_target.add_argument(
        '-b', '--bucket', help='Sets the S3 bucket name to enumerate.', required=True)
    opt_parser_anon = opt_parser.add_argument_group('Anonymous Enumeration')
    opt_parser_anon.add_argument(
        '-a', '--anon', help='Checks for files available with anonymous access.', action='store_true'
    )
    opt_parser_auth = opt_parser.add_argument_group(
        'Authenticated Enumeration - ***To be implemented***')
    opt_parser_auth.add_argument(
        '-ak', '--accesskey', help='Sets the AWS access key to use.')
    opt_parser_auth.add_argument(
        '-sk', '--secretkey', help='Sets the AWS secret key to use.')
    global args
    args = opt_parser.parse_args()
    if len(sys.argv) <= 1:
        opt_parser.print_help()
        opt_parser.exit()
    if not args.bucket:
        print("An S3 bucket is required as an argument.")
        opt_parser.print_help()
        opt_parser.exit()


def main_func():
    file_number = 0
    url = f"https://{args.bucket}?list-type=2&prefix=&delimiter=%2F&encoding-type=url"
    try:
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            directory_name = args.bucket
            os.makedirs(directory_name, exist_ok=True)
            verify_url = f'https://{args.bucket}'
            verify_response = requests.head(verify_url, verify=False)
            for header, value in verify_response.headers.items():
                if 'x-amz-bucket-region' in header:
                    print('Bucket region identified')
                    print(f"{header}: {value}")
            xml_content = response.text
            prefixes = re.findall(r'<Prefix>(.*?)</Prefix>', xml_content)
            print('Directories discovered:')
            for prefix in prefixes:
                if prefix == '':
                    print('/')
                else:
                    print(prefix)
            for prefix in prefixes:
                if prefix == '':
                    print(f'\nChecking / directory for accessible files')
                    print('-'*60)
                    new_url = f"https://{args.bucket}?list-type=2&prefix={prefix}&delimiter=%2F&encoding-type=url"
                    response = requests.get(new_url, verify=False)
                    error_message = re.findall(
                        r'<Message>(.*?)</Message>', response.text)
                    if error_message:
                        for error in error_message:
                            print(f'{prefix} - {error}\n')
                            pass
                    else:
                        keys = re.findall(r'<Key>(.*?)</Key>', response.text)
                        for key in keys:
                            print(f'File Discovered - {key}')
                        if keys:
                            for key in keys:
                                download_url = f'https://{args.bucket}/{key}'
                                print(f'Downloading: {key}')
                                file_response = requests.get(
                                    download_url, stream=True, verify=False)
                                if file_response.status_code == 200:
                                    if not key.endswith('/'):
                                        file_path = os.path.join(
                                            directory_name, key)
                                        os.makedirs(os.path.dirname(
                                            file_path), exist_ok=True)
                                        with open(file_path, 'wb') as file:
                                            for data in file_response.iter_content(1024):
                                                file.write(data)
                                        print(f'Downloaded: {key}')

                                        file_number += 1
                                    else:
                                        pass
                                else:
                                    pass
                            print('\n')
                else:
                    print(f'Checking {prefix} directory for accessible files')
                    print('-'*60)
                    new_url = f"https://{args.bucket}?list-type=2&prefix={prefix}&delimiter=%2F&encoding-type=url"
                    response = requests.get(new_url, verify=False)
                    error_message = re.findall(
                        r'<Message>(.*?)</Message>', response.text)
                    if error_message:
                        for error in error_message:
                            print(f'{prefix} - {error}\n')
                            pass
                    else:
                        keys = re.findall(r'<Key>(.*?)</Key>', response.text)
                        for key in keys:
                            print(f'File Discovered - {key}')
                        if keys:
                            for key in keys:
                                download_url = f'https://{args.bucket}/{key}'
                                print(f'Downloading: {key}')
                                file_response = requests.get(
                                    download_url, stream=True, verify=False)
                                if file_response.status_code == 200:
                                    if not key.endswith('/'):
                                        file_path = os.path.join(
                                            directory_name, key)
                                        os.makedirs(os.path.dirname(
                                            file_path), exist_ok=True)
                                        with open(file_path, 'wb') as file:
                                            for data in file_response.iter_content(1024):
                                                file.write(data)
                                        print(f'Downloaded: {key}')
                                        file_number += 1
                                    else:
                                        pass
                                else:
                                    pass
                            print('\n')
            print(
                f'Downloading complete. {file_number} files downloaded to the {directory_name} directory.')
        elif response.status_code == 403:
            verify_url = f'https://{args.bucket}'
            verify_response = requests.head(verify_url, verify=False)
            for header, value in verify_response.headers.items():
                if 'x-amz-bucket-region' in header:
                    print('Bucket region identified')
                    print(f"{header}: {value}")
            print('You do not have privileges to access this bucket.')
            quit()
        elif response.status_code == 404:
            print('The S3 bucket does not exist.')
            quit()
        else:
            print('Some error occurred that prevented you from accessing the bucket.')
            print(response.status_code)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    banner()
    arg_handler()
    main_func()
