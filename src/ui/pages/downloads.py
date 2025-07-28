from src.modules.gamebanana.types import (
    SubmissionInfoFileSource,
    SubmissionInfoAltFileSource,
)

from src.modules.utils import Blueprint, idle, idle_wrap
from gi.repository import Gtk, Adw, Gio, GLib
import threading
import requests
import time

import traceback


def fmt(size):
    return GLib.format_size_for_display(size)


@Blueprint("download-item")
class DownloadItem(Gtk.ListBoxRow):
    __gtype_name__ = "DownloadItem"

    file_title: Gtk.Label = Gtk.Template.Child()
    file_name: Gtk.Label = Gtk.Template.Child()
    current_progress: Gtk.Label = Gtk.Template.Child()
    current_speed: Gtk.Label = Gtk.Template.Child()

    progress_bar: Gtk.ProgressBar = Gtk.Template.Child()

    stop_btt: Gtk.Button = Gtk.Template.Child()
    open_btt: Gtk.Button = Gtk.Template.Child()

    info_stack: Gtk.Stack = Gtk.Template.Child()

    error_name: Gtk.Label = Gtk.Template.Child()
    # prog_box: Gtk.Box = Gtk.Template.Child()

    def __init__(
        self, download_title: str, path: str, file_info: SubmissionInfoFileSource
    ):
        super().__init__()
        self.file_title.set_label(download_title)
        self.file_name.set_label(file_info["_sFile"])

        self.on_finish = None
        self.cancellable = Gio.Cancellable.new()
        self.url = file_info["_sDownloadUrl"]
        self.size = file_info["_nFilesize"]
        self.fmt_size = fmt(self.size)
        self.path = path

    @idle_wrap
    def show_error(self, error_name):
        self.info_stack.add_css_class("error")
        self.error_name.set_label(error_name)
        self.info_stack.set_visible_child_name("error")

    @idle_wrap
    def finish(self):
        self.stop_btt.set_visible(False)

        if self.cancellable.is_cancelled():
            self.show_error("Cancelled")
        else:
            self.info_stack.set_visible_child_name("open")
        self.on_finish(self)

    @Gtk.Template.Callback()
    def stop_download(self, _):
        # TODO: add a graphical indicator that this download has been canceled
        # maybe a 0.5px border with a color
        self.cancellable.cancel()

    def start_download(self, on_finish):
        self.on_finish = on_finish
        threading.Thread(target=self.__download).start()

    def __download(self):
        try:
            r = requests.get(self.url, stream=True)
            r.raise_for_status()
        except Exception as e:
            self.show_error(e.__class__.__name__)
            self.finish()
            raise e  # the exception will be showed in a dialog

        with open(self.path, "wb") as f:
            downloaded = 0
            start = time.time()
            for chunk in r.iter_content(chunk_size=8192):
                if not chunk or self.cancellable.is_cancelled():
                    break

                f.write(chunk)
                downloaded += len(chunk)

                idle(
                    self.current_progress.set_label,
                    f"Downloading: {fmt(downloaded)} of {self.fmt_size}",
                )
                idle(
                    self.current_speed.set_label,
                    f"{fmt(downloaded / (time.time() - start))}/s",
                )
                idle(self.progress_bar.set_fraction, downloaded / self.size)

            self.finish()


@Blueprint("downloads-page")
class DownloadsPage(Adw.NavigationPage):
    __gtype_name__ = "DownloadsPage"
    _instance = None

    stop_all_btt: Gtk.Button = Gtk.Template.Child()

    active_box: Gtk.ListBox = Gtk.Template.Child()
    finished_box: Gtk.ListBox = Gtk.Template.Child()

    active_stack: Gtk.Stack = Gtk.Template.Child()
    finished_stack: Gtk.Stack = Gtk.Template.Child()

    def __init__(self):
        super().__init__()

        self.active_downloads = []
        self.finished_downloads_count = 0

    def on_finish(self, item):
        self.active_downloads.remove(item)
        self.active_box.remove(item)

        self.finished_downloads_count += 1
        self.finished_box.append(item)

    def append_download(self, item: DownloadItem):
        item.start_download(self.on_finish)
        self.active_downloads.append(item)
        self.active_box.append(item)

    @classmethod
    def get_default(cls):
        return cls._instance
