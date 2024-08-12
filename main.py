from DiscordAPI.api_access import API

from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.recycleview import RecycleView
from kivy.clock import Clock, ClockEvent
from kivy.factory import Factory

from Widgets.message import Message
from Widgets.guildchannel import GuildChannel
from Widgets.guild import Guild
from Widgets.directmessagechannel import DirectMessageChannel


# yes this needs to be here
class DirectMessageListScreen(Screen):
    pass


# this too
class LoginScreen(Screen):
    pass


class DMRV(RecycleView):

    #TODO: refactor to use get
    def getChannels(self):
        dmChannels = App.get_running_app().api.getDirectMessageChannels()
        # i love list comprehensions
        data = [{'text': channel['name'], 'channelId': channel['id']} for channel in dmChannels]
        self.data = data

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.getChannels()


class GRV(RecycleView):

    #TODO: refactor to use get
    def getGuilds(self):
        guilds: list = App.get_running_app().api.getGuilds()
        iconURL: str = "https://cdn.discordapp.com/icons/"
        data: list = []
        for guild in guilds:
            name: str = guild['name']
            guildId: str = guild['id']
            icon: str = f"{iconURL}{guild['id']}/{guild['icon']}"
            data.append({'text': name, 'guildId': guildId, 'icon': icon})
        self.data = data

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.getGuilds()


# oh boy
class ChannelScreen(Screen):

    refreshEvent: ClockEvent
    attachment: str|None = None

    def fileChooser(self):
        if self.attachment:
            self.ids.attach.text = "Attach image"
            self.attachment = None
        else:
            Factory.FilePicker().open()

    def on_pre_enter(self, *args):
        App.get_running_app().drv.getMessages()
        self.refreshEvent = Clock.schedule_interval(App.get_running_app().drv.loadNewMessages, 2)
        super().on_pre_enter(*args)

    # i use App.get_running_app() way too much edit: yep
    def sendMessage(self):
        messageContent: str = self.ids.messageInput.text
        if messageContent == "" and not self.attachment:
            return None
        self.ids.messageInput.text = ""
        reply = App.get_running_app().drv.reply
        attachment = self.attachment
        self.attachment = None
        self.ids.attach.text = "Attach image"
        App.get_running_app().drv.reply = None
        App.get_running_app().drv.setReply()
        App.get_running_app().api.sendMessage(App.get_running_app().currentChat, messageContent, reply, attachment)

    def on_leave(self, *args):
        self.refreshEvent.cancel()
        App.get_running_app().drv.reply = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        App.get_running_app().channelScreen = self


