from ..modules.gamebanana.types import SubmissionInfo, SubmissionWip
from ..modules.gamebanana import Gamebanana
from ..modules.cache import cache_download
from ..modules.utils import Blueprint, idle

from .screenshot import Screenshot
from gi.repository import Gtk, Adw
import traceback
import json

import re


# TODO: Maybe write a rich text viewer insted of deleting html tags
def sanitaze_html(html: str) -> str:
    # Replace <br> and <p> with newlines
    html = re.sub(r"<br\s*/?>", "\n", html)
    html = re.sub(r"</p>", "", html)
    html = re.sub(r"<p>", "", html)

    # Replace <b>, <i>, <u>
    # html = re.sub(r"<b>(.*?)</b>", r"<b>\1</b>", html)
    # html = re.sub(r"<i>(.*?)</i>", r"<i>\1</i>", html)
    # html = re.sub(r"<u>(.*?)</u>", r"<u>\1</u>", html)

    # Remove all other tags (or handle as needed)
    html = re.sub(r"<.*?>", "", html)

    return html.replace("&nbsp;", "").replace("&", "&amp;")


def populate_credits(box, array_credits):
    if len(array_credits) > 0:
        for _type in array_credits:
            exp = Adw.ExpanderRow(title=_type["_sGroupName"])
            for author in _type["_aAuthors"]:
                exp.add_row(
                    Adw.ActionRow(
                        use_markup=False,
                        css_classes=["property"],
                        title=author.get("_sRole", "Unkown role"),
                        subtitle=author.get("_sName", "Unkown author"),
                    )
                )
            idle(box.append, exp)
    else:
        box.append(Adw.ActionRow(title="No credits"))


def populate_updates(box: Gtk.ListBox, submission_type: str, submission_id: str):
    updates = Gamebanana.get_submission_updates(submission_type, submission_id)
    # TODO: refactor this, it looks ugly
    for records in updates:
        if len(records) == 0:
            box.append(Adw.ActionRow(title="No updates"))
            break

        for update in records:
            subtitle = sanitaze_html(update["_sText"])
            exp = Adw.ExpanderRow(
                use_markup=False,
                title=update["_sName"],
                subtitle=subtitle,
            )
            if (n := update.get("_aChangeLog")) is not None:
                for change in n:
                    subtitle = sanitaze_html(change["text"])
                    exp.add_row(
                        Adw.ActionRow(
                            use_markup=False,
                            css_classes=["property"],
                            title=change["cat"],
                            subtitle=subtitle,
                        )
                    )
            idle(box.append, exp)


@Blueprint("wip-page")
class WipPage(Adw.NavigationPage):
    __gtype_name__ = "WipPage"

    wip_icon: Gtk.Picture = Gtk.Template.Child()
    wip_title: Gtk.Label = Gtk.Template.Child()
    wip_caption: Gtk.Label = Gtk.Template.Child()
    wip_description: Gtk.Label = Gtk.Template.Child()

    completed: Gtk.LevelBar = Gtk.Template.Child()
    completed_label: Gtk.Label = Gtk.Template.Child()

    stack: Gtk.Stack = Gtk.Template.Child()
    screenshots_carousel: Adw.Carousel = Gtk.Template.Child()

    updates_box: Gtk.ListBox = Gtk.Template.Child()
    credits_box: Gtk.ListBox = Gtk.Template.Child()

    likes: Gtk.Label = Gtk.Template.Child()
    views: Gtk.Label = Gtk.Template.Child()

    loading_status: Adw.StatusPage = Gtk.Template.Child()
    trashed_status: Adw.StatusPage = Gtk.Template.Child()

    def __init__(self, mod_id):
        super().__init__(title=" - Work in progress")

        spinner = Adw.SpinnerPaintable.new()
        self.loading_status.set_paintable(spinner)
        spinner.set_widget(self.loading_status)

        self.wip_id = mod_id

        # TODO: if this converts into a gamebanana general client, change this to the type of the submission id
        Gamebanana.get_submission_info("Wip", mod_id, self.populate)

    def populate(self, submission: SubmissionWip):
        def finish(cover, *images):
            try:
                idle(self.wip_icon.set_filename, cover)

                for img in images:
                    s = Screenshot()
                    idle(s.pic.set_filename, img)
                    idle(self.screenshots_carousel.append, s)

                idle(self.wip_title.set_label, submission["_sName"])
                idle(self.wip_caption.set_label, submission["_aSubmitter"]["_sName"])

                idle(self.likes.set_label, f"{submission['_nLikeCount']:,}")
                idle(self.views.set_label, f"{submission['_nViewCount']:,}")

                idle(
                    self.wip_description.set_label, sanitaze_html(submission["_sText"])
                )

                idle(
                    self.completed_label.set_label,
                    f"{submission['_sDevelopmentState']} - {submission['_iCompletionPercentage']}% completed",
                )
                idle(
                    self.completed.set_value, submission["_iCompletionPercentage"] / 100
                )

                populate_updates(self.updates_box, "Wip", self.wip_id)
                populate_credits(self.credits_box, submission["_aCredits"])

                idle(self.stack.set_visible_child_name, "main")
            except KeyError as e:
                print(json.dumps(submission, indent=4))
                print(f"<{e.__class__.__name__}>:", e.args)

        self.set_title(submission["_sName"] + " - Work in progress")
        if (n := submission["_aPreviewMedia"].get("_aImages")) is not None:
            cache_download(*[f"{x['_sBaseUrl']}/{x['_sFile']}" for x in n], cb=finish)


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
    trashed_status: Adw.StatusPage = Gtk.Template.Child()

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
            try:
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

                idle(
                    self.mod_description.set_label, sanitaze_html(submission["_sText"])
                )

                populate_updates(self.updates_box, "Mod", self.mod_id)
                populate_credits(self.credits_box, submission["_aCredits"])

                idle(self.stack.set_visible_child_name, "main")
            except KeyError as e:
                print(json.dumps(submission, indent=4))
                print(f"<{e.__class__.__name__}>:", e.args)
                traceback.print_exception(e)

        self.set_title(submission["_sName"] + " - Mod")

        if submission["_bIsTrashed"]:
            self.stack.set_visible_child_name("trashed")
            self.trashed_status.set_description(
                f"This submission was trashed: {submission['_aTrashInfo']['_sReason']}"
            )
            return

        if (n := submission["_aPreviewMedia"].get("_aImages")) is not None:
            cache_download(*[f"{x['_sBaseUrl']}/{x['_sFile']}" for x in n], cb=finish)
