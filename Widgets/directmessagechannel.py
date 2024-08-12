from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.app import App


# why is this its own file
class DirectMessageChannel(BoxLayout):
    text: StringProperty = StringProperty()
    channelId: StringProperty = StringProperty()

    def openChannel(self) -> None:
        App.get_running_app().setChannel(self.channelId)
        App.get_running_app().setScreen('channel')
