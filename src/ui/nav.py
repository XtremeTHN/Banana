from ..modules.utils import Blueprint
from gi.repository import Adw, GObject


class Navigation(Adw.Bin):
    __gtype_name__ = "Navigation"
    _instance = None

    def __init__(self):
        super().__init__()
        self.__page = None
        self.nav_view = Adw.NavigationView()

        self.set_child(self.nav_view)

    @GObject.Property(type=Adw.NavigationPage)
    def page(self):
        return self.__page

    @page.setter
    def page(self, page):
        self.__page = page
        self.nav_view.push(page)

    @classmethod
    def get_default(cls):
        return cls._instance
