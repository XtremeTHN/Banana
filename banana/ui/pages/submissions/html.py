from gi.repository import Gtk, Adw, Gio, Pango, GObject
from bs4 import BeautifulSoup
import logging


class Table(Gtk.TextTagTable):
    def __init__(self):
        super().__init__()
        self.accent = Adw.accent_color_to_rgba(
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
                foreground_rgba=self.accent,
            ),
            "i": Gtk.TextTag(name="i", style=Pango.Style.ITALIC),
            "em": Gtk.TextTag(name="em", style=Pango.Style.ITALIC),
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

    def get_link_tag(self, url):
        tag = Gtk.TextTag(
            weight=500,
            foreground_rgba=self.accent,
            underline=Pango.Underline.SINGLE,
            underline_rgba=self.accent,
        )
        tag.url = url
        self.add(tag)
        return tag


class HtmlView(Gtk.TextView):
    __gtype_name__ = "HtmlView"

    def __init__(self, submission_id=0):
        super().__init__(
            editable=False,
            cursor_visible=False,
        )
        self.__html = ""
        self._table = Table()
        self.logger = logging.getLogger(f"HtmlView({submission_id})")

        click_controller = Gtk.GestureClick.new()
        click_controller.connect("released", self.__on_released)

        motion_controller = Gtk.EventControllerMotion.new()
        motion_controller.connect("motion", self.__on_motion)

        self.add_controller(click_controller)
        self.add_controller(motion_controller)

        self.set_wrap_mode(Gtk.WrapMode.WORD)
        self.set_css_classes([])

    def __on_motion(self, _, x, y):
        tx, ty = self.window_to_buffer_coords(Gtk.TextWindowType.WIDGET, x, y)

        cond, iter = self.get_iter_at_location(tx, ty)

        if cond:
            for tag in iter.get_tags():
                if hasattr(tag, "url"):
                    self.set_cursor_from_name("pointer")
                    return
        self.set_cursor_from_name("text")

    def __on_released(self, gesture: Gtk.GestureClick, n_press: int, x: int, y: int):
        if gesture.get_button() > 1:
            return

        tx, ty = self.window_to_buffer_coords(Gtk.TextWindowType.WIDGET, x, y)
        buff = self.get_buffer()

        if not buff:
            print("warn: buffer not set")
            return

        res, iter = self.get_iter_at_location(tx, ty)

        if not res:
            print("warn: couldn't get text iter")
            return

        self.follow_if_link(iter)

    def follow_if_link(self, iter: Gtk.TextIter):
        for tag in iter.get_tags():
            url = getattr(tag, "url", None)
            if url is not None:
                Gio.AppInfo.launch_default_for_uri_async(url)
                return

    @GObject.Property()
    def html(self):
        return self.__html

    @html.setter
    def html(self, html):
        self.__html = html.replace("&nbsp;", "")
        self.set_buffer(self.get_formatted_buffer())

    def get_formatted_buffer(self):
        buff = Gtk.TextBuffer.new(self._table)
        iter = buff.get_start_iter()

        soup = BeautifulSoup(self.__html, "html.parser")

        def walk(node, iter, tag_stack=[]):
            if isinstance(node, str):
                if node.strip():
                    buff.insert_with_tags(iter, node, *tag_stack)
                return

            if node.name == "br":
                buff.insert(iter, "\n")
                return

            if node.name == "img":
                src = node.attrs.get("src")
                alt = node.attrs.get("alt", "Image")

                if src:
                    tag = self._table.get_link_tag(src)
                    buff.insert_with_tags(iter, f"{alt}\n", tag)
                return

            if node.name == "ul":
                for x in node.children:
                    if x.name == "li":
                        li_tag = self._table.tags.get("li")
                        walk(f"- {x.get_text()}\n", iter, [li_tag])
                return

            if node.name == "a":
                href = node.attrs.get("href")
                link_tag = self._table.get_link_tag(href) if href else None
                for child in node.children:
                    walk(child, iter, tag_stack + ([link_tag] if link_tag else []))
                return

            tag_obj = self._table.tags.get(node.name)
            new_stack = tag_stack + ([tag_obj] if tag_obj else [])

            if not tag_obj:
                self.logger.warning(f"unsupported tag: {node.name}. html: {node}")

            for child in node.children:
                walk(child, iter, new_stack)

            if node.name and node.name.startswith("h"):
                buff.insert(iter, "\n")

        for element in soup.body.contents if soup.body else soup.contents:
            walk(element, iter)

        return buff
