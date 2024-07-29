
from datetime import datetime
import hashlib
import json
import os
from threading import Thread
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock, mainthread

from kivy.properties import StringProperty, ObjectProperty

from widgets.popups import ConfirmDialog

Builder.load_file('views/stocks/stocks.kv')

class Stocks(BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.currentProduct = None
        Clock.schedule_once(self.render, .1)

    def render(self, _):
        tl = Thread(target = self.get_product, daemon=True)
        tl.start()

    def add_new(self):
        md = ModProduct()
        md.callback = self.add_product
        md.open()

    def get_product(self):

        products = []
        if os.path.exists("products.json"):
            with open("products.json", "r") as f:
                products = json.load(f)
        self.set_products(products)
    
    def add_product(self, mv):
        pname = mv.ids.pname
        pcode = mv.ids.pcode
        istock = mv.ids.istock
        price = mv.ids.price
        odate = mv.ids.odate
        #verificar se os campos não estão em branco
        if len(pname.text.strip()) < 3:
            #informar que o fname é inválido
            return
        
        if len(odate.text.strip()) < 5:
            now = datetime.now()
            _now = datetime.strftime(now, "%Y/%m/%d %H:%M")
        else: 
            _now = odate.text.strip()

        product = {
                "product_name": pname.text.strip(),
                "product_code": pcode.text.strip(),
                "price": price.text.strip(),
                "in_stock": istock.text.strip(),
                "order_date": _now,
                "discount": 0,
                "sold": 0
            }
        
        products = []
        if os.path.exists("products.json"):
            with open("products.json", "r") as f:
                products = json.load(f)

        products.append(product)
        with open("products.json", "w") as f:
            json.dump(products, f)
        
        self.set_products([product])

    def update_product(self, product):
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
        print("Updating...")
      
    @mainthread
    def set_products(self, products:list):
        grid = self.ids.gl_products
        grid.clear_widgets()

        for u in products:
            ut = StockTile()
            ut.product_code = u['product_code']
            ut.product_name = u['product_name']
            ut.price = u['price']
            ut.sold = str(u['sold'])
            ut.in_stock = u['in_stock']
            ut.order_date = u['order_date']
            ut.discount = str(u['discount'])
            ut.callback = self.delete_product
            ut.bind(on_release=self.update_product)

            grid.add_widget(ut)

    def delete_product(self, user):
        self.currentProduct = user
        dc = ConfirmDialog()
        dc.title = "Apagar Produto"
        dc.subtitle = "Está certo que deseja deletar este produto?"
        dc.textConfirm = "Sim, Apagar"
        dc.textCancel = "Cancelar"
        dc.confirmColor = App.get_running_app().color_tertiary
        dc.cancelColor = App.get_running_app().color_primary
        dc.confirmCallback = self.delete_from_view
        dc.open()

    def delete_from_view(self, confirmDialog):

        if self.currentProduct:
            self.currentProduct.parent.remove_widget(self.currentProduct)

            self.currentProduct = None

class StockTile(ButtonBehavior, BoxLayout):
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
    callback = ObjectProperty(allownone = True)
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