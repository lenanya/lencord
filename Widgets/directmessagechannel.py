from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.app import App

# set shortcuts for annoying to type functions
gRA = App.get_running_app


# why is this its own file
class DirectMessageChannel(BoxLayout):
    text: StringProperty = StringProperty()
    channelId: StringProperty = StringProperty()

    def openChannel(self) -> None:
        gRA().setChannel(self.channelId)
        gRA().setScreen('channel')
