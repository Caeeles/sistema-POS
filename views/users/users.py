from datetime import datetime
import hashlib
from threading import Thread
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock, mainthread

from kivy.properties import StringProperty, ObjectProperty

from widgets.popups import ConfirmDialog

Builder.load_file('views/users/users.kv')

class Users(BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        Clock.schedule_once(self.render, .1)
        self.currentUser = None

    def render(self, _):
        tl = Thread(target = self.get_users, daemon=True)
        tl.start()

    def add_new(self):
        md = ModUser()
        md.callback = self.add_user
        md.open()

    def get_users(self):
        users = [
                {
                "firstName": "Carlos",
                "lastName": "Silva",
                "username": "caeeles",
                "password": "102030",
                "createdAt": "2024/01/12 12:45:00",
                "signedIn": "2024/01/12 14:45:00"
                },{
                "firstName": "Bacalhau",
                "lastName": "Silva",
                "username": "bacalinda",
                "password": "102030",
                "createdAt": "2024/01/12 12:45:00",
                "signedIn": "2024/01/12 14:45:00"
                },{
                "firstName": "Junior",
                "lastName": "Silva",
                "username": "rolalixo",
                "password": "102030",
                "createdAt": "2024/01/12 12:45:00",
                "signedIn": "2024/01/12 14:45:00"
                },
        ]
        self.set_users(users)
    
    def add_user(self, mv):
        fname = mv.ids.fname
        lname = mv.ids.lname
        uname = mv.ids.uname
        pwd = mv.ids.pwd
        cpwd = mv.ids.cpwd
        #verificar se os campos não estão em branco
        if len(fname.text.strip()) < 3:
            #informar que o fname é inválido
            return
        
        _pwd = pwd.text.strip()
        upass = hashlib.sha256(_pwd.encode()).hexdigest()
        now = datetime.now()
        _now = datetime.strftime(now, "%Y/%m/%d %H:%M")
        user = {
                "firstName": fname.text.strip(),
                "lastName": lname.text.strip(),
                "username": uname.text.strip(),
                "password": upass,
                "createdAt": _now,
                "signedIn": "2024/01/12 14:45:00"
            }
        
        self.set_users([user])

    def update_user(self, user):
        mv = ModUser()
        mv.first_name = user.first_name
        mv.last_name = user.last_name
        mv.username = user.username
        mv.callback = self.set_update

        mv.open()


    def set_update(self, mv):
        print("Updating...")
      

    @mainthread
    def set_users(self, users:list):
        grid = self.ids.gl_users
        grid.clear_widgets()

        for u in users:
            ut = UserTile()
            ut.first_name = u['firstName']
            ut.last_name = u['lastName']
            ut.username = u['username']
            ut.password = u['password']
            ut.created = u['createdAt']
            ut.last_login = u['signedIn']
            ut.callback = self.delete_user
            ut.bind(on_release=self.update_user)

            grid.add_widget(ut)

    def delete_user(self, user):
        self.currentUser = user
        dc = ConfirmDialog()
        dc.title = "Apagar Usuário"
        dc.subtitle = "Está certo que deseja deletar este usuário?"
        dc.textConfirm = "Sim, Apagar"
        dc.textCancel = "Cancelar"
        dc.confirmColor = App.get_running_app().color_tertiary
        dc.cancelColor = App.get_running_app().color_primary
        dc.confirmCallback = self.delete_from_view
        dc.open()

    def delete_from_view(self, confirmDialog):

        if self.currentUser:
            self.currentUser.parent.remove_widget(self.currentUser)


class UserTile(ButtonBehavior, BoxLayout):
    first_name = StringProperty("")
    last_name = StringProperty("")
    username = StringProperty("")
    password = StringProperty("")
    created = StringProperty("")
    last_login = StringProperty("")
    callback = ObjectProperty(allownone=True)
    def __init__(self, **kw) -> None:
        super().__init__(**kw)
        Clock.schedule_once(self.render, .1)

    def render(self, _):
        pass

    def delete_user(self):
        if self.callback:
            self.callback(self)

class ModUser(ModalView):
    first_name = StringProperty("")
    last_name = StringProperty("")
    username = StringProperty("")
    created = StringProperty("")
    last_login = StringProperty("")
    callback = ObjectProperty(allownone = True)
    def __init__(self, **kw) -> None:
        super().__init__(**kw)
        Clock.schedule_once(self.render, .1)

    def render(self, _):
        pass

    def on_first_name(self, inst, fname):
        self.ids.fname.text = fname
        self.ids.title.text = "Modificar Usuário"
        self.ids.btn_confirm.text = "Modificar"
        self.ids.subtitle.text = "Registre suas novas informações de usuário"

    def on_last_name(self, inst, lname):
        self.ids.lname.text = lname

    def on_username(self, inst, uname):
        self.ids.uname.text = uname