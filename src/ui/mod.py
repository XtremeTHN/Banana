from ..modules.gamebanana.types import Submission, SubmissionInfo
from ..modules.utils import Blueprint
from gi.repository import Gtk, Adw, Gio, Gdk, GLib


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
        cover = Gio.File.new_for_uri(submission["_sImageUrl"])
        submitter_pfp = Gio.File.new_for_uri(submitter["_sAvatarUrl"])
        sub_pfp = Gdk.Texture.new_from_file(submitter_pfp)

        self.mod_preview.set_file(cover)
        self.mod_submitter.set_from_paintable(sub_pfp)
        self.mod_submitter.set_tooltip_text(submitter["_sName"])

        self.mod_feature_type.set_label(
            f"Best of {get_formatted_period(submission['_sPeriod'])}"
        )
        self.mod_name.set_label(submission["_sName"])

        if (n := submission.get("_sDescription", "")) != "":
            self.mod_caption.set_label(n)
        else:
            self.mod_caption.set_visible(False)


@Blueprint("mod-button")
class ModButton(Gtk.Button):
    __gtype_name__ = "ModButton"

    mod_cover: Gtk.Picture = Gtk.Template.Child()
    mod_name: Gtk.Label = Gtk.Template.Child()
    mod_caption: Gtk.Label = Gtk.Template.Child()

    def __init__(self, submission: SubmissionInfo):
        super().__init__()

        if len((n := submission["_aPreviewMedia"]["_aImages"])) != 0:
            img = n[0]
            cover = Gio.File.new_for_uri(img["_sBaseUrl"] + "/" + img["_sFile"])
            GLib.idle_add(self.mod_cover.set_file, cover)
            # paintable = Gdk.Texture.new_from_file(cover)

            # self.mod_cover.set_from_paintable(paintable)

        self.mod_name.set_label(submission["_sName"])
