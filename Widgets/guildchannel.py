from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty
from kivy.app import App


class GuildChannel(BoxLayout):
    text: StringProperty = StringProperty()
    channelId: StringProperty = StringProperty()
    type: NumericProperty = NumericProperty()
    
    def openChannel(self) -> None:
        App.get_running_app().setChannel(self.channelId)
        App.get_running_app().setScreen('channel')
        