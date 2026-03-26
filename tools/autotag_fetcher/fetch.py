import imghdr
import os
import sys
from datetime import datetime, timezone

import requests
import json
import io

from PIL import ImageFile

from shared_utils.env import Env

# docker run --rm -p 5000:5000 ghcr.io/danbooru/autotagger

FILENAME_EXPORT = 'exported_urls.json'
EXPORT_PATH_TPL = 'output_' + FILENAME_EXPORT + '/result_'
IMAGE_URL = "http://localhost:7071"
TAGGING_URL = "http://localhost:5000/evaluate"
# TAGGING_URL = "https://autotagger.donmai.us/evaluate"


def send_image_as_blob(image_url, target_url):
    """
    Downloads an image from a URL and sends it as a blob via a POST request.

    Parameters:
    - image_url (str): The URL of the image to download and send.
    - target_url (str): The target endpoint to send the POST request.

    Returns:
    - None
    """

    try:
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        image_response = requests.get(image_url, stream=True)
        if image_response.status_code == 200:
            image_type = imghdr.what(None, h=image_response.content)
            mem_file = io.BytesIO(image_response.content)
            files = {'file': (f'file.{image_type}', mem_file, f'image/{image_type}')}
        else:
            raise Exception(f"Failed to download image. Status code: {image_response.status_code}")

        response = requests.post(target_url, files=files, data={"format": "json"})

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f'Request failed for url:"{image_url}" with status code "{response.status_code}" details: "{response.text}"')

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return [{'filename': '', 'tags': {}}]

def get_processed_ids(output_file):
    ids = []

    dir = os.path.dirname(output_file)
    for file in os.listdir(dir):
        if not file.endswith(".json"): continue
        file_path = os.path.join(dir, file)
        with open(file_path, "r") as f:
            data = json.load(f)
            ids.extend([img["id"] for img in data["images"]])

    return ids

def show_usage():
    print("Usage: python tools/autotag_fetcher _path_to_env_config_file_")

def fetch_tags():
    if len(sys.argv) > 1:
        conf = sys.argv[1]
    else:
        show_usage()
        return

    conf = os.path.abspath(conf)

    if not os.path.exists(conf):
        show_usage()
        print(f'File at {conf} does not exist')
        return



    Env.apply_config(conf)

    path = os.path.join(Env.TMP_PATH, FILENAME_EXPORT)

    with open(path, "r") as f:
        image_urls = json.load(f)

    image_urls = image_urls['json_urls']
    tagger_url = TAGGING_URL
    source_url = IMAGE_URL
    output_file = os.path.join(Env.TMP_PATH, EXPORT_PATH_TPL)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    processed_ids = get_processed_ids(output_file)
    # print(processed_ids)

    all_tags = {'tags': [], 'images': []}

    time = datetime.now(tz=timezone.utc).timestamp()
    flush_rate = 20
    count = 1
    new_data = 0
    max = len(image_urls)
    for img in image_urls:
        print(f"({count}/{max}) {'(v) ' if img['id'] in processed_ids else ''}Processing: {img['id']}", flush=True)

        if img['id'] in processed_ids:
            count += 1
            continue

        file_tags = send_image_as_blob(f"{source_url}{img['url']}", tagger_url)

        for item in file_tags:
            for tag in item['tags'].keys():
                if tag not in all_tags['tags']:
                    all_tags['tags'].append(tag)
            tags = {all_tags['tags'].index(key): int(value * 100) for key, value in item['tags'].items()}
            all_tags['images'].append({"id": img['id'], "timestamp": time, "tags": tags})

        count += 1

        if (count % flush_rate == 0 or count >= max) and len(all_tags['images']) > 0:
            outname = f"{output_file}{count - flush_rate}_{count - 1}.json"
            with open(outname, "w") as file:
                json.dump(all_tags, file, indent=4)
                all_tags = {'tags': [], 'images': []}

            print(f"Flushing tags from {count - flush_rate} to {count - 1} into {outname}")


# Example usage
if __name__ == "__main__":
    fetch_tags()