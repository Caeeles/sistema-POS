from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock, mainthread

Builder.load_file("views/admin/admin.kv")
class Admin(BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw)

    def authenticate(self, user_name):
        App.get_running_app().root.ids.scrn_mngr.current = 'scrn_home'
        print(f"User {user_name} authenticated successfully.")