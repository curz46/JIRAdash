import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gio', '2.0')
from gi.repository import Gtk, Gdk, Gio, GObject

WIDTH  = 800
HEIGHT = 200


class Item(GObject.GObject):

    text = GObject.property(type = str)

    def __init__(self):
        GObject.GObject.__init__(self)

class MyWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Search Query", type=Gtk.WindowType.POPUP)
        self.set_size_request(WIDTH, HEIGHT)
        self.set_resizable(False)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(vbox)

        textbox = Gtk.Entry()
        #textbox.set_size_request(WIDTH, 5)
        vbox.pack_start(textbox, True, True, 0)

        item = Item()
        item.text = "Hello"

        liststore = Gio.ListStore()
        liststore.append(item)
        liststore.append(item)
        liststore.append(item)
        liststore.append(item)

        listbox = Gtk.ListBox()
        listbox.bind_model(liststore, self.create_widget_func)

        vbox.pack_start(listbox, True, True, 0)

        self.add(listbox)

    def create_widget_func(self, item):
        label=Gtk.Label(item.text)
        return label

def init_window():
    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    style_context = Gtk.StyleContext()
    style_context.add_provider_for_screen(
            screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
    css = b"""
    entry { min-height: 0px; }
    """
    provider.load_from_data(css)

    win = MyWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
