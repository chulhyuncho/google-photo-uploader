import os
import pickle
import datetime
import requests
import urllib.parse
import time
import threading
import queue
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.appendonly']

def authenticate_google_photos():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("Error: credentials.json not found. Please place it in the project root.")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

class ProgressBarFile:
    def __init__(self, filepath, pbar):
        self.filepath = filepath
        self.file = open(filepath, 'rb')
        self.pbar = pbar

    def read(self, size=-1):
        chunk = self.file.read(size)
        if chunk:
            self.pbar.update(len(chunk))
        return chunk

    def seek(self, offset, whence=0):
        self.file.seek(offset, whence)

    def close(self):
        self.file.close()

def upload_media(creds, file_path, pbar):
    """Uploads the media file and returns an upload token."""
    upload_url = 'https://photoslibrary.googleapis.com/v1/uploads'
    
    filename = os.path.basename(file_path)
    encoded_filename = urllib.parse.quote(filename)
    
    headers = {
        'Authorization': f'Bearer {creds.token}',
        'Content-Type': 'application/octet-stream',
        'X-Google-Upload-File-Name': encoded_filename,
        'X-Google-Upload-Protocol': 'raw',
    }

    pbar_file = ProgressBarFile(file_path, pbar)

    try:
        response = requests.post(upload_url, headers=headers, data=pbar_file)
    finally:
        pbar_file.close()
    
    if response.status_code == 200:
        return response.text
    else:
        tqdm.write(f"Error uploading {file_path}: {response.status_code} - {response.text}")
        return None

def register_media_items_batch(creds, items):
    """Creates multiple media items in Google Photos with exponential backoff for 429 errors."""
    if not items:
        return []

    create_url = 'https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate'
    headers = {
        'Authorization': f'Bearer {creds.token}',
        'Content-Type': 'application/json',
    }
    
    new_media_items = []
    for token, path in items:
        new_media_items.append({
            "description": os.path.basename(path),
            "simpleMediaItem": {
                "uploadToken": token
            }
        })

    body = {"newMediaItems": new_media_items}
    
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            response = requests.post(create_url, headers=headers, json=body)
            if response.status_code == 429:
                tqdm.write(f"Rate limit hit during registration. Retrying in {retry_delay}s... (Attempt {attempt+1}/{max_retries})")
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
                
            response.raise_for_status()
            results = response.json().get('newMediaItemResults', [])
            
            success_paths = []
            for i, result in enumerate(results):
                status = result.get('status', {})
                file_path = items[i][1]
                if status.get('code') == 0 or status.get('message') == 'Success' or 'mediaItem' in result:
                    success_paths.append(file_path)
                else:
                    tqdm.write(f"Failed to register {file_path}: {status.get('message', 'Unknown error')}")
            
            return success_paths

        except requests.exceptions.RequestException as e:
            tqdm.write(f"HTTP request failed during registration batch: {e}")
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 429:
                     tqdm.write(f"Rate limit hit (429). Retrying in {retry_delay}s...")
                     time.sleep(retry_delay)
                     retry_delay *= 2
                     continue
                tqdm.write(f"Response from API: {e.response.text}")
            break
        except Exception as e:
            tqdm.write(f"Unexpected error during registration batch: {e}")
            break
            
    return []

def delete_empty_parents(path, root_path):
    """Recursively deletes empty parent directories up to root_path."""
    curr = os.path.dirname(path)
    # Don't delete the root_path itself or go above it
    if os.path.abspath(curr) == os.path.abspath(root_path) or not curr.startswith(root_path):
        return
        
    try:
        # Check if directory is empty
        if not os.listdir(curr):
            os.rmdir(curr)
            tqdm.write(f"Deleted empty folder: {curr}")
            # Recursively check the parent
            delete_empty_parents(curr, root_path)
    except Exception:
        # If we can't delete (e.g. not empty or permissions), just stop
        pass

def registration_worker(creds, reg_queue, root_path):
    """Worker thread that pulls items from queue and registers them in batches."""
    while True:
        items = []
        # Try to get up to 50 items
        try:
            # Wait for the first item
            item = reg_queue.get(timeout=1)
            if item == "SHUTDOWN":
                reg_queue.task_done()
                break
            items.append(item)
            
            # Try to get more items immediately without waiting
            while len(items) < 50:
                try:
                    next_item = reg_queue.get_nowait()
                    if next_item == "SHUTDOWN":
                        reg_queue.put(next_item)
                        break
                    items.append(next_item)
                except queue.Empty:
                    break
        except queue.Empty:
            continue

        if items:
            success_paths = register_media_items_batch(creds, items)
            for path in success_paths:
                try:
                    os.remove(path)
                    tqdm.write(f"Successfully uploaded and deleted: {path}")
                    # After deleting a file, try to clean up empty parents
                    delete_empty_parents(path, root_path)
                except Exception as e:
                    tqdm.write(f"Failed to delete {path}: {e}")
            
            for _ in range(len(items)):
                reg_queue.task_done()

