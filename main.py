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


class DMRV(RecycleView):

    def get_channels(self):
        dm_channels = App.get_running_app().api.get_direct_message_channels()
        # i love list comprehensions
        data = [{'text': channel['name'], 'channel_id': channel['id']} for channel in dm_channels]
        self.data = data

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.get_channels()


class GRV(RecycleView):

    def get_guilds(self):
        guilds: list = App.get_running_app().api.get_guilds()
        icon_url: str = "https://cdn.discordapp.com/icons/"
        data: list = []
        for guild in guilds:
            name: str = guild['name']
            guild_id: str = guild['id']
            icon: str = f"{icon_url}{guild['id']}/{guild['icon']}"
            data.append({'text': name, 'guild_id': guild_id, 'icon': icon})
        self.data = data

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.get_guilds()


# oh boy
class ChannelScreen(Screen):

    refresh_event: ClockEvent
    attachment: str or None = None

    def file_chooser(self):
        if self.attachment:
            self.ids.attach.text = "Attach image"
            self.attachment = None
        else:
            Factory.FilePicker().open()

    def on_pre_enter(self, *args):
        App.get_running_app().drv.get_messages()
        self.refresh_event = Clock.schedule_interval(App.get_running_app().drv.load_new_messages, 2)
        super().on_pre_enter(*args)

    # i use App.get_running_app() way too much
    def send_message(self):
        message_content: str = self.ids.message_input.text
        if message_content == "" and not self.attachment:
            return None
        self.ids.message_input.text = ""
        reply = App.get_running_app().drv.reply
        attachment = self.attachment
        self.attachment = None
        self.ids.attach.text = "Attach image"
        App.get_running_app().drv.reply = None
        App.get_running_app().drv.set_reply()
        App.get_running_app().api.send_message(App.get_running_app().current_chat, message_content, reply, attachment)

    def on_leave(self, *args):
        self.refresh_event.cancel()
        App.get_running_app().drv.reply = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        App.get_running_app().channel_screen = self


# i should really standardise the recycleviews
class DRV(RecycleView):

    messages: list
    newest_message_id: str
    reply: dict = None

    def set_reply(self):
        texture_size = App.get_running_app().channel_screen.ids.reply.texture_size
        App.get_running_app().channel_screen.ids.reply.size = texture_size if self.reply else (0, 0)
        if self.reply:
            App.get_running_app().channel_screen.ids.reply.text = "Replying to: " + self.reply['reply_author']
        else:
            App.get_running_app().channel_screen.ids.reply.text = ""

    # *args needs to be there cuz it gets called by Clock with random arguments which caused problems
    def get_messages(self, *args):
        _ = args  # so i just void it here :3
        self.messages = App.get_running_app().api.get_channel_messages(App.get_running_app().current_chat, 100)
        if not self.messages:
            return None
        if type(self.messages) is not list:
            return None
        self.newest_message_id = self.messages[0]['id']
        self.update_data()
    
    def update_data(self):
        messages: list = self.messages
        data: list = []

        for message in messages:
            auth: str or None = message['author'].get('global_name', None)
            if not auth:
                auth = message['author'].get('username', 'UNKNOWN_USER_ERROR')
            txt: str = message.get('content', '')
            message_reference: dict = message.get('message_reference', {})
            reply: str = App.get_running_app().api.get_referenced_message(message_reference, messages)
            msg_id: str = message['id']
            img: str = f"https://cdn.discordapp.com/avatars/{message['author']['id']}/{message['author']['avatar']}"
            img_h: int = 0
            # placeholder cuz something needs to be there
            att: str = ("https://cdn.discordapp.com/attachments/1143229203551096842/1252962153556611173"
                        "/Screenshot_20240619_142408_Pydroid_3.jpg?ex=6674c830&is=667376b0&hm"
                        "=13e97ac0b5ac6391dc957f1a0a96cb04bb7a2dfe1750c4b14559937585f4108f&")
            mentions: list = message.get('mentions', [])
            bgcol: list = [0.1, 0.1, 0.1, 0.5]
            for user in mentions:
                if user.get('id', 'ERROR') == App.get_running_app().user_id:
                    bgcol = [0.3, 0.1, 0.3, 0.5]

            for attachment in message.get('attachments', []):
                if attachment.get('content_type', 'NOT_IMAGE').startswith('image'):
                    img_h = attachment.get('height', 0)
                    img_w = attachment.get('width', None)

                    # this doesnt actually do what its supposed to, image scaling is fucked
                    if img_w:
                        ratio = img_w / (self.width * 0.9)
                        img_h = img_h / ratio

                    att = attachment['url']
            data.append({'reply': reply, 'author': auth, 'text': txt, 'message_id': msg_id, 'image_link': img,
                         'image_h': img_h, 'attachment_link': att, 'background_color': bgcol})
        self.data = data

    # i love voiding args
    def load_new_messages(self, *args):
        _ = args
        new_messages: list or None
        chat = App.get_running_app().current_chat
        if not self.messages:
            new_messages = App.get_running_app().api.get_channel_messages(chat, 10)
        else:
            new_messages = App.get_running_app().api.get_channel_messages(chat, 10, self.newest_message_id)
        if new_messages:
            self.messages = new_messages + self.messages
            self.messages = self.messages[:100]
            self.newest_message_id = self.messages[0]['id']
            self.update_data()

    def __init__(self, **kwargs):
        App.get_running_app().drv = self
        super().__init__(**kwargs)


# tried putting this in its own file but it just completely broke lol
class GuildChannelListScreen(Screen):
    def on_pre_enter(self, *args):
        App.get_running_app().gcrv.get_channels()
        super().on_pre_enter(*args)


# you can never have enough recycleviews (i hate them)
class GCRV(RecycleView):

    def get_channels(self):
        guild_channels = App.get_running_app().api.get_guild_channels(App.get_running_app().current_guild)
        guild_channels = [channel for channel in guild_channels if channel['type'] != 2 and channel['type'] != 5]
        data = [{'text': channel['name'], 'channel_id': channel['id']} for channel in guild_channels]
        self.data = data

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        App.get_running_app().gcrv = self
        self.get_channels()


class LenCordApp(App):
    sm: ScreenManager = ScreenManager()
    token: str
    api: API
    current_chat: str
    # random placeholder so it doesnt kill itself during startup
    current_guild: str = "1105880476738130082" 
    user_id: str

    # why are all of these functions what did i smoke
    def set_channel(self, channel_id: str):
        self.current_chat = channel_id
    
    def set_guild(self, guild_id: str):
        self.current_guild = guild_id
        
    def set_screen(self, screen: str):
        self.sm.current = screen

    def get_token(self):
        with open("token", "r") as file:
            self.token = file.read()

    def get_api(self):
        self.api = API(self.token)

    def get_id(self):
        self.user_id = self.api.get_user_id()

    def build(self):
        self.get_token()
        self.get_api()
        self.get_id()
        self.sm.add_widget(DirectMessageListScreen(name="dmlist"))
        self.sm.add_widget(ChannelScreen(name='channel'))
        self.sm.add_widget(GuildChannelListScreen(name='guild'))
        self.sm.current = 'dmlist' # todo: rename that fuckin screen 
        Clock.max_iteration = 100 # idk, images still fuck up the layout lol

        return self.sm


if __name__ == "__main__":
    LenCordApp().run()
