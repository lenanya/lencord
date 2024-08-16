from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty
from kivy.app import App

# set shortcuts for annoying to type functions
gRA = App.get_running_app

class GuildChannel(BoxLayout):
    text: StringProperty = StringProperty()
    channelId: StringProperty = StringProperty()
    type: NumericProperty = NumericProperty()
    
    def openChannel(self) -> None:
        gRA().setChannel(self.channelId)
        gRA().setScreen('channel')
        