from kivy.uix.modalview import ModalView
from kivy.properties import StringProperty, ObjectProperty, ColorProperty, NumericProperty
from kivy.clock import Clock
from kivy.lang import Builder

Builder.load_string("""
<PaymentScreen>:
    background: ""
    background_color: [0,0,0, .1]                
    BackBox:
        orientation: 'vertical'
        size_hint: [.7, .7]
        bcolor: app.color_primary_bg
        radius: [self.height*.08]
        padding: 20
        spacing: 10
        BackBox:
            orientation: 'vertical'
            size_hint_y: .2
            spacing: dp(10)
            padding: dp(12)
            Text:
                size_hint_y: .8
                color: app.color_primary_text
                text: "Pagamento"
                font_size: self.height*.8
                font_name: app.fonts.styled
                halign: "center"
                valign: "middle"
            Text:
                size_hint_y: .2
                color: app.color_secondary_text
                text: "Insira os detalhes do pagamento, abaixo:"
                font_size: self.height*.9
                font_name: app.fonts.body
                halign: "center"
                valign: "bottom"


        BoxLayout:
            orientation: 'vertical'
            size_hint_y: .7
            BoxLayout:
                size_hint_y: .15
                padding: [dp(64), 0, dp(64), 0]
                Text:
                    text: "Total a Pagar:"
                    color: app.color_primary_text
                    font_size: app.fonts.size.h1
                    font_name: app.fonts.body
                Text:
                    id: total_display
                    text: "R$ %s"%str(round(root.total_display, 2))
                    color: app.color_primary_text
                    halign: "right"
                    font_size: app.fonts.size.h1
                    font_name: app.fonts.body
            Divider:
            BoxLayout:
                size_hint_y: .7
                padding: [dp(64), dp(10)]
                spacing: dp(20)
                BoxLayout:
                    orientation: "vertical"
                    spacing: dp(10)
                    Text:
                        text: "Dinheiro"
                        halign: "right"
                        color: app.color_primary_text
                        font_size: app.fonts.size.h2
                        font_name: app.fonts.body
                    Text:
                        text: "Débito"
                        halign: "right"
                        color: app.color_primary_text
                        font_size: app.fonts.size.h2
                        font_name: app.fonts.body
                    Text:
                        text: "Crédito"
                        halign: "right"
                        color: app.color_primary_text
                        font_size: app.fonts.size.h2
                        font_name: app.fonts.body
                    Text:
                        text: "PIX"
                        halign: "right"
                        color: app.color_primary_text
                        font_size: app.fonts.size.h2
                        font_name: app.fonts.body
                BoxLayout:
                    orientation: "vertical"
                    spacing: dp(10)
                    BackBox:
                        bcolor: app.color_secondary_bg
                        padding: [0, dp(5)]
                        radius: [self.height*.1]
                        FlatField:
                            id: cash_input
                            hint_text: "insira o valor em espécie"
                            hint_text_color: app.color_secondary_text
                            input_filter: 'float'
                            color: app.color_primary_text
                            font_size: app.fonts.size.h2
                            multiline: False
                            on_text: root.calculate_change()
                    BackBox:
                        bcolor: app.color_secondary_bg
                        padding: [0, dp(5)]
                        radius: [self.height*.1]
                        FlatField:
                            id: debit_input
                            hint_text: "insira o valor do débito"
                            hint_text_color: app.color_secondary_text
                            input_filter: 'float'
                            color: app.color_primary_text
                            font_size: app.fonts.size.h2
                            multiline: False
                            on_text: root.calculate_change()
                    BackBox:
                        bcolor: app.color_secondary_bg
                        padding: [0, dp(5)]
                        radius: [self.height*.1]
                        FlatField:
                            id: credit_input
                            hint_text: "insira o valor do crédito"
                            hint_text_color: app.color_secondary_text
                            input_filter: 'float'
                            color: app.color_primary_text
                            font_size: app.fonts.size.h2
                            multiline: False
                            on_text: root.calculate_change()
                    BackBox:
                        bcolor: app.color_secondary_bg
                        padding: [0, dp(5)]
                        radius: [self.height*.1]
                        FlatField:
                            id: pix_input
                            hint_text: "insira o valor do pix"
                            hint_text_color: app.color_secondary_text
                            input_filter: 'float'
                            color: app.color_primary_text
                            font_size: app.fonts.size.h2
                            multiline: False
                            on_text: root.calculate_change()
            Divider:
            BoxLayout:
                size_hint_y: .15
                BoxLayout:
                BoxLayout:
                    padding: [0, 0, dp(64), 0]
                    Text:
                        text: "Troco"
                        color: app.color_primary_text
                        font_size: app.fonts.size.h1
                        font_name: app.fonts.body
                    Text:
                        id: change_amount
                        text: "R$ %s"%str(round(root.change_display, 2))
                        color: app.color_primary_text
                        halign: "right"
                        font_size: app.fonts.size.h1
                        font_name: app.fonts.body
        
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: .1
            height: 60
            spacing: dp(10)
            padding: [dp(64), 0, dp(64), 0]
            FlatButton:
                padding: 5
                text: 'Cancelar'
                color: app.color_tertiary
                font_size: app.fonts.size.h2
                on_release: root.cancel()
            RoundedButton:
                padding: 5
                text: 'Concluir Pagamento'
                color: rgba('#ffffff')
                bcolor: app.color_primary
                font_size: app.fonts.size.h2
                radius: [self.height*.1]
                on_release: root.complete()
                disabled: root.change_display <= (-0.51)
""")

class PaymentScreen(ModalView):
    callback = ObjectProperty(allownone=True)
    total_display = NumericProperty(0.0)
    change_display = NumericProperty(0.0)
    confirmCallback = ObjectProperty(allownone=True)
    CancelCallback = ObjectProperty(allownone=True)
    confirmColor = ColorProperty([1, 1, 1, 1])
    cancelColor = ColorProperty([1, 1, 1, 1])

    def __init__(self, **kw) -> None:
        super().__init__(**kw)
        Clock.schedule_once(self.render, .1)

    def render(self, _):
        pass
    
    def cancel(self):
        self.dismiss()
        if self.CancelCallback:
            self.CancelCallback(self)

    def complete(self):
        self.dismiss()
        if self.confirmCallback:
            payment_methods = {
                "cash": self.get_input_value('cash_input'),
                "debit": self.get_input_value('debit_input'),
                "credit": self.get_input_value('credit_input'),
                "pix": self.get_input_value('pix_input')
            }
            self.confirmCallback(payment_methods)

    def calculate_change(self):
        cash = self.get_input_value('cash_input')
        debit = self.get_input_value('debit_input')
        credit = self.get_input_value('credit_input')
        pix = self.get_input_value('pix_input')
        
        total_received = cash + debit + credit + pix
        self.change_display = total_received - self.total_display
        
        # Adicionando prints para depuração
        print(f"Valores inseridos - Dinheiro: {cash}, Débito: {debit}, Crédito: {credit}, PIX: {pix}")
        print(f"Total Recebido: {total_received}, Troco: {self.change_display}")

    def get_input_value(self, input_id):
        try:
            value = self.ids[input_id].text
            return float(value) if value else 0.0
        except ValueError:
            return 0.0
