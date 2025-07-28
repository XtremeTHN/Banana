from ..modules.utils import Blueprint, Thread
from ..modules.gamebanana.types import SubmissionInfoFileSource
from gi.repository import Gtk, Adw, GLib

import requests
import queue
import time


def fmt(size):
    return GLib.format_size_for_display(size)


@Blueprint("sidebar-mod")
class Mod(Gtk.Box):
    __gtype_name__ = "SidebarMod"

    mod_name: Gtk.Label = Gtk.Template.Child()
    mode_filename: Gtk.Label = Gtk.Template.Child()

    downloaded: Gtk.Label = Gtk.Template.Child()
    current_speed: Gtk.Label = Gtk.Template.Child()

    progress: Gtk.ProgressBar = Gtk.Template.Child()

    def __init__(self, mod_name: str, file_source: SubmissionInfoFileSource):
        super().__init__()

        self.url = file_source["_sDownloadUrl"]
        self.mod_name.set_label(mod_name)
        self.mode_filename.set_label(file_source["_sFile"])

        self.total_size = file_source["_nFilesize"]

    def calculate_speed(self, start_time, downloaded):
        return fmt(downloaded / (time.time() - start_time))

    def start_download(self, path: str):
        try:
            r = requests.get(self.url, stream=True)
            r.raise_for_status()
        except Exception as e:
            # TODO: implement graphical error handling
            print("error downlading", e.args)
            return

        with open(path, "wb") as f:
            downloaded = 0
            start = time.time()
            for chunk in r.iter_content(chunk_size=8192):
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)

                GLib.idle_add(
                    self.downloaded_label.set_label,
                    f"Downloading: {fmt(downloaded)} of {fmt(self.total_size)}",
                )
                GLib.idle_add(
                    self.current_speed.set_label,
                    f"{self.calculate_speed(start, downloaded)}/s",
                )
                GLib.idle_add(self.progress.set_fraction, downloaded / self.total_size)


@Blueprint("sidebar")
class BananaSidebar(Adw.Bin):
    _instance = None
    __gtype_name__ = "BananaSidebar"

    mods_box: Gtk.ListBox = Gtk.Template.Child()

    def __init__(self):
        super().__init__()
        self.queue = queue.Queue()  # FIXME: change this if the queue is reverse
        placeholder = Adw.StatusPage(
            # css_classes=["compact"],
            title="No downloads",
            description="You have no downloads in progress. Start a new download to see it here.",
        )

        placeholder.set_icon_name("folder-download-symbolic")

        self.mods_box.set_placeholder(placeholder)

        self.process_queue()

    @classmethod
    def get_default(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def add_mod(self, mod_name: str, file_source: SubmissionInfoFileSource, path: str):
        m = Mod(mod_name, file_source)
        self.queue.put((m, path))
        self.mods_box.append(m)

    @Thread
    def process_queue(self):
        while True:
            mod_widget, path = self.queue.get()
            mod_widget.start_download(path)
