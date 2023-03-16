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


class MyWindow(Gtk.Window):
    def __init__(self, conn, schema):
        self._dbconn = conn
        self._columns = schema["gui"]["columns"]
        self._filters = schema["gui"]["filters"]
        self._active_filters = schema["gui"]["filters"]["default_filters"]

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

        self.create_filter_buttons(filter_box)

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

    def create_filter_buttons(self, filter_box):
        cur = self._dbconn.cursor()
        #cur.execute(f"SELECT DISTINCT {self._filters['field']} FROM issues ORDER BY {self._filters['field']} ASC LIMIT 10")
        cur.execute(f"""SELECT {self._filters['field']}, COUNT(*) as count
                    FROM issues
                    GROUP BY {self._filters['field']}
                    ORDER BY count DESC
                    LIMIT 8""")

        for row in cur.fetchall():
            filter_value = row[0]
            button = Gtk.ToggleButton(label=filter_value)
            button.set_active(filter_value in self._active_filters)
            button.connect("toggled", self.on_filter_button_toggled, filter_value)
            filter_box.pack_start(button, False, False, 0)

    def on_filter_button_toggled(self, button, filter_value):
        if button.get_active():
            self._active_filters.append(filter_value)
        else:
            self._active_filters.remove(filter_value)

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

        if query == "":
            return

        cur = self._dbconn.cursor()

        select_columns = ", ".join(self._columns)
        query_columns = " OR ".join([f"{col} LIKE ?" for col in self._columns])
        filter_condition = f"{self._filters['field']} IN ({','.join(['?'] * len(self._active_filters))})"

        cur.execute(f"SELECT {select_columns} FROM issues WHERE ({query_columns}) AND ({filter_condition}) ORDER BY updated_time LIMIT 100",
                    tuple([f"%{query}%"] * len(self._columns) + list(self._active_filters)))
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
    css = b"""
    * {
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
        font-size: 14px;
    }

    window {
        background-color: #F0F0F0;
        border-radius: 6px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }

    entry {
        min-height: 30px;
        padding: 5px 10px;
        background-color: #FFFFFF;
        border: 1px solid #CCCCCC;
        border-radius: 3px;
    }

    entry:focus {
        border-color: #66AFE9;
    }

    listbox {
        background-color: #FFFFFF;
    }

    label {
        padding: 5px 10px;
        color: #333333;
    }

    label:hover {
        background-color: #F0F0F0;
    }

    box {
        padding: 10px;
    }
    """
    provider.load_from_data(css)

    win = MyWindow(conn, schema)
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
