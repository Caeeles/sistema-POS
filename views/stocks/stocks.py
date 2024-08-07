from datetime import datetime
from threading import Thread
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock, mainthread
from kivy.properties import StringProperty, ObjectProperty

from api.db import get_session
from api.models import Product, Stock, User
from widgets.popups import ConfirmDialog

Builder.load_file('views/stocks/stocks.kv')

PERMISSIONS = {
    'Vendedor': ['view'],
    'Supervisor': ['view', 'add', 'update'],
    'Gerente': ['view', 'add', 'update'],
    'Superusuário': ['view', 'add', 'update', 'delete']
}

def has_permission(user_role, action):
    return action in PERMISSIONS.get(user_role, [])

class Stocks(Screen):
    screen_manager = ObjectProperty(None)
    current_user_role = StringProperty("")

    def __init__(self, **kw):
        super().__init__(**kw)
        self.currentProduct = None
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

    def render(self, _):
        tl = Thread(target=self.get_product, daemon=True)
        tl.start()

    def on_enter(self, *args):
        # Garante que o ScreenManager está acessível
        self.screen_manager = self.manager

    def add_new(self):
        if not has_permission(self.current_user_role, 'add'):
            print("Você não tem permissão para adicionar um novo produto.")
            return
        md = ModProduct()
        md.callback = self.add_product
        md.open()

    def get_product(self):
        with get_session() as session:
            products = session.query(Product).all()
            product_list = []
            for product in products:
                stock = session.query(Stock).filter_by(product_id=product.id).first()
                if stock:
                    product_list.append({
                        "product_name": product.pname,
                        "product_code": product.pcode,
                        "price": stock.price,
                        "in_stock": stock.istock,
                        "order_date": stock.odate.strftime("%Y/%m/%d %H:%M"),
                        "discount": stock.discount,
                        "sold": stock.sold
                    })
            self.set_products(product_list)

    def add_product(self, mv):
        if not has_permission(self.current_user_role, 'add'):
            print("Você não tem permissão para adicionar um novo produto.")
            return
        pname = mv.ids.pname.text.strip()
        pcode = mv.ids.pcode.text.strip()
        istock = mv.ids.istock.text.strip()
        price = mv.ids.price.text.strip()
        odate = mv.ids.odate.text.strip()

        if len(pname) < 3 or len(pcode) < 1:
            return

        try:
            price = float(price)
            istock = int(istock)
        except ValueError:
            return

        try:
            now = datetime.strptime(odate, "%Y/%m/%d %H:%M")
        except ValueError:
            now = datetime.now()

        with get_session() as session:
            # Verifica se o código do produto já existe
            existing_product = session.query(Product).filter_by(pcode=pcode).first()
            if existing_product:
                return  # Ou trate o caso de produto já existente de acordo com sua lógica

            # Adiciona novo produto
            product = Product(pname=pname, pcode=pcode)
            session.add(product)
            session.commit()

            # Adiciona estoque do produto
            stock = Stock(
                product_id=product.id,
                istock=istock,
                price=price,
                odate=now,
                discount=0,  # ou utilize o valor do campo discount se necessário
                sold=0
            )
            session.add(stock)
            session.commit()

            # Atualiza a lista de produtos
            self.get_product()

    def update_product(self, product):
        if not has_permission(self.current_user_role, 'update'):
            # Informar que o usuário não tem permissão
            print("Você não tem permissão para atualizar este produto.")
            return
        mv = ModProduct()
        mv.product_code = product.product_code
        mv.product_name = product.product_name
        mv.in_stock = product.in_stock
        mv.order_date = product.order_date
        mv.price = product.price
        mv.discount = product.discount
        mv.callback = self.set_update

        mv.open()

    def set_update(self, mv):
        if not has_permission(self.current_user_role, 'update'):
            # Informar que o usuário não tem permissão
            print("Você não tem permissão para atualizar este produto.")
            return
        pname = mv.ids.pname.text.strip()
        pcode = mv.ids.pcode.text.strip()
        istock = mv.ids.istock.text.strip()
        price = mv.ids.price.text.strip()
        odate = mv.ids.odate.text.strip()
        discount = mv.ids.discount.text.strip()

        if len(pname) < 3 or len(pcode) < 1 or len(odate) < 5:
            return

        try:
            price = float(price)
            istock = int(istock)
            discount = float(discount)
        except ValueError:
            return

        try:
            now = datetime.strptime(odate, "%Y/%m/%d %H:%M")
        except ValueError:
            now = datetime.now()

        # Atualiza o banco de dados
        with get_session() as session:
            # Encontra o produto e o estoque correspondente
            product = session.query(Product).filter_by(pcode=mv.product_code).first()
            if product:
                product.pname = pname
                session.commit()  # Atualiza o produto

                stock = session.query(Stock).filter_by(product_id=product.id).first()
                if stock:
                    stock.istock = istock
                    stock.price = price
                    stock.odate = now
                    stock.discount = discount
                    session.commit()  # Atualiza o estoque

        self.get_product()  # Atualiza a lista de produtos

