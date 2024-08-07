from os.path import dirname, join

from kivy.garden.iconfonts import register
from api.db import init_db
from app import MainApp

# Registro dos ícones
register(
    "FeatherIcons",
    join(dirname(__file__), "assets/fonts/feather/feather.ttf"),
    join(dirname(__file__), "assets/fonts/feather/feather.fontd"),
)

# Inicializar db
init_db()

MainApp().run()