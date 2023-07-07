from gi.repository import Gtk, Gdk, Gio, Pango
from dash.view import DashView, Item
from dash.model import DashModel
import os

class DashController:
    def __init__(self, model, schema):
        self._model = model
        self._columns = schema["gui"]["columns"]
        self._filters = schema["gui"]["filters"]
        self._active_filters = {filter_group: set(obj['default_filters']) for filter_group, obj in self._filters.items()}
        self._view = DashView(self, schema)

        self._keys = {}

    def get_active_filters(self):
        return self._active_filters

    def create_filter_menus(self, filter_box):
        for filter_group, filter_config in self._filters.items():
            filter_menu_button = Gtk.MenuButton.new()
            filter_menu_button.set_can_focus(False)
            filter_menu_button.set_label(filter_group.capitalize())
            filter_menu = Gtk.Menu.new()

            filter_data = self._model.get_filter_data(filter_group)

            for row in filter_data:
                filter_value = row[0] if row[0] else "None"
                check_menu_item = FilterCheckMenuItem(filter_value, filter_group, filter_value, self.on_filter_item_toggled)
                check_menu_item.set_active(filter_value in filter_config["default_filters"])
                filter_menu.append(check_menu_item)

            filter_menu.show_all()
            filter_menu_button.set_popup(filter_menu)
            filter_box.pack_start(filter_menu_button, False, False, 0)

    def on_filter_item_toggled(self, check_menu_item):
        filter_group, filter_value = check_menu_item.get_filter_info()
        if check_menu_item.get_active():
            self._active_filters[filter_group].add(filter_value)
        else:
            self._active_filters[filter_group].remove(filter_value)

        self.update_search_results(self._view.get_entry_text())

    def on_text_changed(self, entry):
        query = entry.get_text().strip()
        self.update_search_results(query)

    def update_search_results(self, query):
        search_results = self._model.search_issues(query, self._active_filters)
        self._view.update_search_results(search_results)

    def create_widget_func(self, item):
        grid = Gtk.Grid()
        grid.item = item
        grid.set_column_spacing(2)
        grid.set_size_request(-1, 30)

        for i, field in enumerate(item.fields):
            label = Gtk.Label(field)
            if self._columns[i] == 'key':
                font = Pango.FontDescription("monospace")
                label.modify_font(font)
            label.set_max_width_chars(80)
            label.set_ellipsize(Pango.EllipsizeMode.END)
            label.set_line_wrap(True)
            label.set_visible(True)
            if self._columns[i] == 'summary':
                label.set_width_chars(50)
            else:
                label.set_width_chars(15)
            label.set_xalign(0)
            grid.attach(label, i, 0, 1, 1)

        return grid

    def on_typing(self, widget, event):
        keyval = event.keyval
        self._keys[keyval] = True
        selected_row = self._view.listbox.get_selected_row()

        keyval = event.keyval
        if keyval == Gdk.KEY_Up:
            # Handle up arrow key
            if selected_row:
                rows = self._view.listbox.get_children()
                index = rows.index(selected_row)
                if index > 0:
                    prev_row = self._view.listbox.get_row_at_index(index - 1)
                    self._view.listbox.select_row(prev_row)
            return True  # To prevent further processing of the event
        elif keyval == Gdk.KEY_Down:
            # Handle down arrow key
            if selected_row:
                rows = self._view.listbox.get_children()
                index = rows.index(selected_row)
                if index < len(rows) - 1:
                    next_row = self._view.listbox.get_row_at_index(index + 1)
                    self._view.listbox.select_row(next_row)
            else:
                selected_row = self._view.listbox.get_row_at_index(0)
                self._view.listbox.select_row(selected_row)
            return True  # To prevent further processing of the event
        elif keyval == Gdk.KEY_Return:
            if selected_row:
                selected_row.activate()
        return False  # Allow further processing of the event

    def on_key_press(self, widget, event):
        k = event.keyval
        self._keys[k] = True
        print("on_key_release", event)
        print(f"{k} = {self._keys[k]}")

    def on_key_release(self, widget, event):
        k = event.keyval
        self._keys[k] = False
        print("on_key_release", event)
        print(f"{k} = {self._keys[k]}")

    def is_key_pressed(self, k):
        if k not in self._keys:
            return False
        print(f"{k} = {self._keys[k]}")
        return self._keys[k]


class FilterCheckMenuItem(Gtk.CheckMenuItem):
    def __init__(self, label, filter_group_name, filter_value, filter_toggle_callback):
        super().__init__(label=label)
        self._filter_group_name = filter_group_name
        self._filter_value = filter_value
        self.connect("toggled", filter_toggle_callback)

    def get_filter_info(self):
        return self._filter_group_name, self._filter_value

