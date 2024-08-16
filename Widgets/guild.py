from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty
from kivy.app import App

# set shortcuts for annoying to type functions
gRA = App.get_running_app

class Guild(BoxLayout):
    text: StringProperty = StringProperty()
    guildId: StringProperty = StringProperty()
    icon: StringProperty = StringProperty()
    members: NumericProperty = NumericProperty()
    online: NumericProperty = NumericProperty()

    def openGuild(self) -> None:
        gRA().setGuild(self.guildId)
        gRA().setScreen('guild')
