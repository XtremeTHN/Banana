from gi.repository import Adw, Gtk
from src.modules.gamebanana import Gamebanana
from src.modules.utils import idle  # TODO: rename src folder to banana
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


def populate_updates(box: Gtk.ListBox, submission_type: str, submission_id: str):
    updates = Gamebanana.get_submission_updates(submission_type, submission_id)
    # TODO: refactor this, it looks ugly
    for records in updates:
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
