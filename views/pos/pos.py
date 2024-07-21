
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.metrics import dp, sp
from kivy.utils import rgba, QueryDict

from kivy.clock import Clock, mainthread

from kivy.properties import StringProperty, ListProperty, ColorProperty, NumericProperty, ObjectProperty

from random import randint

Builder.load_file( 'views/pos/pos.kv')
class Pos(BoxLayout):
    current_total = NumericProperty(0.0)
    current_cart = ListProperty([])
    def __init__(self, **kw) -> None:
        super().__init__(**kw)
        Clock.schedule_once(self.render, .1)

    def render(self, _):
        pass



    def add_product(self, inst):
        data = {
            "name": inst.name,
            "pcode": inst.pcode,
            "price": inst.price,
            "qty": 1
        }

        self.current_cart.append(data)

    def on_current_cart(self, inst, cart):
        self.ids.gl_products.clear_widgets()
        self.ids.gl_receipt.clear_widgets()
        
        for f in cart:
            self._add_product(f)
            self.add_receipt_item(f)
    
    def _add_product(self, product: dict):
        grid = self.ids.gl_products

        pt = ProductTile()
        pt.pcode = product.get("pcode", "")
        pt.name = product.get("name", "")
        pt.qty = product.get("qty", 0)
        pt.price = product.get("price", 0)
        pt.qty_callback = self.qty_control

        grid.add_widget(pt)

    def add_receipt_item(self, item: dict) -> None:
        rc = ReceiptItem()
        rc.name = item['name']
        rc.qty = item['qty']
        rc.price = item['price']

        self.ids.gl_receipt.add_widget(rc)

    def qty_control(self, tile, increasing=False):
        _qty = int(tile.qty)

        if increasing:
            _qty += 1
        else:
            _qty -= 1
            
            if _qty < 0:
                #perguntar ao usuário se ele quer deletar o produto
                _qty = 0

        tile.qty = _qty

class ProductTile(BoxLayout):
    pcode = StringProperty("")
    name = StringProperty("")
    qty = NumericProperty(0)
    price = NumericProperty(0)
    qty_callback = ObjectProperty(allownone = True)
    def __init__(self, **kw) -> None:
        super().__init__(**kw)
        Clock.schedule_once(self.render, .1)

    def render(self, _):
        pass

class ReceiptItem(BoxLayout):
    name = StringProperty("")
    qty = NumericProperty(0)
    price = NumericProperty(0)
    def __init__(self, **kw) -> None:
        super().__init__(**kw)
        Clock.schedule_once(self.render, .1)

    def render(self, _):
        pass