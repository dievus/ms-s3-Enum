import requests
import re
import os
import argparse
import textwrap
import sys

def banner():
    print('┌┬┐┌─┐  ╔═╗3  ╔═╗┌┐┌┬ ┬┌┬┐')
    print('│││└─┐  ╚═╗   ║╣ ││││ ││││')
    print('┴ ┴└─┘  ╚═╝   ╚═╝┘└┘└─┘┴ ┴')
    print('Public S3 File Downloader')
    print('Another tool by Mr Mayor\n')

def arg_handler():
    opt_parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, epilog=textwrap.dedent(
        '''python3 mss3enum.py -b bucket.s3.amazonaws.com -a'''))
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
    directory_name = args.bucket
    os.makedirs(directory_name, exist_ok=True)
    response = requests.get(url)
    xml_content = response.text
    prefixes = re.findall(r'<Prefix>(.*?)</Prefix>', xml_content)

    for prefix in prefixes:
        new_url = f"https://{args.bucket}?list-type=2&prefix={prefix}&delimiter=%2F&encoding-type=url"
        response = requests.get(new_url)
        print(f'\nUpdated URL: {new_url}')
        print('Open Files:\n' + '-' * 60)
        keys = re.findall(r'<Key>(.*?)</Key>', response.text)
        if keys:
            for key in keys:
                download_url = f'https://{args.bucket}/{key}'
                print(f'Downloading: {download_url}')
                file_response = requests.get(download_url, stream=True)
                if file_response.status_code == 200:
                    if not key.endswith('/'):
                        file_path = os.path.join(directory_name, key)
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        with open(file_path, 'wb') as file:
                            for data in file_response.iter_content(1024):
                                file.write(data)
                        print(f'Downloaded: {file_path}')
                        file_number += 1
                    else:
                        print(f'Skipped directory key: {key}')
                else:
                    print(
                        f'Failed to download {key}: {file_response.status_code}')
    print(
        f'\nDownloading complete. {file_number} files downloaded to the {directory_name} directory.')


if __name__ == "__main__":
    banner()
    arg_handler()
    main_func()
