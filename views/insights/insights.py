
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

Builder.load_file('views/insights/insights.kv')

class Insights(BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        Clock.schedule_once(self.render, .1)

    def render(self, _):
        pass
