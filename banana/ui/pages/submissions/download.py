from banana.modules.gamebanana.types import (
    SubmissionInfoFileSource,
    SubmissionInfoAltFileSource,
)
from banana.modules.utils import Blueprint
from ..downloads import DownloadsPage, DownloadItem

from gi.repository import Gtk, Adw, Gio, GLib


class AltFileRow(Adw.ActionRow):
    def __init__(self, _notify, file: SubmissionInfoAltFileSource):
        super().__init__(
            activatable=True,
            title=file["description"],
            subtitle=file["url"],
        )
        self.url = file["url"]
        self._notify = _notify
        image = Gtk.Image(icon_name="external-link-symbolic", margin_start=10)

        self.add_suffix(image)
        self.connect("activated", self.__on_clicked)

    def __on_clicked(self, _):
        # NOTE: maybe add a web view showing the url
        # and append the download to the downlads page
        Gio.AppInfo.launch_default_for_uri_async(self.url)
        self._notify("The download url has been opened in your browser")


class FileRow(Adw.ActionRow):
    def __init__(
        self,
        submission_name: str,
        _notify,
        file: SubmissionInfoFileSource,
    ):
        super().__init__(
            title=file["_sFile"],
            subtitle=f"{file.get('_sDescription')} ({GLib.format_size_for_display(file.get('_nFilesize'))})",
            activatable=True,
        )
        self.connect("activated", self.__download)
        self._notify = _notify
        self.info = file
        self.submission_name = submission_name
        self.is_alt = bool(file.get("url"))

        img = Gtk.Image(icon_name="download-symbolic", margin_start=10)

        self.add_suffix(img)

    def __on_save_finish(self, dialog: Gtk.FileDialog, result):
        try:
            f = dialog.save_finish(result)
            item = DownloadItem(self.submission_name, f.get_path(), self.info)
            DownloadsPage.get_default().append_download(item)

            self._notify(f"Downloading {self.info['_sFile']}...")
        except GLib.GError:
            return
        finally:
            self.set_sensitive(True)

    def __download(self, _):
        self.set_sensitive(False)
        name = self.info["_sFile"]

        diag = Gtk.FileDialog(
            title=f"Save {name}",
            initial_name=name,
            initial_folder=Gio.File.new_for_path(
                GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOWNLOAD)
            ),
        )
        diag.save(self.get_root(), None, self.__on_save_finish)


@Blueprint("submission-download-dialog")
class SubmissionDownloadDialog(Adw.Dialog):
    __gtype_name__ = "SubmissionDownloadDialog"

    files_box: Gtk.ListBox = Gtk.Template.Child()
    alt_files_box: Gtk.ListBox = Gtk.Template.Child()
    toast_ovrl: Adw.ToastOverlay = Gtk.Template.Child()

    def __init__(
        self,
        submission_name: str,
        files: list[SubmissionInfoFileSource],
        alt_files: list[SubmissionInfoAltFileSource],
    ):
        super().__init__()

        self.set_title(f"{submission_name} - Downloads")

        if len(files) == 0:
            self.files_box.append(Adw.ActionRow(title="No files"))

        if len(alt_files) == 0:
            self.alt_files_box.append(Adw.ActionRow(title="No alt files"))

        for file in files:
            row = FileRow(submission_name, self._notify, file)
            self.files_box.append(row)

        for alt in alt_files:
            row = AltFileRow(self._notify, alt)
            self.alt_files_box.append(row)

    def _notify(self, message):
        self.toast_ovrl.add_toast(Adw.Toast.new(message))
