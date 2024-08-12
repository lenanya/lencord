from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty, ColorProperty
from kivy.app import App


class Message(BoxLayout):
    author: StringProperty = StringProperty()
    reply: StringProperty = StringProperty()
    text: StringProperty = StringProperty()
    messageId: StringProperty = StringProperty()
    imageLink: StringProperty = StringProperty()
    imageHeight: NumericProperty = NumericProperty()
    attachmentLink: StringProperty = StringProperty()
    backgroundColor: ColorProperty = ColorProperty()
    
    def setReply(self):
        # why did i make that a dict and not just 2 strings
        App.get_running_app().drv.reply = {"replyId": self.messageId, "replyAuthor": self.author}
        App.get_running_app().drv.setReply()