def is_too_large(file_path, max_size_mb):
    """Checks if a file exceeds the maximum size limit (in MB)."""
    if max_size_mb is None:
        return False
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    return size_mb > max_size_mb

def process_single_file(creds, file_path, reg_queue, position=None, max_size_mb=None):
    """Uploads file and puts token into registration queue, with size check."""
    if not os.path.exists(file_path):
        return

    if is_too_large(file_path, max_size_mb):
        tqdm.write(f"Skipping {file_path}: size exceeds {max_size_mb}MB")
        return

    file_size = os.path.getsize(file_path)
    with tqdm(total=file_size, unit='B', unit_scale=True, desc=file_path, position=position, leave=False) as pbar:
        upload_token = upload_media(creds, file_path, pbar)
        if upload_token:
            reg_queue.put((upload_token, file_path))
        else:
             tqdm.write(f"Upload failed for: {file_path}")

def final_cleanup(folder_path):
    """Final pass to remove any empty directories in the folder_path."""
    for root, dirs, files in os.walk(folder_path, topdown=False):
        for name in dirs:
            dir_path = os.path.join(root, name)
            try:
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    tqdm.write(f"Final cleanup: Deleted empty folder {dir_path}")
            except Exception:
                pass

def scan_and_upload(creds, folder_path, max_workers=4, max_size_mb=None):
    """Scans folder and uploads files in parallel with batched registration, size filtering and folder cleanup."""
    valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.avi')
    files_to_upload = []
    
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.lower().endswith(valid_extensions):
                file_path = os.path.join(root, filename)
                if not is_too_large(file_path, max_size_mb):
                    files_to_upload.append(file_path)
                else:
                    tqdm.write(f"Skipping {file_path}: size exceeds limit")

    if not files_to_upload:
        print("No eligible files to upload (or all files were filtered out). Checking for empty folders...")
        final_cleanup(folder_path)
        return

    print(f"Found {len(files_to_upload)} files. Starting parallel upload and batched registration...")

    reg_queue = queue.Queue()
    reg_thread = threading.Thread(target=registration_worker, args=(creds, reg_queue, folder_path), daemon=True)
    reg_thread.start()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_single_file, creds, f, reg_queue, i % max_workers, max_size_mb): f for i, f in enumerate(files_to_upload)}
        for future in as_completed(futures):
            future.result()

    # Signal registration worker to finish and wait
    reg_queue.put("SHUTDOWN")
    reg_queue.join()
    reg_thread.join()
    
    # Final cleanup pass for any remaining empty folders (e.g. from skipped files)
    final_cleanup(folder_path)

class NewFileHandler(FileSystemEventHandler):
    def __init__(self, creds, executor, reg_queue, max_size_mb=None):
        self.creds = creds
        self.executor = executor
        self.reg_queue = reg_queue
        self.max_size_mb = max_size_mb
        self.valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.avi')

    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            filename = os.path.basename(file_path)
            if filename.lower().endswith(self.valid_extensions):
                if is_too_large(file_path, self.max_size_mb):
                    tqdm.write(f"Skipped new file (too large): {file_path}")
                    return
                tqdm.write(f"New file detected: {file_path}")
                self.executor.submit(self.delayed_process, file_path)

    def delayed_process(self, file_path):
        # Wait for file to be fully written
        time.sleep(2)
        process_single_file(self.creds, file_path, self.reg_queue, max_size_mb=self.max_size_mb)

def start_watching(creds, folder_path, max_size_mb=None):
    """Starts watching the folder with a shared thread pool, registration queue, and size filtering."""
    reg_queue = queue.Queue()
    reg_thread = threading.Thread(target=registration_worker, args=(creds, reg_queue), daemon=True)
    reg_thread.start()

    with ThreadPoolExecutor(max_workers=4) as executor:
        event_handler = NewFileHandler(creds, executor, reg_queue, max_size_mb=max_size_mb)
        observer = Observer()
        observer.schedule(event_handler, folder_path, recursive=True)
        observer.start()
        print(f"Watching folder (recursively): {folder_path}")
        if max_size_mb:
            print(f"Max size limit active: {max_size_mb}MB")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        
        reg_queue.put("SHUTDOWN")
        reg_queue.join()
        observer.join()
        reg_thread.join()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Upload photos to Google Photos and delete them immediately.')
    parser.add_argument('folder', help='Path to the folder to scan.')
    parser.add_argument('--watch', action='store_true', help='Watch the folder for new files.')
    parser.add_argument('--workers', type=int, default=4, help='Number of parallel upload workers.')
    parser.add_argument('--max-size', type=float, help='Maximum file size in MB to upload.')
    args = parser.parse_args()

    creds = authenticate_google_photos()
    if creds:
        if not os.path.isdir(args.folder):
            print(f"Error: {args.folder} is not a valid directory.")
        else:
            print(f"Scanning {args.folder}...")
            scan_and_upload(creds, args.folder, max_workers=args.workers, max_size_mb=args.max_size)
            
            if args.watch:
                start_watching(creds, args.folder, max_size_mb=args.max_size)
            else:
                print("Done.")



