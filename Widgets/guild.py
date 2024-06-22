from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty
from kivy.app import App


class Guild(BoxLayout):
    text: StringProperty = StringProperty()
    guild_id: StringProperty = StringProperty()
    icon: StringProperty = StringProperty()
    members: NumericProperty = NumericProperty()
    online: NumericProperty = NumericProperty()

    def open_guild(self) -> None:
        App.get_running_app().set_guild(self.guild_id)
        App.get_running_app().set_screen('guild')
