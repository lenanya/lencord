# lencord
A custom Discord Client written in Python using the kivy library for UI (VERY wip)

To run:
- install python 3.12
- install kivy, requests (pip install kivy, requests)
- insert your discord token in the file named 'token' (ik ik sus but its open source you can read all the code)
- run main.py

## Working
- image attachments (sort of, a bit laggy) (minus gifs)
- uploading images via filepicker (minus gifs)
- sending messages
- replying
- messages that mention you are highlighted
- server channels, aswell as existing dms

## Not Working
- logging in with email and password (only token right now)
- gifs
- user profiles
- role colors
- permissions
- files other than images (both uploading them and seeing them)
- voice chat (probably never will)
- updating messages dynamically (loads most recent 100 and then updates every 2 seconds, keeping 100 messages loaded)
- link embeds
- images arent scaled correctly yet
- emoji
- mentions
- adding friends, removing friends
- updating your profile
- settings
- starting dms
- joining servers
- creating servers
- leaving servers
- server info in general
