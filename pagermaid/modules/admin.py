""" Pagermaid plugin base. """
import json, requests, re
from translate import Translator as trans
from urllib.parse import urlparse
from pagermaid import bot, log
from pagermaid.listener import listener, config
from pagermaid.utils import clear_emojis, obtain_message, attach_log
from telethon.tl.types import ChannelParticipantsAdmins
from os import remove

@listener(is_plugin=True, outgoing=True, command="admin",
          description="一键 AT 本群管理员（仅在群组中有效）")
async def admin(context):
    await context.edit('正在获取管理员列表中...')
    chat = await context.get_chat()
    try:
        admins = await context.client.get_participants(chat, filter=ChannelParticipantsAdmins)
    except:
        await context.edit('请在群组中使用。')
        return True
    admin_list = []
    for admin in admins:
        if admin.first_name is not None:
            admin_list.extend(['[' + admin.first_name + '](tg://user?id=' + str(admin.id) + ')'])
    await context.edit(' , '.join(admin_list))