from datetime import datetime
from werkzeug.security import generate_password_hash
from threading import Thread
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock, mainthread

from kivy.properties import StringProperty, ObjectProperty, ListProperty
from api.db import get_session
from api.models import User
from widgets.popups import ConfirmDialog

Builder.load_file('views/users/users.kv')

# Dicionário de permissões
PERMISSIONS = {
    'Vendedor': ['view'],
    'Supervisor': ['view'],
    'Gerente': ['view', 'add', 'update'],
    'Superusuário': ['view', 'add', 'update', 'delete']
}

def has_permission(user_role, action):
    return action in PERMISSIONS.get(user_role, [])

class Users(BoxLayout):
    current_user_role = StringProperty("")
    
    def __init__(self, **kw):
        super().__init__(**kw)
        self.currentUser = None
        self.bind(current_user_role=self.on_current_user_role_change)
        App.get_running_app().bind(authenticated_user=self.on_authenticated_user_change)
        self.set_current_user_role()
        Clock.schedule_once(self.render, .1)

    def on_current_user_role_change(self, instance, value):
        print(f"Current user role updated: {value}")

    def on_authenticated_user_change(self, instance, value):
        self.set_current_user_role()

    def set_current_user_role(self):
        username = App.get_running_app().authenticated_user
        if username:
            print(f"Fetching role for authenticated user: {username}")
            user_info = self.get_user_info(username)
            if user_info:
                self.current_user_role = user_info.role
                print(f"Current user role set to: {self.current_user_role}")
            else:
                print("User info not found")
        else:
            print("No user authenticated")

    def get_user_info(self, username):
        with get_session() as session:
            try:
                user = session.query(User).filter(User.username == username).first()
                if user:
                    return user
                else:
                    print(f"Usuário não encontrado: {username}")
                    return None
            except Exception as e:
                print(f"Erro ao buscar informações do usuário: {e}")
                return None
            
    def get_users(self):
        with get_session() as session:
            users = session.query(User).all()
            user_list = []
            for user in users:
                user_list.append({
                    "first_name": user.fname,
                    "last_name": user.lname,
                    "username": user.username,
                    "password": user.password,
                    "created": user.created_at.strftime("%Y/%m/%d %H:%M"),
                    "user_role": user.role
                })
            self.set_users(user_list)

    def render(self, _):
        tl = Thread(target=self.get_users, daemon=True)
        tl.start()

    def add_new(self):
        if not has_permission(self.current_user_role, 'add'):
            print("Você não tem permissão para adicionar um novo usuário.")
            return
        md = ModUser(current_user_role=self.current_user_role)
        md.callback = self.add_user
        md.open()
    
    def add_user(self, mv):
        if not has_permission(self.current_user_role, 'add'):
            print("Você não tem permissão para adicionar um novo usuário.")
            return
        fname = mv.ids.fname
        lname = mv.ids.lname
        uname = mv.ids.uname
        pwd = mv.ids.pwd
        cpwd = mv.ids.cpwd
        role = mv.ids.role

        if len(fname.text.strip()) < 3:
            print("Nome inválido.")
            return
        
        if pwd.text != cpwd.text:
            print("As senhas não coincidem.")
            return
        
        if self.current_user_role != 'Superusuário' and role.text.strip() in ['Gerente', 'Superusuário']:
            print("Você não tem permissão para atribuir esses cargos.")
            return

        _pwd = pwd.text.strip()
        upass = generate_password_hash(_pwd)
        now = datetime.now()

        user = User(
            fname=fname.text.strip(),
            lname=lname.text.strip(),
            username=uname.text.strip(),
            password=upass,
            created_at=now,
            role=role.text.strip()
        )

        with get_session() as session:
            session.add(user)
            session.commit()

        # Atualizar a lista de usuários após adicionar
        self.get_users()

    def update_user(self, user):
        if not has_permission(self.current_user_role, 'update'):
            # Informar que o usuário não tem permissão
            print("Você não tem permissão para atualizar este usuário.")
            return
        mv = ModUser(current_user_role=self.current_user_role)
        mv.ids.fname.text = user.first_name
        mv.ids.lname.text = user.last_name
        mv.ids.uname.text = user.username
        mv.ids.role.text = user.user_role
        mv.callback = self.set_update

        mv.open()

    def set_update(self, mv):
        if not has_permission(self.current_user_role, 'update'):
            print("Você não tem permissão para atualizar este usuário.")
            return

        fname = mv.ids.fname
        lname = mv.ids.lname
        uname = mv.ids.uname
        pwd = mv.ids.pwd
        role = mv.ids.role

        with get_session() as session:
            user = session.query(User).filter_by(username=uname.text.strip()).first()
            if user:
                if self.current_user_role == 'Gerente' and user.role in ['Gerente', 'Superusuário']:
                    print("Apenas um Superusuário tem permissão para atualizar este usuário.")
                    return

                user.fname = fname.text.strip()
                user.lname = lname.text.strip()

                # Verificar se o cargo pode ser atribuído
                if self.current_user_role != 'Superusuário' and role.text.strip() in ['Gerente', 'Superusuário']:
                    print("Você não tem permissão para atribuir esses cargos.")
                    return

                user.role = role.text.strip()
                if pwd.text:
                    user.password = generate_password_hash(pwd.text.strip())
                session.commit()

        # Atualizar a lista de usuários após atualizar
        self.get_users()
      
    @mainthread
    def set_users(self, users: list):
        print(f"Updating user list with {len(users)} users")
        grid = self.ids.gl_users
        grid.clear_widgets()

        for u in users:
            ut = UserTile()
            ut.first_name = u['first_name']
            ut.last_name = u['last_name']
            ut.username = u['username']
            ut.password = u['password']
            ut.created = u['created']
            ut.user_role = u['user_role']
            ut.callback = self.delete_user
            ut.bind(on_release=self.update_user)

            grid.add_widget(ut)

    def delete_user(self, user):
        if not has_permission(self.current_user_role, 'delete'):
            # Informar que o usuário não tem permissão
            print("Você não tem permissão para deletar este usuário.")
            return
        self.currentUser = user
        dc = ConfirmDialog()
        dc.title = "Apagar Usuário"
        dc.subtitle = "Está certo que deseja deletar este usuário?"
        dc.textConfirm = "Sim, Apagar"
        dc.textCancel = "Cancelar"
        dc.confirmColor = App.get_running_app().color_tertiary
        dc.cancelColor = App.get_running_app().color_primary
        dc.confirmCallback = self.confirm_delete
        dc.open()
    def confirm_delete(self, *args):
        uname = self.currentUser.username
        with get_session() as session:
            user = session.query(User).filter(User.username == uname).first()
            if user:
                session.delete(user)
                session.commit()

        self.get_users()

