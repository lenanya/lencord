from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty
from kivy.app import App


class Guild(BoxLayout):
    text: StringProperty = StringProperty()
    guildId: StringProperty = StringProperty()
    icon: StringProperty = StringProperty()
    members: NumericProperty = NumericProperty()
    online: NumericProperty = NumericProperty()

    def openGuild(self) -> None:
        App.get_running_app().setGuild(self.guildId)
        App.get_running_app().setScreen('guild')
