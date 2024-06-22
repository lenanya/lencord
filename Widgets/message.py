from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty, ColorProperty
from kivy.app import App


class Message(BoxLayout):
    author: StringProperty = StringProperty()
    reply: StringProperty = StringProperty()
    text: StringProperty = StringProperty()
    message_id: StringProperty = StringProperty()
    image_link: StringProperty = StringProperty()
    image_h: NumericProperty = NumericProperty()
    attachment_link: StringProperty = StringProperty()
    background_color: ColorProperty = ColorProperty()
    
    def set_reply(self):
        # why did i make that a dict and not just 2 strings
        App.get_running_app().drv.reply = {"reply_id": self.message_id, "reply_author": self.author} #
        App.get_running_app().drv.set_reply()