class UserTile(ButtonBehavior, BoxLayout):
    first_name = StringProperty("")
    last_name = StringProperty("")
    username = StringProperty("")
    password = StringProperty("")
    created = StringProperty("")
    user_role = StringProperty("")
    callback = ObjectProperty(allownone=True)
    
    # def __init__(self, **kw) -> None:
    #     super().__init__(**kw)
    #     Clock.schedule_once(self.render, .1)

    # def render(self, _):
    #     pass

    def delete_user(self):
        if self.callback:
            self.callback(self)

class ModUser(ModalView):
    first_name = StringProperty("")
    last_name = StringProperty("")
    username = StringProperty("")
    created = StringProperty("")
    user_role = StringProperty("")
    current_user_role = StringProperty("")  # Adicione esta linha
    callback = ObjectProperty(allownone=True)
    spinner_values = ListProperty(['Vendedor', 'Supervisor', 'Gerente', 'Superusuário'])  # Adicione esta linha
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_spinner_values()
        print(f"Modal user initialized with role: {self.current_user_role}")

    def update_spinner_values(self):
        if self.current_user_role != 'Superusuário':
            self.spinner_values = ['Vendedor', 'Supervisor']
        else:
            self.spinner_values = ['Vendedor', 'Supervisor', 'Gerente', 'Superusuário']

    def close(self):
        self.dismiss()

    def save(self):
        if self.callback:
            self.callback(self)
        self.dismiss()
