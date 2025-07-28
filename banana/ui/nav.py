from ..modules.utils import Blueprint
from gi.repository import Adw, GObject


class Navigation(Adw.Bin):
    __gtype_name__ = "Navigation"
    _instance = None

    def __init__(self):
        super().__init__()
        self.__navigation: Adw.NavigationView = None

    @GObject.Property(type=Adw.NavigationView)
    def navigation(self):
        return self.__navigation

    @navigation.setter
    def navigation(self, widget):
        self.__navigation = widget
        self.set_child(self.__navigation)

    @classmethod
    def get_default(cls):
        return cls._instance
