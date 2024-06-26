#!/usr/bin/env python3

from asyncio import run, gather
from sys import argv
from math import ceil
from traceback import format_exc
from os import path, makedirs
from gcloud.aio.auth import Token
from gcloud.aio.storage import Storage

SCOPES = ["https://www.googleapis.com/auth/cloud-platform.read-only"]
PARALLEL_DOWNLOADS = 5
TIMEOUT = 30

"""
script that simply mirrors a GCS bucket to local files
"""


async def main(bucket_name: str, prefix: str, service_file: str, options: dict = {}):

    try:
        token = Token(service_file=service_file, scopes=SCOPES)
    except Exception as e:
        quit(e)

    try:
        params = {'prefix': prefix}
        async with Storage(token=token) as storage:
            objects = []
            while True:
                _ = await storage.list_objects(bucket_name, params=params, timeout=TIMEOUT)
                items = _.get('items', [])
                objects.extend(items)
                if next_page_token := _.get('nextPageToken'):
                    params.update({'pageToken': next_page_token})
                else:
                    break
            await storage.close()
    except Exception as e:
        await storage.close()
        await token.close()
        raise e

    object_names = tuple([obj['name'] for obj in objects if int(obj.get('size', 0)) != 0])  # ignore zero-byte objects

    if verbose := options.get('verbose', True):
        print(f"Downloading {len(object_names)} non-zero objects from bucket {bucket_name}/{prefix}...")

    try:
        if not path.exists(prefix):
            makedirs(prefix)

        pages = ceil(len(object_names) / PARALLEL_DOWNLOADS)
        async with Storage(token=token) as storage:
            for page in range(0, pages):
                start = page * PARALLEL_DOWNLOADS
                end = start + PARALLEL_DOWNLOADS
                o = object_names[start:end]
                print(o)
                tasks = [storage.download_to_filename(bucket_name, object_name, object_name) for object_name in o]
                await gather(*tasks)
    except Exception as e:
        await storage.close()
        await token.close()
        raise e

    await storage.close()
    await token.close()


if __name__ == '__main__':

    try:
        arg_names = ['bucket_name', 'prefix', 'service_file']
        if len(argv) > len(arg_names):
            args = [argv[i+1] for i, v in enumerate(arg_names)]
            run(main(args[0], args[1], args[2]))
        else:
            message = f"Usage: {argv[0]}"
            for arg_name in arg_names:
                message += f" <{arg_name}>"
            quit(message)
    except Exception as e:
        quit(format_exc())
    

