import threading as t
import requests
import os

from gi.repository import GLib

CACHE = GLib.get_user_cache_dir() + "/banana"
os.makedirs(CACHE, exist_ok=True)


def temp_download(*urls, cb=None) -> str:
    def f():
        files = []
        for url in urls:
            name = url.split("/")[-1]
            path = os.path.join(CACHE, name)

            if os.path.exists(path) is False:
                r = requests.get(url)
                r.raise_for_status()

                with open(path, "wb") as f:
                    f.write(r.content)
                    f.close()

            files.append(path)

        cb(*files)

    t.Thread(target=f).start()
