import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gio', '2.0')
from gi.repository import Gtk, Gdk, Gio, GObject, Pango

WIDTH  = 800
HEIGHT = 800

class Item(GObject.GObject):
    def __init__(self, fields):
        GObject.GObject.__init__(self)
        self.fields = fields

class FilterCheckMenuItem(Gtk.CheckMenuItem):
    def __init__(self, label, filter_group_name, filter_value, filter_toggle_callback):
        super().__init__(label=label)
        self._filter_group_name = filter_group_name
        self._filter_value = filter_value
        self.connect("toggled", filter_toggle_callback)

    def get_filter_info(self):
        return self._filter_group_name, self._filter_value

class MyWindow(Gtk.Window):
    def __init__(self, conn, schema):
        self._dbconn = conn
        self._columns = schema["gui"]["columns"]
        self._filters = schema["gui"]["filters"]
        self._active_filters = {filter_group: set(obj['default_filters']) for filter_group, obj in self._filters.items()}

        Gtk.Window.__init__(self, title="Search Query", type=Gtk.WindowType.POPUP)
        self.set_size_request(WIDTH, HEIGHT)
        self.set_resizable(False)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(vbox)

        entry_box = Gtk.Box()
        entry_box.set_size_request(-1, 60)  # Set the height of the input box
        vbox.pack_start(entry_box, False, False, 0)

        textbox = Gtk.Entry()
        textbox.set_valign(Gtk.Align.FILL)  # Fill the height of the input box
        textbox.set_max_length(200)  # Set the maximum length of the input text
        entry_box.pack_start(textbox, True, True, 0)
        textbox.connect("changed", self.on_text_changed)

        self._entry = textbox

        filter_box = Gtk.Box()
        vbox.pack_start(filter_box, False, False, 0)

        self.create_filter_menus(filter_box)

        self.liststore = Gio.ListStore()
        self.listbox = Gtk.ListBox()
        self.listbox.bind_model(self.liststore, self.create_widget_func)

        # Append columns
        item = Item(fields=self._columns)
        self.liststore.append(item)

        # Wrap the ListBox with a ScrolledWindow
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(self.listbox)
        vbox.pack_start(scrolled_window, True, True, 0)

        self.update_search_results("")

    def create_filter_menus(self, filter_box):
        for filter_group, filter_config in self._filters.items():
            filter_menu_button = Gtk.MenuButton.new()
            filter_menu_button.set_label(filter_group.capitalize())
            filter_menu = Gtk.Menu.new()

            cur = self._dbconn.cursor()
            cur.execute(f"""SELECT {filter_group}, COUNT(*) as count
                        FROM issues
                        GROUP BY {filter_group}
                        ORDER BY count DESC
                        LIMIT 20""")

            for row in cur.fetchall():
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

        self.update_search_results(self._entry.get_text())

    def create_widget_func(self, item):
        grid = Gtk.Grid()
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

    def on_text_changed(self, entry):
        query = entry.get_text().strip()
        self.update_search_results(query)

    def update_search_results(self, query):
        self.liststore.remove_all()

        cur = self._dbconn.cursor()

        select_columns = ", ".join(self._columns)
        query_columns = " OR ".join([f"{col} LIKE ?" for col in self._columns])

        filter_conditions = []
        filter_values = []
        for field, filter_set in self._active_filters.items():
            if filter_set:
                filter_conditions.append(f"{field} IN ({','.join(['?'] * len(filter_set))})")
                filter_values.extend(filter_set)

        filter_condition = " AND ".join(filter_conditions) if filter_conditions else "1"

        sql = f"""SELECT {select_columns} FROM issues
                  WHERE ({query_columns}) AND ({filter_condition})
                  ORDER BY updated_time DESC LIMIT 100"""

        cur.execute(sql, tuple([f"%{query}%"] * len(self._columns) + filter_values))

        # Append columns
        item = Item(fields=self._columns)
        self.liststore.append(item)

        for row in cur.fetchall():
            item = Item(fields=row)
            self.liststore.append(item)


def init_window(conn, schema):
    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    style_context = Gtk.StyleContext()
    style_context.add_provider_for_screen(
            screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
    provider.load_from_path("styles.css")

    win = MyWindow(conn, schema)
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
