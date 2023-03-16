import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gio', '2.0')
from gi.repository import Gtk, Gdk

from dash.controller import DashController
from dash.model import DashModel

def init_window(conn, schema):
    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    style_context = Gtk.StyleContext()
    style_context.add_provider_for_screen(
        screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    provider.load_from_path("styles.css")

    model = DashModel(conn, schema)
    controller = DashController(model, schema)
    controller._view.connect("delete-event", Gtk.main_quit)
    controller._view.show_all()
    Gtk.main()
