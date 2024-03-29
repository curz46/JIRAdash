import os

JIRA_URL = os.environ.get("JIRA_URL")

from gi.repository import Gtk, Gdk, Gio, GObject, Pango
from dash.model import DashModel

class DashView(Gtk.Window):
    def __init__(self, controller, schema):
        self._controller = controller

        Gtk.Window.__init__(self, title="Search Query", type=Gtk.WindowType.POPUP)
        self.set_size_request(1100, 800)
        self.set_resizable(False)

        self.connect("key-press-event", self._controller.on_key_press)
        self.connect("key-release-event", self._controller.on_key_release)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(vbox)

        # Entry box
        entry_box = Gtk.Box()
        entry_box.set_size_request(-1, 60)
        vbox.pack_start(entry_box, False, False, 0)

        textbox = Gtk.Entry()
        textbox.set_valign(Gtk.Align.FILL)
        textbox.set_max_length(200)
        entry_box.pack_start(textbox, True, True, 0)
        textbox.connect("changed", self._controller.on_text_changed)
        textbox.connect("key-press-event", self._controller.on_typing)

        self._entry = textbox

        # Filter box
        filter_box = Gtk.Box()
        vbox.pack_start(filter_box, False, False, 0)

        self._controller.create_filter_menus(filter_box)

        # ListBox
        self.liststore = Gio.ListStore()
        self.listbox = Gtk.ListBox()
        self.listbox.bind_model(self.liststore, self._controller.create_widget_func)
        self.listbox.connect("row_activated", self.on_row_activated)

        # ScrolledWindow
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(self.listbox)
        vbox.pack_start(scrolled_window, True, True, 0)

    def on_row_activated(self, listbox, row):
        grid = row.get_child()
        item = grid.item
        if item and item.fields:
            key = item.fields[0]
            # TODO 
            os.system(f"xdg-open {JIRA_URL}/browse/{key}")
            if not self._controller.is_key_pressed(Gdk.KEY_Shift_L):
                exit()

    def get_entry_text(self):
        return self._entry.get_text()

    def update_search_results(self, data):
        self.liststore.remove_all()

        for row in data:
            item = Item(fields=row)
            self.liststore.append(item)

        rows = self.listbox.get_children()
        if len(rows) > 0:
            self.listbox.select_row( rows[0] )

    def add_filter_menu(self, filter_menu_button, filter_menu):
        filter_box = self.get_children()[0].get_children()[1]
        filter_box.pack_start(filter_menu_button, False, False, 0)

    def get_active_filters(self):
        return self._controller.get_active_filters()

class Item(GObject.GObject):
    def __init__(self, fields):
        GObject.GObject.__init__(self)
        self.fields = fields

    def get_fields():
        return self.fields
