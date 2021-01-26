""" Pagermaid plugin base. """
import json, requests, re
from translate import Translator as trans
from urllib.parse import urlparse
from pagermaid import bot, log
from pagermaid.listener import listener, config
from pagermaid.utils import clear_emojis, obtain_message, attach_log
from telethon.tl.types import ChannelParticipantsAdmins
from os import remove

@listener(outgoing=True, command="pixiv",
          description="查询插画信息 （或者回复一条消息）",
          parameters="[<图片链接>] <图片序号>")
async def pixiv(context):
    reply = await context.get_reply_message()
    await context.edit('正在查询中...')
    try:
        if reply:
            try:
                if context.arguments.strip() == '':
                    pixiv_page = 1
                else:
                    try:
                        pixiv_page = int(context.arguments.strip())
                    except:
                        await context.edit('呜呜呜出错了...可能参数不是数字')
                        return True
            except:
                pass
            for num in range(0, len(reply.entities)):
                url = reply.message[reply.entities[num].offset:reply.entities[num].offset + reply.entities[num].length]
                url = urlparse(url)
                try:
                    url = str(re.findall(r"\d+\.?\d*", url.path)[0])
                    pixiv_json = json.loads(requests.get(
                        "https://api.imjad.cn/pixiv/v2/?type=illust&id=" + url).content.decode(
                        "utf-8"))
                except:
                    await context.edit('呜呜呜出错了...可能是链接不上 API 服务器')
                    return True
                try:
                    pixiv_tag = pixiv_json['error']['user_message']
                    await context.edit('没有找到要查询的 pixiv 作品...')
                    return True
                except:
                    if pixiv_page > pixiv_json['illust']['page_count']:
                        await context.edit('呜呜呜出错了...可能是参数指定的页数大于插画页数')
                        return True
                    else:
                        pass
                    pixiv_tag = []
                    pixiv_num = str(pixiv_json['illust']['page_count'])
                    pixiv_list = '[' + pixiv_json['illust']['title'] + '](https://www.pixiv.net/artworks/' + str(
                        pixiv_json['illust']['id']) + ')' + ' (' + str(pixiv_page) + '/' + pixiv_num + ')'
                    for nums in range(0, len(pixiv_json['illust']['tags'])):
                        pixiv_tag.extend(['#' + pixiv_json['illust']['tags'][nums]['name']])
                    try:
                        await context.edit('正在下载图片中 ...')
                        try:
                            r = requests.get('https://daidr.me/imageProxy/?url=' +
                                                    pixiv_json['illust']['meta_single_page']['original_image_url'])
                        except:
                            r = requests.get('https://daidr.me/imageProxy/?url=' +
                                             pixiv_json['illust']['meta_pages'][pixiv_page - 1]['image_urls']['original'])
                        with open("pixiv.jpg", "wb") as code:
                            code.write(r.content)
                        await context.edit('正在上传图片中 ...')
                        await context.client.send_file(context.chat_id, 'pixiv.jpg',
                                                       caption=pixiv_list + '\nTags: ' + ' , '.join(pixiv_tag),
                                                       reply_to=reply.id)
                        await context.delete()
                        remove('pixiv.jpg')
                    except:
                        pass
                    return True
        else:
            try:
                url = urlparse(context.arguments.split()[0])
                if len(context.arguments.split()) == 1:
                    pixiv_page = 1
                else:
                    try:
                        pixiv_page = int(context.arguments.split()[1])
                    except:
                        await context.edit('呜呜呜出错了...可能参数不是数字')
                        return True
            except:
                pass
            try:
                url = str(re.findall(r"\d+\.?\d*", url.path)[0])
                pixiv_json = json.loads(requests.get(
                    "https://api.imjad.cn/pixiv/v2/?type=illust&id=" + url).content.decode(
                    "utf-8"))
            except:
                await context.edit('呜呜呜出错了...可能是链接不上 API 服务器')
            try:
                pixiv_tag = pixiv_json['error']['user_message']
                await context.edit('没有找到要查询的 pixiv 作品...')
                return True
            except:
                if pixiv_page > pixiv_json['illust']['page_count']:
                    await context.edit('呜呜呜出错了...可能是参数指定的页数大于插画页数')
                    return True
                else:
                    pass
                pixiv_tag = []
                pixiv_num = str(pixiv_json['illust']['page_count'])
                pixiv_list = '[' + pixiv_json['illust']['title'] + '](https://www.pixiv.net/artworks/' + str(
                    pixiv_json['illust']['id']) + ')' + ' (' + str(pixiv_page) + '/' + pixiv_num + ')'
                for nums in range(0, len(pixiv_json['illust']['tags'])):
                    pixiv_tag.extend(['#' + pixiv_json['illust']['tags'][nums]['name']])
                try:
                    await context.edit('正在下载图片中 ...')
                    try:
                        r = requests.get('https://daidr.me/imageProxy/?url=' +
                                         pixiv_json['illust']['meta_single_page']['original_image_url'])
                    except:
                        r = requests.get('https://daidr.me/imageProxy/?url=' +
                                         pixiv_json['illust']['meta_pages'][pixiv_page - 1]['image_urls']['original'])
                    with open("pixiv.jpg", "wb") as code:
                        code.write(r.content)
                    await context.edit('正在上传图片中 ...')
                    await context.client.send_file(context.chat_id, 'pixiv.jpg',
                                                   caption=pixiv_list + '\nTags: ' + ' , '.join(pixiv_tag))
                    await context.delete()
                    remove('pixiv.jpg')
                except:
                    pass
                return True
        await context.edit('没有找到要查询的 pixiv 作品 ...')
    except:
        await context.edit('没有找到要查询的 pixiv 作品 ...')