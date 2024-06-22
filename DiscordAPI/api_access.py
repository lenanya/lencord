import requests
import json


def sort_by_last_message(channels: list) -> list:
    removed: list = [channel for channel in channels if channel['last_message_id'] is None]
    null_removed_channels: list = [channel for channel in channels if channel['last_message_id'] is not None]
    sorted_list: list = sorted(null_removed_channels, key=lambda x: x['last_message_id'], reverse=True)
    sorted_list.extend(removed)
    return sorted_list


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
            channel['name'] = channel['recipients'][0]['username']

        return sorted_direct_message_channels

    def get_channel_messages(self, channel_id: str, amount: int, after: str or None = None) -> list:
        messages_url: str = f"https://discord.com/api/v10/channels/{channel_id}/messages"
        headers: dict = {"Authorization": self.token}
        params: dict = {"limit": amount}
        if after:
            params['after'] = after
        response = requests.get(messages_url, headers=headers, params=params)

        return response.json()

    @staticmethod
    def get_referenced_message(message_reference: dict, messages: list) -> str:
        channel_id: str or None = message_reference.get('channel_id', None)
        message_id: str or None = message_reference.get('message_id', None)
        if not channel_id or not message_id:
            return ''
        message: dict or None = None
        for i in messages:
            if i.get('id', '') == message_id:
                message = i
        if not message:
            return "Replies to unloaded message\n"
        author: str or None = message['author'].get('global_name', None)
        if not author:
            author = message['author'].get('username', 'NO_USERNAME_ERROR')
        content: str = message.get('content', '')
        return f"Reply to \"{content[:20].replace("\n", " ")} . . .\" from: {author}\n"

    def send_message(self, channel_id: str, content: str, reply: dict or None = None, attachment: str or None = None):
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

        _ = requests.post(channel_url, files=files, headers=headers)

    def get_guilds(self) -> list:
        # sleep(2)
        guilds_url: str = "https://discord.com/api/v10/users/@me/guilds"
        headers: dict = {"Authorization": self.token}
        params: dict = {"with_count": True}
        return requests.get(guilds_url, headers=headers, params=params).json()

    def get_guild_channels(self, guild_id: str) -> list:
        guild_channels_url: str = f"https://discord.com/api/v10/guilds/{guild_id}/channels"
        headers: dict = {"Authorization": self.token}
        guild_channels: list = requests.get(guild_channels_url, headers=headers).json()
        return sorted(guild_channels, key=lambda x: x['position'])

    def get_user_id(self) -> str:
        headers: dict = {"Authorization": self.token}
        user_url: str = "https://discord.com/api/v10/users/@me"
        response = requests.get(user_url, headers=headers).json()
        return response.get('id', 'ERROR')
