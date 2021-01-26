""" Pagermaid plugin base. """
import json, requests, re
from translate import Translator as trans
from urllib.parse import urlparse
from pagermaid import bot, log
from pagermaid.listener import listener, config
from pagermaid.utils import clear_emojis, obtain_message, attach_log
from telethon.tl.types import ChannelParticipantsAdmins
from os import remove

@listener(is_plugin=True, outgoing=True, command="ip",
          description="IPINFO （或者回复一句话）",
          parameters="<ip/域名>")
async def ipinfo(context):
    reply = await context.get_reply_message()
    await context.edit('正在查询中...')
    try:
        if reply:
            for num in range(0, len(reply.entities)):
                url = reply.message[reply.entities[num].offset:reply.entities[num].offset + reply.entities[num].length]
                url = urlparse(url)
                if url.hostname:
                    url = url.hostname
                else:
                    url = url.path
                ipinfo_json = json.loads(requests.get(
                    "http://ip-api.com/json/" + url + "?fields=status,message,country,regionName,city,lat,lon,isp,org,as,mobile,proxy,hosting,query").content.decode(
                    "utf-8"))
                if ipinfo_json['status'] == 'fail':
                    pass
                elif ipinfo_json['status'] == 'success':
                    ipinfo_list = []
                    ipinfo_list.extend(["查询目标： `" + url + "`"])
                    if ipinfo_json['query'] == url:
                        pass
                    else:
                        ipinfo_list.extend(["解析地址： `" + ipinfo_json['query'] + "`"])
                    ipinfo_list.extend(["地区： `" + ipinfo_json['country'] + ' - ' + ipinfo_json['regionName'] + ' - ' +
                                        ipinfo_json['city'] + "`"])
                    ipinfo_list.extend(["经纬度： `" + str(ipinfo_json['lat']) + ',' + str(ipinfo_json['lon']) + "`"])
                    ipinfo_list.extend(["ISP： `" + ipinfo_json['isp'] + "`"])
                    if not ipinfo_json['org'] == '':
                        ipinfo_list.extend(["组织： `" + ipinfo_json['org'] + "`"])
                    try:
                        ipinfo_list.extend(
                            ['[' + ipinfo_json['as'] + '](https://bgp.he.net/' + ipinfo_json['as'].split()[0] + ')'])
                    except:
                        pass
                    if ipinfo_json['mobile']:
                        ipinfo_list.extend(['此 IP 可能为**蜂窝移动数据 IP**'])
                    if ipinfo_json['proxy']:
                        ipinfo_list.extend(['此 IP 可能为**代理 IP**'])
                    if ipinfo_json['hosting']:
                        ipinfo_list.extend(['此 IP 可能为**数据中心 IP**'])
                    await context.edit('\n'.join(ipinfo_list))
                    return True
        else:
            url = urlparse(context.arguments)
            if url.hostname:
                url = url.hostname
            else:
                url = url.path
            ipinfo_json = json.loads(requests.get(
                "http://ip-api.com/json/" + url + "?fields=status,message,country,regionName,city,lat,lon,isp,org,as,mobile,proxy,hosting,query").content.decode(
                "utf-8"))
            if ipinfo_json['status'] == 'fail':
                pass
            elif ipinfo_json['status'] == 'success':
                ipinfo_list = []
                if url == '':
                    ipinfo_list.extend(["查询目标： `本机地址`"])
                else:
                    ipinfo_list.extend(["查询目标： `" + url + "`"])
                if ipinfo_json['query'] == url:
                    pass
                else:
                    ipinfo_list.extend(["解析地址： `" + ipinfo_json['query'] + "`"])
                ipinfo_list.extend(["地区： `" + ipinfo_json['country'] + ' - ' + ipinfo_json['regionName'] + ' - ' +
                                    ipinfo_json['city'] + "`"])
                ipinfo_list.extend(["经纬度： `" + str(ipinfo_json['lat']) + ',' + str(ipinfo_json['lon']) + "`"])
                ipinfo_list.extend(["ISP： `" + ipinfo_json['isp'] + "`"])
                if not ipinfo_json['org'] == '':
                    ipinfo_list.extend(["组织： `" + ipinfo_json['org'] + "`"])
                try:
                    ipinfo_list.extend(
                        ['[' + ipinfo_json['as'] + '](https://bgp.he.net/' + ipinfo_json['as'].split()[0] + ')'])
                except:
                    pass
                if ipinfo_json['mobile']:
                    ipinfo_list.extend(['此 IP 可能为**蜂窝移动数据 IP**'])
                if ipinfo_json['proxy']:
                    ipinfo_list.extend(['此 IP 可能为**代理 IP**'])
                if ipinfo_json['hosting']:
                    ipinfo_list.extend(['此 IP 可能为**数据中心 IP**'])
                await context.edit('\n'.join(ipinfo_list))
                return True
        await context.edit('没有找到要查询的 ip/域名 ...')
    except:
        await context.edit('没有找到要查询的 ip/域名 ...')