# i should really standardise the recycleviews edit: yep
class DRV(RecycleView):

    messages: list
    newestMessageId: str
    reply: dict|None = None

    def setReply(self):
        texture_size = App.get_running_app().channelScreen.ids.reply.texture_size
        # what the fuck
        App.get_running_app().channelScreen.ids.reply.size = texture_size if self.reply else (0, 0)
        if self.reply:
            App.get_running_app().channelScreen.ids.reply.text = "Replying to: " + self.reply['replyAuthor']
        else:
            App.get_running_app().channelScreen.ids.reply.text = ""

    # *args needs to be there cuz it gets called by Clock with random arguments which caused problems
    def getMessages(self, *args):
        _ = args  # so i just void it here :3
        # what is it with these long ahh lines
        self.messages = App.get_running_app().api.getChannelMessages(App.get_running_app().currentChat, 100)
        if not self.messages:
            return None
        if type(self.messages) is not list:
            return None
        self.newestMessageId = self.messages[0]['id']
        self.updateData()
    
    # TODO: refactor for readability
    def updateData(self):
        messages: list = self.messages
        data: list = []

        for message in messages:
            author: str|None = message['author'].get('global_name', None)
            if not author:
                author = message['author'].get('username', 'UNKNOWN_USER_ERROR')  # i hate json
            txt: str = message.get('content', '')
            messageReference: dict = message.get('message_reference', {})
            reply: str = App.get_running_app().api.getReferencedMessage(messageReference, messages)
            messageId: str = message['id']
            image: str = f"https://cdn.discordapp.com/avatars/{message['author']['id']}/{message['author']['avatar']}"
            imageHeight: int = 0
            # placeholder cuz something needs to be there idk edit: why
            # TODO: fix
            attachment: str = ("https://cdn.discordapp.com/attachments/1143229203551096842/1252962153556611173"
                        "/Screenshot_20240619_142408_Pydroid_3.jpg?ex=6674c830&is=667376b0&hm"
                        "=13e97ac0b5ac6391dc957f1a0a96cb04bb7a2dfe1750c4b14559937585f4108f&")
            mentions: list = message.get('mentions', [])
            backgroundColor: list = [0.1, 0.1, 0.1, 0.5]
            for user in mentions:
                if user.get('id', 'ERROR') == App.get_running_app().userId:
                    backgroundColor = [0.3, 0.1, 0.3, 0.5]

            for attachment in message.get('attachments', []):
                if attachment.get('content_type', 'NOTIMAGE').startswith('image'):
                    imageHeight = attachment.get('height', 0)
                    imageWidth = attachment.get('width', None)

                    # this doesnt actually do what its supposed to, image scaling is fucked
                    # TODO: fix
                    if imageWidth:
                        ratio = imageWidth / (self.width * 0.9)
                        imageHeight = imageHeight / ratio

                    attachment = attachment['url']
            data.append({'reply': reply, 'author': author, 'text': txt, 'messageId': messageId, 'imageLink': image,
                         'imageHeight': imageHeight, 'attachmentLink': attachment, 'backgroundColor': backgroundColor})
        self.data = data

    # i love voiding args
    def loadNewMessages(self, *args):
        _ = args
        new_messages: list|None  # "or None" is my saviour edit: its |None lol
        chat = App.get_running_app().currentChat
        if not self.messages:
            new_messages = App.get_running_app().api.getChannelMessages(chat, 10)
        else:
            new_messages = App.get_running_app().api.getChannelMessages(chat, 10, self.newestMessageId)
        if new_messages:
            self.messages = new_messages + self.messages
            self.messages = self.messages[:100]
            self.newestMessageId = self.messages[0]['id']
            self.updateData() # TODO: refactor for readability

    def __init__(self, **kwargs):
        App.get_running_app().drv = self
        super().__init__(**kwargs)  # i dont like super().__init__() idk why


# tried putting this in its own file but it just completely broke lol
class GuildChannelListScreen(Screen):
    def on_pre_enter(self, *args):
        App.get_running_app().gcrv.getChannels()
        super().on_pre_enter(*args)


# you can never have enough recycleviews (i hate them)
class GCRV(RecycleView):

    def getChannels(self): # TODO: refactor for readability
        guildChannels = App.get_running_app().api.getGuildChannels(App.get_running_app().currentGuild)
        guildChannels = [channel for channel in guildChannels if channel['type'] != 2 and channel['type'] != 5]
        data = [{'text': channel['name'], 'channelId': channel['id']} for channel in guildChannels]
        self.data = data

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        App.get_running_app().gcrv = self
        self.getChannels()


class LenCordApp(App):
    sm: ScreenManager = ScreenManager()
    token: str
    api: API
    currentChat: str
    # random placeholder so it doesnt kill itself during startup
    # TODO: fix
    currentGuild: str = "1105880476738130082"  # what server even is this edit: its mine
    userId: str

    # why are all of these functions what did i smoke edit: you drank
    def setChannel(self, channelId: str):
        self.currentChat = channelId
    
    def setGuild(self, guild_id: str):
        self.currentGuild = guild_id
        
    def setScreen(self, screen: str):
        self.sm.current = screen

    def getReady(self):
        self.api = API(self.token)
        self.userId = self.api.getUserId()
        self.sm.add_widget(DirectMessageListScreen(name="dmlist"))
        self.sm.add_widget(ChannelScreen(name='channel'))
        self.sm.add_widget(GuildChannelListScreen(name='guild'))

    def build(self):
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.current = 'login'
        Clock.max_iteration = 100  # idk, images still fuck up the layout lol
        # TODO: fix :(

        return self.sm


if __name__ == "__main__":
    LenCordApp().run()
