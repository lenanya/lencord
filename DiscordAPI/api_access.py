import requests
import json


def sortByLastMessage(channels: list) -> list:
    removed: list = [channel for channel in channels if channel.get['last_message_id'] is None]
    nullRemovedChannels: list = [channel for channel in channels if channel.get['last_message_id'] is not None]
    
    sortedList: list = sorted(nullRemovedChannels, key=lambda x: int(x.get['last_message_id']), reverse=True)
    sortedList.extend(removed)
    
    return sortedList

def globalNameOrUsername(user: dict) -> str:
    name: str
    globalName: str|None = user.get("global_name", None)
    
    if not globalName:
        name = user.get("username", "ERRORGETTINGUSERNAME") # TODO: add error handling
    else:
        name = globalName
    
    return name

def getDirectMessageChannelName(recipients: list) -> str:
    name: str
    
    if len(recipients) < 2:
        name = globalNameOrUsername(recipients[0])
    else:
        names: list = [globalNameOrUsername(user) for user in recipients]
        name = ", ".join(names)
    
    return name


# this is not anything official i just named it that 
class API:

    def __init__(self, token: str):
        self.token: str = token

    def getDirectMessageChannels(self) -> list:
        channelsURL: str = "https://discord.com/api/v10/users/@me/channels"
        headers: dict = {"Authorization": self.token}
        response = requests.get(channelsURL, headers=headers)

        directMessageChannels: list = response.json()
        sortedDirectMessageChannels: list = sortByLastMessage(directMessageChannels)
        
        for channel in sortedDirectMessageChannels:
            channel['name'] = getDirectMessageChannelName(channel['recipients'])

        return sortedDirectMessageChannels

    def getChannelMessages(self, channelId: str, amount: int, after: str|None = None) -> list:
        messages_url: str = f"https://discord.com/api/v10/channels/{channelId}/messages"
        headers: dict = {"Authorization": self.token}
        params: dict = {"limit": amount}
        
        if after:
            params['after'] = after
            
        response = requests.get(messages_url, headers=headers, params=params)

        return response.json()

    @staticmethod 
    def getReferencedMessage(messageReference: dict, referencedMessage: dict) -> str:
        channelId: str|None = messageReference.get('channel_id', None)
        messageId: str|None = messageReference.get('message_id', None)
        
        if not channelId or not messageId:
            return ''
        
        message: dict = referencedMessage
        author: str = globalNameOrUsername(message['author'])
        content: str = message.get('content', '')
        
        messageReply: str = content[:20].replace("\n", " ")
        return f"Reply to \"{messageReply} . . .\" from: {author}\n"

    # i do not like multipart/form >:(
    def sendMessage(self, channelId: str, content: str, reply: dict|None = None, attachment: str|None = None):
        channelURL: str = f"https://discord.com/api/v10/channels/{channelId}/messages"
        headers: dict = {"Authorization": self.token}
        jsonPayload: dict = {'content': content}

        if reply:
            jsonPayload['message_reference'] = {"message_id": reply.get('reply_id')}

        if attachment:
            filePath: str = attachment
            fileName: str = filePath[-filePath[::-1].find("/"):]
            fileExtension: str = fileName[-fileName[::-1].find("."):]
            
            jsonPayload['embeds'] = [{'title': 'image', 'thumbnail': {'url': f"attachment://{fileName}"},
                                       'image': {'url': f"attachment://{fileName}"}}]
            jsonPayload['attachments'] = [{'id': 0, 'filename': fileName}]
            
            with open(filePath, 'rb') as file:
                fileData: bytes = file.read()

            files = (
                ("payload_json", (None, json.dumps(jsonPayload), "application/json")),
                ("files[0]", (fileName, fileData, f"image/{fileExtension}"))
            )
        else:
            files = {"payload_json": (None, json.dumps(jsonPayload), "application/json")}

        _ = requests.post(channelURL, files=files, headers=headers)

    def getGuilds(self) -> list:
        guildsURL: str = "https://discord.com/api/v10/users/@me/guilds"
        headers: dict = {"Authorization": self.token}
        params: dict = {"with_count": True}
        
        return requests.get(guildsURL, headers=headers, params=params).json()
    
    def getGuild(self, guildId: str) -> dict:
        guildURL: str = f"https://discord.com/api/v10/guilds/{guildId}"
        headers: dict = {"Authorization": self.token}
        params: dict = {"with_counts": True}
        
        return requests.get(guildURL, headers=headers, params=params).json()
        
    # TODO: fix order
    def getGuildChannels(self, guildId: str) -> list:
        guildChannelsURL: str = f"https://discord.com/api/v10/guilds/{guildId}/channels"
        headers: dict = {"Authorization": self.token}
        
        guildChannels: list = requests.get(guildChannelsURL, headers=headers).json()
        
        return sorted(guildChannels, key=lambda x: x['position'])  # lambda my beloved
    
    def getUserId(self) -> str:
        headers: dict = {"Authorization": self.token}
        userURL: str = "https://discord.com/api/v10/users/@me"
        
        response = requests.get(userURL, headers=headers).json()
        
        return response.get('id', 'ERROR')  # lets hope that never returns 'ERROR' lol
        # TODO: handle errors bruh

    def getUser(self, userId: str) -> dict:
        headers: dict = {"Authorization": self.token}
        userURL: str = f"https://discord.com/api/v10/users/{userId}"
        
        return requests.get(userURL, headers=headers).json()
    
    # TODO: start dms 
    # TODO: send friend requests 
    # TODO: join guilds 
    # TODO: admin stuff?