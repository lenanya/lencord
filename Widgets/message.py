from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty, ColorProperty
from kivy.app import App

# set shortcuts for annoying to type functions
gRA = App.get_running_app

class Message(BoxLayout):
    author: StringProperty = StringProperty()
    reply: StringProperty = StringProperty()
    text: StringProperty = StringProperty()
    messageId: StringProperty = StringProperty()
    authorAvatar: StringProperty = StringProperty()
    imageHeight: NumericProperty = NumericProperty()
    attachmentLink: StringProperty = StringProperty()
    backgroundColor: ColorProperty = ColorProperty()
    
    def setReply(self):
        # why did i make that a dict and not just 2 strings
        gRA().drv.reply = {"replyId": self.messageId, "replyAuthor": self.author}
        gRA().drv.setReply()
