from gi.repository import Adw, Gtk, Pango
from banana.modules.gamebanana import Gamebanana
from bs4 import BeautifulSoup
from banana.modules.utils import idle
import logging
import re


class Table(Gtk.TextTagTable):
    def __init__(self):
        super().__init__()
        accent = Adw.accent_color_to_rgba(
            Adw.StyleManager.get_default().get_accent_color()
        )

        self.tags = {
            "b": Gtk.TextTag(name="b", weight=700),
            "strong": Gtk.TextTag(name="strong", weight=700),
            "u": Gtk.TextTag(
                name="u",
                underline=Pango.Underline.SINGLE,
            ),
            "a": Gtk.TextTag(
                name="a",
                weight=500,
                foreground_rgba=accent,
                underline=Pango.Underline.SINGLE,
                underline_rgba=accent,
            ),
            "i": Gtk.TextTag(name="i", style=Pango.Style.ITALIC),
            "li": Gtk.TextTag(name="li", indent=4),
            "h1": Gtk.TextTag(
                name="h1",
                scale=1.6,
                weight=800,
            ),
            "h2": Gtk.TextTag(name="h2", scale=1.4, weight=800),
            "h3": Gtk.TextTag(name="h3", scale=1.2, weight=800),
            "h4": Gtk.TextTag(name="h4", scale=1, weight=800),
            "span": Gtk.TextTag(
                name="span",
            ),
        }

        for _, x in self.tags.items():
            self.add(x)


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


def parse(txt: str):
    txt = txt.replace("&nbsp;", "")
    table = Table()
    buff = Gtk.TextBuffer.new(table)
    soup = BeautifulSoup(txt, "html.parser")

    for elem in soup:
        mark = buff.get_insert()
        text = elem.text

        if elem.name == "br":
            buff.insert_at_cursor("\n")
            continue

        if elem.name == "h1":
            text = text + "\n"

        if elem.name == "hr":
            continue

        if elem.name == "ul":
            for x in elem.children:
                buff.insert_with_tags_by_name(
                    buff.get_iter_at_mark(mark), f"- {x.text}\n", "li"
                )
            continue

        if elem.name is None:
            buff.insert_at_cursor(text)
            continue

        if elem.name not in table.tags:
            logging.warning(f"tag not supported: {elem.name}")
            buff.insert_at_cursor(text)
            continue

        buff.insert_with_tags_by_name(buff.get_iter_at_mark(mark), text, elem.name)

    return buff


def populate_credits(box, array_credits):
    if len(array_credits) == 0:
        idle(box.append, Adw.ActionRow(title="No credits"))
        return

    for _type in array_credits:
        authors = _type["_aAuthors"]
        if len(authors) == 0:
            row = Adw.ActionRow(title=_type["_sGroupName"], use_markup=False)
        else:
            row = Adw.ExpanderRow(title=_type["_sGroupName"], use_markup=False)

        for author in _type["_aAuthors"]:
            row.add_row(
                Adw.ActionRow(
                    use_markup=False,
                    css_classes=["property"],
                    title=author.get("_sRole", "Unkown role"),
                    subtitle=author.get("_sName", "Unkown author"),
                )
            )
        idle(box.append, row)


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
