import requests
import re
import os
from urllib.parse import urlparse

def banner():
    print('┌┬┐┌─┐  ╔═╗3  ╔═╗┌┐┌┬ ┬┌┬┐')
    print('│││└─┐  ╚═╗   ║╣ ││││ ││││')
    print('┴ ┴└─┘  ╚═╝   ╚═╝┘└┘└─┘┴ ┴')
    print('Public S3 File Downloader')
    print('Another tool by Mr Mayor\n')

def main_func():
    directory_name = target_url
    os.makedirs(directory_name, exist_ok=True)
    response = requests.get(url)
    xml_content = response.text
    prefixes = re.findall(r'<Prefix>(.*?)</Prefix>', xml_content)

    for prefix in prefixes:
        new_url = f"https://{target_url}?list-type=2&prefix={prefix}&delimiter=%2F&encoding-type=url"
        response = requests.get(new_url)
        print(f'\nUpdated URL: {new_url}')
        print('Open Files:\n' + '-' * 60)
        keys = re.findall(r'<Key>(.*?)</Key>', response.text)
        if keys:
            for key in keys:
                download_url = f'https://{target_url}/{key}'
                print(f'Downloading: {download_url}')
                file_response = requests.get(download_url, stream=True)
                if file_response.status_code == 200:
                    if not key.endswith('/'):
                        file_path = os.path.join(directory_name, key)
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        with open(file_path, 'wb') as file:
                            # 1 KiB chunks
                            for data in file_response.iter_content(1024):
                                file.write(data)
                        print(f'Downloaded: {file_path}')
                    else:
                        print(f'Skipped directory key: {key}')
                else:
                    print(
                        f'Failed to download {key}: {file_response.status_code}')


if __name__ == "__main__":
    banner()
    target_url = input('Enter the target S3 bucket to check: ')
    url = f"https://{target_url}?list-type=2&prefix=&delimiter=%2F&encoding-type=url"
    main_func()
