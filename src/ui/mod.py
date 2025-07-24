from ..modules.gamebanana.types import Submission, SubmissionInfo
from ..modules.cache import cache_download
from ..modules.utils import Blueprint
from gi.repository import Gtk, Adw, Gio, Gdk, GLib


# idle = GLib.idle_add
def idle(func, *args):
    return GLib.idle_add(func, *args)


def get_formatted_period(period: str):
    match period:
        case "today":
            return "today"
        case "week":
            return "this week"
        case "month":
            return "this month"
        case "3month":
            return "this 3 months"
        case "6month":
            return "this 6 months"
        case "year":
            return "this year"
        case "alltime":
            return "all time"
        case _:
            print(period)


@Blueprint("top-mod")
class TopMod(Gtk.Overlay):
    __gtype_name__ = "TopMod"
    mod_preview: Gtk.Picture = Gtk.Template.Child()
    mod_feature_type: Gtk.Label = Gtk.Template.Child()
    mod_submitter: Gtk.Image = Gtk.Template.Child()

    mod_name: Gtk.Label = Gtk.Template.Child()
    mod_caption: Gtk.Label = Gtk.Template.Child()

    download_btt: Gtk.Button = Gtk.Template.Child()

    def __init__(self, submission):
        super().__init__()
        event = Gtk.EventControllerMotion.new()
        self.add_controller(event)
        event.connect("enter", self.__on_hover)
        event.connect("leave", self.__on_hover_lost)

        self.populate(submission)

    def __on_hover(self, *_):
        self.download_btt.set_visible(True)

    def __on_hover_lost(self, *_):
        self.download_btt.set_visible(False)

    def populate(self, submission: Submission):
        submitter = submission["_aSubmitter"]

        def on_finish(cover, sub_pfp):
            idle(self.mod_preview.set_filename, cover)
            idle(self.mod_submitter.set_from_file, sub_pfp)
            idle(self.mod_submitter.set_tooltip_text, submitter["_sName"])

            idle(
                self.mod_feature_type.set_label,
                f"Best of {get_formatted_period(submission['_sPeriod'])}",
            )
            idle(self.mod_name.set_label, submission["_sName"])

            if (n := submission.get("_sDescription", "")) != "":
                idle(self.mod_caption.set_label, n)
            else:
                idle(self.mod_caption.set_visible, False)

        cache_download(submission["_sImageUrl"], submitter["_sAvatarUrl"], cb=on_finish)


@Blueprint("mod-button")
class ModButton(Gtk.Button):
    __gtype_name__ = "ModButton"

    mod_cover: Gtk.Picture = Gtk.Template.Child()
    mod_name: Gtk.Label = Gtk.Template.Child()
    mod_caption: Gtk.Label = Gtk.Template.Child()

    def __init__(self, submission: SubmissionInfo):
        super().__init__()
        preview = submission["_aPreviewMedia"]
        if preview.get("_aImages") is not None:
            if len((n := submission["_aPreviewMedia"]["_aImages"])) != 0:
                cache_download(
                    n[0]["_sBaseUrl"] + "/" + n[0]["_sFile"], cb=self.__on_down_finish
                )

        self.mod_name.set_label(submission["_sName"])

    def __on_down_finish(self, cover):
        GLib.idle_add(self.mod_cover.set_filename, cover)