# Adicione um evento on_release no seu botão de confirmação no arquivo .kv do ModProduct

    @mainthread
    def set_products(self, products: list):
        grid = self.ids.gl_products
        grid.clear_widgets()

        for u in products:
            ut = StockTile()
            ut.product_code = u['product_code']
            ut.product_name = u['product_name']
            ut.price = str(u['price'])
            ut.sold = str(u['sold'])
            ut.in_stock = str(u['in_stock'])
            ut.order_date = u['order_date']
            ut.discount = str(u['discount'])
            ut.product = u  # Atribua o produto aqui
            ut.delete_product_with_confirmation = self.delete_product_with_confirmation
            ut.bind(on_release=self.update_product)

            grid.add_widget(ut)

    def delete_product_with_confirmation(self, product):
        if not has_permission(self.current_user_role, 'delete'):
            # Informar que o usuário não tem permissão
            print("Você não tem permissão para deletar este produto.")
            return
        self.currentProduct = product
        dc = ConfirmDialog()
        dc.title = "Apagar Produto"
        dc.subtitle = "Está certo que deseja deletar este produto?"
        dc.textConfirm = "Sim, Apagar"
        dc.textCancel = "Cancelar"
        dc.confirmColor = App.get_running_app().color_tertiary
        dc.cancelColor = App.get_running_app().color_primary
        dc.confirmCallback = self.delete_product
        dc.open()

    def delete_product(self, confirmDialog):
        if self.currentProduct:
            product_code = self.currentProduct.get('product_code')  # Acessa o código do produto como chave de dicionário
            #print(f"Tentando deletar o produto com código: {product_code}")  # Linha para depuração

            with get_session() as session:
                product_in_db = session.query(Product).filter_by(pcode=product_code).first()
                if product_in_db:
                    session.query(Stock).filter_by(product_id=product_in_db.id).delete()
                    session.delete(product_in_db)
                    session.commit()
                    #print(f"Produto {product_code} deletado com sucesso.")  # Linha para depuração
                #else:
                    #print(f"Produto com código {product_code} não encontrado no banco de dados.")  # Mensagem de erro
            self.get_product()  # Atualiza a lista de produtos
        # else:
        #     print("Produto não encontrado ou já deletado.")
            
class StockTile(ButtonBehavior, BoxLayout):
    product = ObjectProperty(None)  # Propriedade que armazena o produto
    product_code = StringProperty("")
    product_name = StringProperty("")
    in_stock = StringProperty("")
    sold = StringProperty("")
    order_date = StringProperty("")
    price = StringProperty("")
    discount = StringProperty("")
    callback = ObjectProperty(allownone=True)
    confirm_delete_product = ObjectProperty(allownone=True)

    def __init__(self, **kw) -> None:
        super().__init__(**kw)
        Clock.schedule_once(self.render, .1)

    def render(self, _):
        pass

    def delete_product(self):
        if self.callback:
            self.callback(self)

class ModProduct(ModalView):
    product_code = StringProperty("")
    product_name = StringProperty("")
    in_stock = StringProperty("")
    sold = StringProperty("")
    order_date = StringProperty("")
    price = StringProperty("")
    discount = StringProperty("")
    callback = ObjectProperty(allownone=True)

    def __init__(self, **kw) -> None:
        super().__init__(**kw)
        Clock.schedule_once(self.render, .1)

    def render(self, _):
        pass

    def on_product_name(self, inst, pname):
        self.ids.pname.text = pname
        self.ids.title.text = "Modificar Produto"
        self.ids.btn_confirm.text = "Modificar"
        self.ids.subtitle.text = "Registre suas novas informações do produto"

    def on_product_code(self, inst, pcode):
        self.ids.pcode.text = pcode

    def on_in_stock(self, inst, istock):
        self.ids.istock.text = istock

    def on_price(self, inst, price):
        self.ids.price.text = price

    def on_order_date(self, inst, odate):
        self.ids.odate.text = odate

    def on_discount(self, inst, discount):
        self.ids.discount.text = discount

    def test_db_connection():
        with get_session() as session:
            #print("Conexão bem-sucedida!")
            products = session.query(Product).all()
            #print(f"Produtos no banco de dados: {products}")

    test_db_connection()
