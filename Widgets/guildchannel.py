from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty
from kivy.app import App


class GuildChannel(BoxLayout):
    text: StringProperty = StringProperty()
    channel_id: StringProperty = StringProperty()
    type: NumericProperty = NumericProperty()
    
    def open_channel(self) -> None:
        App.get_running_app().set_channel(self.channel_id)
        App.get_running_app().set_screen('channel')
        