import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

Builder.load_file("views/auth/auth.kv")

class Auth(BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        print("IDs disponíveis na tela de autenticação:", self.ids)

    def authenticate(self):
        username = self.ids.username.text
        password = self.ids.password.text
        response = requests.post('http://127.0.0.1:5000/login', json={"username": username, "password": password})
        
        print("Status Code:", response.status_code)
        print("Response Headers:", response.headers)
        print("Response Text:", response.text)
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                print("Resposta JSON do servidor:", response_data)

                if response_data.get("status") == "success":
                    app = App.get_running_app()
                    app.authenticated_user = username
                    app.root.ids.scrn_mngr.current = 'scrn_admin'

                    self.clear_fields()
            except ValueError:
                print("Erro ao decodificar a resposta JSON")
        else:
            print(f"Erro na autenticação: {response.status_code}")

    def clear_fields(self):
        """Limpa os campos de texto de autenticação."""
        username_field = self.ids.get('username')
        password_field = self.ids.get('password')

        if username_field:
            username_field.text = ''
        if password_field:
            password_field.text = ''

class AuthApp(App):
    def build(self):
        self.authenticated_user = None
        return Auth()

if __name__ == '__main__':
    AuthApp().run()
