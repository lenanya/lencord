from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.app import App


# why is this its own file
class DirectMessageChannel(BoxLayout):
    text: StringProperty = StringProperty()
    channel_id: StringProperty = StringProperty()

    def open_channel(self) -> None:
        App.get_running_app().set_channel(self.channel_id)
        App.get_running_app().set_screen('channel')
