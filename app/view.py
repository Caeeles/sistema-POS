from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty

class MainWindow(BoxLayout):
    username = StringProperty("first.carlos")
    role = StringProperty("user")

    def __init__(self, **kw):
        super().__init__(**kw)

    def change_screen(self, screen_name):
        """Método para trocar de tela"""
        self.ids.scrn_mngr.current = screen_name