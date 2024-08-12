import requests
import json


def sort_by_last_message(channels: list) -> list:
    removed: list = [channel for channel in channels if channel['last_message_id'] is None]
    null_removed_channels: list = [channel for channel in channels if channel['last_message_id'] is not None]
    sorted_list: list = sorted(null_removed_channels, key=lambda x: x['last_message_id'], reverse=True)
    sorted_list.extend(removed)
    return sorted_list



# this is not anything official i just named it that 
class API:

    def __init__(self, token: str):
        self.token: str = token

    def get_direct_message_channels(self) -> list:
        channels_url: str = "https://discord.com/api/v10/users/@me/channels"
        headers: dict = {"Authorization": self.token}
        response = requests.get(channels_url, headers=headers)

        direct_message_channels: list = response.json()
        sorted_direct_message_channels: list = sort_by_last_message(direct_message_channels)
        for channel in sorted_direct_message_channels:
            channel['name'] = channel['recipients'][0]['username']  # yeah i need to fix that

        return sorted_direct_message_channels

    def get_channel_messages(self, channel_id: str, amount: int, after: str|None = None) -> list:
        messages_url: str = f"https://discord.com/api/v10/channels/{channel_id}/messages"
        headers: dict = {"Authorization": self.token}
        params: dict = {"limit": amount}
        if after:
            params['after'] = after
        response = requests.get(messages_url, headers=headers, params=params)

        return response.json()

    # we love spaghetti
    @staticmethod  # what does this even do
    def get_referenced_message(message_reference: dict, messages: list) -> str:
        channel_id: str|None = message_reference.get('channel_id', None)
        message_id: str|None = message_reference.get('message_id', None)
        if not channel_id or not message_id:
            return ''
        message: dict|None = None
        for i in messages:
            if i.get('id', '') == message_id:
                message = i
        if not message:
            return "Replies to unloaded message\n"
        author: str|None = message['author'].get('global_name', None)
        if not author:
            author = message['author'].get('username', 'NO_USERNAME_ERROR')
        content: str = message.get('content', '')
        msg_reply: str = content[:20].replace("\n", " ")
        return f"Reply to \"{msg_reply} . . .\" from: {author}\n"

    # i do not like multipart/form >:(
    def send_message(self, channel_id: str, content: str, reply: dict|None = None, attachment: str|None = None):
        channel_url: str = f"https://discord.com/api/v10/channels/{channel_id}/messages"
        headers: dict = {"Authorization": self.token}

        json_payload: dict = {
            'content': content
        }

        if reply:
            json_payload['message_reference'] = {"message_id": reply['reply_id']}

        if attachment:
            file_path: str = attachment
            file_name: str = file_path[-file_path[::-1].find("/"):]
            file_extension: str = file_name[-file_name[::-1].find("."):]
            json_payload['embeds'] = [{'title': 'image', 'thumbnail': {'url': f"attachment://{file_name}"},
                                       'image': {'url': f"attachment://{file_name}"}}]
            json_payload['attachments'] = [{'id': 0, 'filename': file_name}]
            with open(file_path, 'rb') as file:
                file_data: bytes = file.read()

            files = (
                ("payload_json", (None, json.dumps(json_payload), "application/json")),
                ("files[0]", (file_name, file_data, f"image/{file_extension}"))
            )
        else:
            files = {"payload_json": (None, json.dumps(json_payload), "application/json")}

        _ = requests.post(channel_url, files=files, headers=headers) # TODO: refactor

    # nice and simple
    def get_guilds(self) -> list:
        # sleep(2) oops forgot that here but now its staying lol
        guilds_url: str = "https://discord.com/api/v10/users/@me/guilds"
        headers: dict = {"Authorization": self.token}
        params: dict = {"with_count": True}  # why, i never use the counts lol
        return requests.get(guilds_url, headers=headers, params=params).json()
    
    def get_guild(self, guild_id: str) -> dict:
        guild_url: str = f"https://discord.com/api/v10/guilds/{guild_id}"
        headers: dict = {"Authorization": self.token}
        params: dict = {"with_counts": True}
        return requests.get(guild_url, headers=headers, params=params).json()
        
    # TODO: fix order
    def get_guild_channels(self, guild_id: str) -> list:
        guild_channels_url: str = f"https://discord.com/api/v10/guilds/{guild_id}/channels"
        headers: dict = {"Authorization": self.token}
        guild_channels: list = requests.get(guild_channels_url, headers=headers).json()
        return sorted(guild_channels, key=lambda x: x['position'])  # lambda my beloved
    
    def get_user_id(self) -> str:
        headers: dict = {"Authorization": self.token}
        user_url: str = "https://discord.com/api/v10/users/@me"
        response = requests.get(user_url, headers=headers).json()
        return response.get('id', 'ERROR')  # lets hope that never returns 'ERROR' lol

    def get_user(self, user_id: str) -> dict:
        headers: dict = {"Authorization": self.token}
        user_url: str = f"https://discord.com/api/v10/users/{user_id}"
        return requests.get(user_url, headers=headers).json()
    
    # TODO: start dms 
    # TODO: send friend requests 
    # TODO: join guilds 
    # TODO: admin stuff?