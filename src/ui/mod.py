from ..modules.gamebanana.types import Submission, SubmissionInfo, Update
from ..modules.gamebanana import Gamebanana, get_sync
from ..modules.cache import cache_download
from ..modules.utils import Blueprint, idle

from .nav import Navigation
from .screenshot import Screenshot
from gi.repository import Gtk, Adw, Gio, Gdk, GLib

import re


def html_to_pango(html: str) -> str:
    # Replace <br> and <p> with newlines
    html = re.sub(r"<br\s*/?>", "\n", html)
    html = re.sub(r"</p>", "\n", html)
    html = re.sub(r"<p>", "", html)

    # Replace <b>, <i>, <u>
    # html = re.sub(r"<b>(.*?)</b>", r"<b>\1</b>", html)
    # html = re.sub(r"<i>(.*?)</i>", r"<i>\1</i>", html)
    # html = re.sub(r"<u>(.*?)</u>", r"<u>\1</u>", html)

    # Remove all other tags (or handle as needed)
    html = re.sub(r"<.*?>", "", html)

    return html.replace("&nbsp;", "")


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
        self.mod_id = submission["_idRow"]

        preview = submission["_aPreviewMedia"]
        if preview.get("_aImages") is not None:
            if len((n := submission["_aPreviewMedia"]["_aImages"])) != 0:
                cache_download(
                    n[0]["_sBaseUrl"] + "/" + n[0]["_sFile"], cb=self.__on_down_finish
                )

        self.mod_name.set_label(submission["_sName"])

    @Gtk.Template.Callback()
    def on_clicked(self, btt):
        page = ModPage(self.mod_id)
        Navigation.get_default().nav_view.push(page)

    def __on_down_finish(self, cover):
        GLib.idle_add(self.mod_cover.set_filename, cover)


@Blueprint("mod-page")
class ModPage(Adw.NavigationPage):
    __gtype_name__ = "ModPage"

    mod_icon: Gtk.Picture = Gtk.Template.Child()
    mod_title: Gtk.Label = Gtk.Template.Child()
    mod_caption: Gtk.Label = Gtk.Template.Child()
    mod_description: Gtk.Label = Gtk.Template.Child()

    stack: Gtk.Stack = Gtk.Template.Child()
    screenshots_carousel: Adw.Carousel = Gtk.Template.Child()
    credits_box: Gtk.ListBox = Gtk.Template.Child()
    updates_box: Gtk.ListBox = Gtk.Template.Child()

    likes: Gtk.Label = Gtk.Template.Child()
    downloads: Gtk.Label = Gtk.Template.Child()
    views: Gtk.Label = Gtk.Template.Child()

    loading_status: Adw.StatusPage = Gtk.Template.Child()

    def __init__(self, mod_id):
        super().__init__(title="Mod")

        spinner = Adw.SpinnerPaintable.new()
        self.loading_status.set_paintable(spinner)
        spinner.set_widget(self.loading_status)

        self.mod_id = mod_id

        # TODO: if this converts into a gamebanana general client, change this to the type of the submission id
        Gamebanana.get_submission_info("Mod", mod_id, self.populate)

    def populate(self, submission: SubmissionInfo):
        def finish(cover, *images):
            print(cover)
            idle(self.mod_icon.set_filename, cover)

            for img in images:
                s = Screenshot()
                idle(s.pic.set_filename, img)
                idle(self.screenshots_carousel.append, s)

            idle(self.mod_title.set_label, submission["_sName"])
            idle(self.mod_caption.set_label, submission["_aSubmitter"]["_sName"])

            idle(self.likes.set_label, f"{submission['_nLikeCount']:,}")
            idle(self.views.set_label, f"{submission['_nViewCount']:,}")
            idle(self.downloads.set_label, f"{submission['_nDownloadCount']:,}")

            idle(self.mod_description.set_label, html_to_pango(submission["_sText"]))

            updates = Gamebanana.get_submission_updates("Mod", self.mod_id)

            # TODO: refactor this, it looks ugly
            for records in updates:
                if len(records) == 0:
                    self.updates_box.append(Adw.ActionRow(title="No updates"))
                    break

                for update in records:
                    exp = Adw.ExpanderRow(
                        title=update["_sName"], subtitle=update["_sText"]
                    )
                    if (n := update.get("_aChangeLog")) is not None:
                        for change in n:
                            txt = change["text"].replace("<p>", "").replace("</p>", "")
                            exp.add_row(
                                Adw.ActionRow(
                                    css_classes=["property"],
                                    title=change["cat"],
                                    subtitle=txt,
                                )
                            )
                    idle(self.updates_box.append, exp)

            if len((credits := submission["_aCredits"])) > 0:
                for _type in credits:
                    exp = Adw.ExpanderRow(title=_type["_sGroupName"])
                    for author in _type["_aAuthors"]:
                        exp.add_row(
                            Adw.ActionRow(
                                css_classes=["property"],
                                title=author["_sRole"],
                                subtitle=author["_sName"],
                            )
                        )
                    idle(self.credits_box.append, exp)

            self.stack.set_visible_child_name("main")

        if (n := submission["_aPreviewMedia"].get("_aImages")) is not None:
            cache_download(*[f"{x['_sBaseUrl']}/{x['_sFile']}" for x in n], cb=finish)
