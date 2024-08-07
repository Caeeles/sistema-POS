from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.properties import StringProperty, ListProperty, NumericProperty, ObjectProperty
from sqlalchemy.orm import Session
from api.models import Product, Stock, User, Sales, SaleDetails
from api.db import get_db
from widgets.popups import ConfirmDialog
from widgets.payment import PaymentScreen

from kivy.uix.popup import Popup
import json

Builder.load_file('views/pos/pos.kv')

class Pos(BoxLayout):
    current_total = NumericProperty(0.0)
    current_cart = ListProperty([])
    logged_user_name = StringProperty("")

    def on_logged_user_name(self, instance, value):
        print(f"Logged user name updated: {value}")

    def __init__(self, user_id=None, **kw):
        super().__init__(**kw)
        self.bind(logged_user_name=self.on_logged_user_name)
        App.get_running_app().bind(authenticated_user=self.on_authenticated_user_change)
        self.set_logged_user_name()
        Clock.schedule_once(self.render, .1)

    def on_authenticated_user_change(self, instance, value):
        self.set_logged_user_name()
        
    def set_logged_user_name(self):
        username = App.get_running_app().authenticated_user
        if username:
            print(f"Setting logged user name: {username}")
            self.logged_user_name = username
        else:
            print("No user authenticated")

    def get_user_info(self, username):
        db: Session = next(get_db())
        try:
            user = db.query(User).filter(User.username == username).first()
            if user:
                return user
            else:
                print(f"Usuário não encontrado: {username}")
                return None
        except Exception as e:
            print(f"Erro ao buscar informações do usuário: {e}")
            return None
        finally:
            db.close()
    
    def render(self, _):
        prods = self.load_products()
        self.ids.ti_search.products = prods

    def load_products(self):
        db: Session = next(get_db())
        products = db.query(Product).all()
        prods = []
        for product in products:
            stock = product.stock  # Acessar o relacionamento stock diretamente
            if stock:
                discount = stock.discount if stock.discount else 0
                price_with_discount = stock.price * (1 - discount / 100)
                prod = {
                    "name": product.pname,
                    "pcode": product.pcode,
                    "price": price_with_discount,
                    "qty": stock.istock
                }
            else:
                prod = {
                    "name": product.pname,
                    "pcode": product.pcode,
                    "price": 0,
                    "qty": 0
                }
            prods.append(prod)
        db.close()
        return prods

    def add_product(self, inst):
        data = {
            "name": inst.name,
            "pcode": inst.pcode,
            "price": inst.price,
            "qty": 1
        }

        temp = list(filter(lambda x: x['pcode'] == inst.pcode, self.current_cart))

        if len(temp) > 0:
            # Atualizar a quantidade
            grid = self.ids.gl_products
            tgt = None
            for c in grid.children:
                if c.pcode == temp[0]['pcode']:
                    tgt = c
                    break

            if tgt:
                self.qty_control(tgt, increasing=True)
        else:
            self.current_cart.append(data)
        self.update_total()  # Atualizar o total após adicionar produto

    def update_total(self):
        _total = 0
        for item in self.current_cart:
            _total += round(float(item['price']) * int(item['qty']), 2)
        self.current_total = _total

    def on_current_cart(self, inst, cart):
        self.ids.gl_products.clear_widgets()
        self.ids.gl_receipt.clear_widgets()
        for f in cart:
            self._add_product(f)
            self.add_receipt_item(f)
        self.update_total()

    def _add_product(self, product: dict):
        grid = self.ids.gl_products
        pt = ProductTile()
        pt.pcode = product.get("pcode", "")
        pt.name = product.get("name", "")
        pt.qty = product.get("qty", 0)
        pt.price = product.get("price", 0)
        pt.total_price = pt.price * pt.qty  # Atualizado para exibir o preço total
        pt.qty_callback = self.qty_control
        grid.add_widget(pt)

    def add_receipt_item(self, item: dict) -> None:
        rc = ReceiptItem()
        rc.name = item['name']
        rc.qty = item['qty']
        rc.price = item['price'] * item['qty']  # Preço total por item
        self.ids.gl_receipt.add_widget(rc)

    def qty_control(self, tile, increasing=False):
        _qty = int(tile.qty)
        if increasing:
            _qty += 1
        else:
            _qty -= 1
            if _qty < 0:
                _qty = 0

        data = {
            "name": tile.name,
            "pcode": tile.pcode,
            "price": tile.price,
            "qty": _qty
        }
        _id = tile.pcode

        tgt = None
        tmp = list(self.current_cart)
        for i, x in enumerate(tmp):
            if x['pcode'] == _id:
                tgt = i
                break

        if tgt is not None:
            self.current_cart.pop(tgt)
            if _qty > 0:
                self.current_cart.insert(tgt, data)
        tile.qty = _qty
        tile.total_price = tile.price * _qty  # Atualizar o preço total do item
        self.update_total()  # Atualizar o total após alterar quantidade

    def clear_cart(self, *args):
        self.current_cart = []
        self.update_total()  # Atualizar o total após limpar o carrinho

    def delete_cart(self):
        dc = ConfirmDialog()
        dc.title = "Apagar Compra"
        dc.subtitle = "Tem certeza que deseja apagar esse carrinho"
        dc.textConfirm = "Sim, Deletar"
        dc.textCancel = "Cancelar"
        dc.confirmColor = App.get_running_app().color_primary
        dc.cancelColor = App.get_running_app().color_tertiary
        dc.confirmCallback = self.clear_cart
        dc.open()

    def checkout_callback(self, *args):
        username = App.get_running_app().authenticated_user
        user = self.get_user_info(username)
        if not user:
            print("Usuário não autenticado ou não encontrado.")
            return

        total_sale = 0
        product_details = []

        db: Session = next(get_db())  # Adiciona essa linha para obter a sessão do banco de dados
        try:
            for item in self.current_cart:
                product = db.query(Product).filter(Product.pcode == item['pcode']).first()
                if product and product.stock:
                    if product.stock.istock >= item['qty']:
                        total_sale += item['price'] * item['qty']
                        product_details.append({"product_id": product.id, "qty": item['qty']})
                    else:
                        print(f"Estoque insuficiente para o produto: {product.pname}")
                else:
                    print(f"Produto não encontrado: {item['name']}")

            pm = PaymentScreen()
            pm.total_display = total_sale
            pm.confirmCallback = lambda payment_methods: self.save_sale_details(user.id, product_details, payment_methods)  # Passa user.id como user_id
            pm.open()
        except Exception as e:
            print(f"Erro durante o checkout: {e}")
        finally:
            db.close()  # Certifique-se de fechar a sessão do banco de dados
    

    def save_sale_details(self, user_id, product_details, payment_methods):
        db = next(get_db())
        try:
            total_paid = sum(float(payment_methods[method]) for method in payment_methods)
            change = total_paid - self.current_total

            # Adicionando prints para depuração
            print(f"Total pago: {total_paid}, Total esperado: {self.current_total}, Troco calculado: {change}")

            sale = Sales(
                user_id=user_id,
                total=self.current_total
            )
            db.add(sale)
            db.commit()
            sale_id = sale.id

            for item in product_details:
                product = db.query(Product).filter(Product.id == item['product_id']).first()
                if product and product.stock:
                    product.stock.istock -= item['qty']
                    product.stock.sold += item['qty']

            sale_details = SaleDetails(
                sale_id=sale_id,
                total_paid=total_paid,
                change=change,
                payment_methods=json.dumps(payment_methods),
                product_details=json.dumps(product_details)
            )
            db.add(sale_details)
            db.commit()

            print("Detalhes da venda registrados com sucesso")

            # Limpar o carrinho após registrar os detalhes da venda
            self.clear_cart()
        except Exception as e:
            db.rollback()
            print(f"Erro ao registrar detalhes da venda: {e}")
        finally:
            db.close()

    def get_input_value_from_screen(self, input_id):
        try:
            input_widget = App.get_running_app().root.ids[input_id]
            value = input_widget.text
            return float(value) if value else 0.0
        except (ValueError, KeyError):
            return 0.0
    
    def checkout(self):
        dc = ConfirmDialog()
        dc.title = "Checkout"
        dc.subtitle = "Tem certeza que deseja concluir essa venda?"
        dc.textConfirm = "Sim, Checkout"
        dc.textCancel = "Cancelar"
        dc.confirmColor = App.get_running_app().color_primary
        dc.cancelColor = App.get_running_app().color_tertiary
        dc.confirmCallback = self.checkout_callback
        dc.open()
    
    def on_spinner_select(self, selection):
        if selection == 'Logout':
            self.logout()

    def logout(self):
        app = App.get_running_app()
        app.authenticated_user = ""  # Limpar o usuário autenticado
        self.set_logged_user_name()  # Atualizar o nome do usuário na interface
        self.clear_cart()  # Limpar o carrinho, se desejar

        screen_manager = app.root.ids.get('scrn_mngr', None)
        if screen_manager is None:
            print("ScreenManager não encontrado")
            return

        auth_screen = screen_manager.get_screen('scrn_auth')
        if auth_screen is None:
            print("Tela de autenticação não encontrada")
            return

        username_field = auth_screen.ids.get('username', None)
        password_field = auth_screen.ids.get('password', None)

        if username_field is None:
            print("ID 'username' não encontrado na tela de autenticação")
        if password_field is None:
            print("ID 'password' não encontrado na tela de autenticação")

        if username_field:
            username_field.text = ''
        if password_field:
            password_field.text = ''

        screen_manager.current = 'scrn_auth'
            
class ProductTile(BoxLayout):
    pcode = StringProperty("")
    name = StringProperty("")
    qty = NumericProperty(0)
    price = NumericProperty(0)
    total_price = NumericProperty(0)  # Adicionado para exibir o preço total
    qty_callback = ObjectProperty(allownone=True)

    def __init__(self, **kw) -> None:
        super().__init__(**kw)
        Clock.schedule_once(self.render, .1)

    def render(self, _):
        pass

class ReceiptItem(BoxLayout):
    name = StringProperty("")
    qty = NumericProperty(0)
    price = NumericProperty(0)  # Preço total do item

    def __init__(self, **kw) -> None:
        super().__init__(**kw)
        Clock.schedule_once(self.render, .1)

    def render(self, _):
        pass

