from DiscordAPI.api_access import API, globalNameOrUsername
import requests
import sys

from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.recycleview import RecycleView
from kivy.clock import Clock, ClockEvent
from kivy.factory import Factory

from Widgets.message import Message
from Widgets.guildchannel import GuildChannel
from Widgets.guild import Guild
from Widgets.directmessagechannel import DirectMessageChannel

# set shortcuts for annoying to type functions
gRA = App.get_running_app


# yes this needs to be here
class DirectMessageListScreen(Screen):
    pass


# this too
class LoginScreen(Screen):
    pass


class DMRV(RecycleView):

    def getChannels(self):
        dmChannels = gRA().api.getDirectMessageChannels()
        # i love list comprehensions
        data = [{'text': channel.get('name'), 'channelId': channel.get('id')} for channel in dmChannels]
        
        self.data = data

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.getChannels()


class GRV(RecycleView):

    def getGuilds(self):
        guilds: list = gRA().api.getGuilds()
        iconURL: str = "https://cdn.discordapp.com/icons/"
        data: list = []
        
        for guild in guilds:
            name: str = guild.get('name')
            guildId: str = guild.get('id')
            guildIcon: str = guild.get('icon')
            icon: str = f"{iconURL}{guildId}/{guildIcon}"
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
        gRA().drv.getMessages()
        self.refreshEvent = Clock.schedule_interval(gRA().drv.loadNewMessages, 2)
        super().on_pre_enter(*args)
        
    def sendMessage(self):
        messageContent: str = self.ids.messageInput.text
        
        if messageContent == "" and not self.attachment:
            return None
        
        self.ids.messageInput.text = ""
        attachment = self.attachment
        self.attachment = None
        self.ids.attach.text = "Attach image"
        
        reply = gRA().drv.reply
        gRA().drv.reply = None
        gRA().drv.setReply()
        gRA().api.sendMessage(gRA().currentChat, messageContent, reply, attachment)

    def on_leave(self, *args):
        self.refreshEvent.cancel()
        gRA().drv.reply = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        gRA().channelScreen = self


# i should really standardise the recycleviews edit: yep
class DRV(RecycleView):

    messages: list
    newestMessageId: str
    reply: dict|None = None

    def setReply(self):
        textureSize = gRA().channelScreen.ids.reply.texture_size
        gRA().channelScreen.ids.reply.size = textureSize if self.reply else (0, 0)
        
        if self.reply:
            gRA().channelScreen.ids.reply.text = "Replying to: " + self.reply.get('replyAuthor')
        else:
            gRA().channelScreen.ids.reply.text = ""

    def getMessages(self, *args):
        _ = args
        self.messages = gRA().api.getChannelMessages(gRA().currentChat, 100)
        
        if not self.messages:
            return None
        if type(self.messages) is not list:
            return None
        
        self.newestMessageId = self.messages[0].get('id')
        self.updateData()
    
    @staticmethod # not used but maybe for future 
    def imageOrGIFReplace(url: str) -> str:
        contentType: str = requests.get(url).headers.get('Content-Type')
        if contentType.endswith("gif"):
            return "http://celestynya.com/images/gifNotLoaded.png"
        return url
    
    def updateData(self):
        messages: list = self.messages
        data: list = []
        avatarBaseLink: str = "https://cdn.discordapp.com/avatars"

        for message in messages:
            author: dict = message.get('author')
            authorName: str = globalNameOrUsername(author)
            authorID: str = author.get('id')
            authorAvatar: str = author.get('avatar')
            # maybe later
            # authorAvatarLink: str = self.imageOrGIFReplace(f"{avatarBaseLink}/{authorID}/{authorAvatar}")
            authorAvatarLink: str = f"{avatarBaseLink}/{authorID}/{authorAvatar}"
            
            content: str = message.get('content', '')
            messageId: str = message.get('id')
            messageReference: dict = message.get('message_reference', {})
            referencedMessage: dict = message.get('referenced_message', {})
            reply: str = gRA().api.getReferencedMessage(messageReference, referencedMessage)
            
            mentions: list = message.get('mentions', [])
            attachmentLink: str = ("http://celestynya.com/images/gifNotLoaded.png")
            
            imageHeight: int = 0
            backgroundColor: list = [0.1, 0.1, 0.1, 0.5]
            
            for user in mentions:
                if user.get('id', 'ERROR') == gRA().userId:
                    backgroundColor = [0.3, 0.1, 0.3, 0.5]
                    break

            for attachment in message.get('attachments', []):
                if attachment.get('content_type', 'NOTIMAGE').startswith('image'):
                    imageHeight = attachment.get('height', 0)
                    imageWidth = attachment.get('width', None)

                    # this doesnt actually do what its supposed to, image scaling is fucked
                    # TODO: fix
                    if imageWidth:
                        ratio = imageWidth / (self.width * 0.9)
                        imageHeight = imageHeight / ratio

                    # attachmentLink = self.imageOrGIFReplace(attachment.get('url'))
                    attachmentLink = attachment.get('url')
                    
            data.append({'reply': reply, 'author': authorName, 
                         'text': content, 'messageId': messageId, 
                         'authorAvatar': authorAvatarLink,
                         'imageHeight': imageHeight, 
                         'attachmentLink': attachmentLink, 
                         'backgroundColor': backgroundColor})
        self.data = data

    def loadNewMessages(self, *args):
        _ = args
        newMessages: list|None
        chat = gRA().currentChat
        
        if not self.messages:
            newMessages = gRA().api.getChannelMessages(chat, 10)
        else:
            newMessages = gRA().api.getChannelMessages(chat, 10, self.newestMessageId)
        if newMessages:
            self.messages = (newMessages + self.messages)[:100]
            self.newestMessageId = self.messages[0].get('id', None)
            
            self.updateData()

    def __init__(self, **kwargs):
        gRA().drv = self
        super().__init__(**kwargs)


# tried putting this in its own file but it just completely broke lol
class GuildChannelListScreen(Screen):
    def on_pre_enter(self, *args):
        gRA().gcrv.getChannels()
        super().on_pre_enter(*args)


# you can never have enough recycleviews (i hate them)
class GCRV(RecycleView):

    def getChannels(self):
        guildChannels = gRA().api.getGuildChannels(gRA().currentGuild)
        guildChannels = [
            channel for channel in guildChannels if channel.get('type') != 2 and channel.get('type') != 5
            ]
        data = [{'text': channel.get('name'), 'channelId': channel.get('id')} for channel in guildChannels]
        
        self.data = data

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        gRA().gcrv = self


class LenCordApp(App):
    sm: ScreenManager = ScreenManager()
    token: str
    api: API
    currentChat: str
    currentGuild: str = ""
    userId: str

    def setChannel(self, channelId: str):
        self.currentChat = channelId
    
    def get_token_from_file(self):
        with open("token.txt", "r") as f:
                self.token = f.read().strip("\n")
                f.close()
                print(self.token)
    
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
        if "debug" in sys.argv:
            with open("token.txt", "r") as f:
                self.token = f.read().strip("\n")
            f.close()
            self.getReady()
            self.sm.current = 'dmlist'
        else:
            self.sm.add_widget(LoginScreen(name='login'))
            self.sm.current = 'login'

        Clock.max_iteration = 100  # idk, images still fuck up the layout lol
        # TODO: fix :(

        return self.sm


if __name__ == "__main__":
    LenCordApp().run()
