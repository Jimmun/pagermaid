""" Message related utilities. """

from os import environ
from random import choice
from emoji import get_emoji_regexp
from googletrans import LANGUAGES
from googletrans import Translator
from os import remove
from gtts import gTTS
from telethon import functions
from dotenv import load_dotenv
from asyncio import create_subprocess_shell as async_run
from asyncio.subprocess import PIPE
from jarvis import command_help, bot, log, log_chatid
from jarvis.events import register

load_dotenv("config.env")
lang = environ.get("APPLICATION_LANGUAGE", "en")


@register(outgoing=True, pattern="^-userid$")
async def userid(context):
    """ Queries the userid of a user. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        message = await context.get_reply_message()
        if message:
            if not message.forward:
                user_id = message.sender.id
                if message.sender.username:
                    target = "@" + message.sender.username
                else:
                    try:
                        target = "**" + message.sender.first_name + "**"
                    except TypeError:
                        target = "**" + "Deleted Account" + "**"

            else:
                user_id = message.forward.sender.id
                if message.forward.sender.username:
                    target = "@" + message.forward.sender.username
                else:
                    target = "*" + message.forward.sender.first_name + "*"
            await context.edit(
                "**Username:** {} \n**UserID:** `{}`"
                    .format(target, user_id)
            )
        else:
            await context.edit("`Unable to get the target message.`")


@register(outgoing=True, pattern="^-chatid$")
async def chatid(context):
    """ Queries the chatid of the chat you are in. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        await context.edit("ChatID: `" + str(context.chat_id) + "`")


@register(outgoing=True, pattern=r"^-log(?: |$)([\s\S]*)")
async def log(context):
    """ Forwards a message into log group """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        if log:
            if context.reply_to_msg_id:
                reply_msg = await context.get_reply_message()
                await reply_msg.forward_to(log_chatid)
            elif context.pattern_match.group(1):
                user = f"Chat ID: {context.chat_id}\n\n"
                text = user + context.pattern_match.group(1)
                await bot.send_message(log_chatid, text)
            else:
                await context.edit("`Unable to get the target message.`")
                return
            await context.edit("Noted.")
        else:
            await context.edit("`Logging is disabled.`")


@register(outgoing=True, pattern="^-leave$")
async def leave(context):
    """ It leaves you from the group. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        await context.edit("Goodbye.")
        try:
            await bot(functions.channels.LeaveChannelRequest(leave.chat_id))
        except AttributeError:
            await context.edit("You are not in a group.")


@register(outgoing=True, pattern=r"^-translate(?: |$)([\s\S]*)")
async def translate(context):
    """ Jarvis universal translator. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        translator = Translator()
        text = await context.get_reply_message()
        message = context.pattern_match.group(1)
        if message:
            pass
        elif text:
            message = text.text
        else:
            await context.edit("`Invalid parameter.`")
            return

        try:
            await context.edit("`Generating translation . . .`")
            reply_text = translator.translate(clear_emojis(message), dest=lang)
        except ValueError:
            await context.edit("`Language not found, please correct the error in the config file.`")
            return

        source_lang = LANGUAGES[f'{reply_text.src.lower()}']
        trans_lang = LANGUAGES[f'{reply_text.dest.lower()}']
        reply_text = f"**Translated** from {source_lang.title()}:\n{reply_text.text}"

        if len(reply_text) > 4096:
            await context.edit("`Output exceeded limit, attaching file.`")
            file = open("output.log", "w+")
            file.write(reply_text)
            file.close()
            await context.client.send_file(
                context.chat_id,
                "output.log",
                reply_to=context.id,
            )
            remove("output.log")
            return
        await context.edit(reply_text)
        if log:
            log_message = f"Translated `{message}` from {source_lang} to {trans_lang}."
            if len(log_message) > 4096:
                await context.edit("`Output exceeded limit, attaching file.`")
                file = open("output.log", "w+")
                file.write(log_message)
                file.close()
                await context.client.send_file(
                    context.chat_id,
                    "output.log",
                    reply_to=context.id,
                )
                remove("output.log")
                return
            await context.client.send_message(
                log_chatid,
                log_message,
            )


@register(outgoing=True, pattern=r"^-tts(?: |$)([\s\S]*)")
async def tts(context):
    """ Send TTS stuff as voice message. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        text = await context.get_reply_message()
        message = context.pattern_match.group(1)
        if message:
            pass
        elif text:
            message = text.text
        else:
            await context.edit("`Invalid argument.`")
            return

        try:
            await context.edit("`Generating vocals . . .`")
            gTTS(message, lang)
        except AssertionError:
            await context.edit("`Invalid argument.`")
            return
        except ValueError:
            await context.edit('`Language not found, please correct the error in the config file.`')
            return
        except RuntimeError:
            await context.edit('`Error loading array of languages.`')
            return
        gtts = gTTS(message, lang)
        gtts.save("vocals.mp3")
        with open("vocals.mp3", "rb") as audio:
            line_list = list(audio)
            line_count = len(line_list)
        if line_count == 1:
            gtts = gTTS(message, lang)
            gtts.save("vocals.mp3")
        with open("vocals.mp3", "r"):
            await context.client.send_file(context.chat_id, "vocals.mp3", voice_note=True)
            remove("vocals.mp3")
            if log:
                await context.client.send_message(
                    log_chatid, "Generated tts for `" + message + "`."
                )
            await context.delete()


@register(outgoing=True, pattern="^-rng(?: |$)(.*)")
async def rng(context):
    """ Automates keyboard spamming. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        try:
            length = context.pattern_match.group(1)
            if length:
                command = "head -c 65536 /dev/urandom | tr -dc A-Za-z0-9 | head -c " + length + " ; echo \'\'"
            else:
                command = "head -c 65536 /dev/urandom | tr -dc A-Za-z0-9 | head -c 64 ; echo \'\'"
            execute = await async_run(
                command,
                stdout=PIPE,
                stderr=PIPE
            )

            stdout, stderr = await execute.communicate()
            result = str(stdout.decode().strip()) \
                + str(stderr.decode().strip())

            await context.edit(result)
        except FileNotFoundError:
            await context.edit("`A util is missing.`")


@register(outgoing=True, pattern=r"^-owo(?: |$)([\s\S]*)")
async def owo(context):
    """ Makes messages become owo. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        if log:
            if context.reply_to_msg_id:
                reply_msg = await context.get_reply_message()
                await context.edit(owoifier(reply_msg.text))
                return
            elif context.pattern_match.group(1):
                text = context.pattern_match.group(1)
                await context.edit(owoifier(text))
            else:
                await context.edit("`Unable to get the target message.`")
                return


@register(outgoing=True, pattern="^-channel$")
async def channel(context):
    """ Returns the author's channel. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        await context.edit("Author Channel: @SparkzStuff")


@register(outgoing=True, pattern="^-source$")
async def source(context):
    """ Prints the git repository URL. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        await context.edit("https://git.stykers.moe/scm/~stykers/jarvis.git")


@register(outgoing=True, pattern="^-site$")
async def site(context):
    """ Outputs the site URL. """
    if not context.text[0].isalpha() and context.text[0] not in ("/", "#", "@", "!"):
        await context.edit("https://jarvis.stykers.moe/")


def clear_emojis(target):
    """ Removes all Emojis from provided string """
    return get_emoji_regexp().sub(u'', target)


def last_replace(s, old, new):
    li = s.rsplit(old, 1)
    return new.join(li)


def owoifier(text):
    """ Converts your text to OwO """
    smileys = [';;w;;', '^w^', '>w<', 'UwU', '(・`ω\´・)', '(´・ω・\`)']

    text = text.replace('L', 'W').replace('l', 'w')
    text = text.replace('R', 'W').replace('r', 'w')

    text = last_replace(text, '!', '! {}'.format(choice(smileys)))
    text = last_replace(text, '?', '? owo')
    text = last_replace(text, '.', '. {}'.format(choice(smileys)))

    for v in ['a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U']:
        if 'n{}'.format(v) in text:
            text = text.replace('n{}'.format(v), 'ny{}'.format(v))
        if 'N{}'.format(v) in text:
            text = text.replace('N{}'.format(v), 'N{}{}'.format('Y' if v.isupper() else 'y', v))

    return text


command_help.update({
    "chatid": "Parameter: -chatid\
    \nUsage: Query the chatid of the chat you are in"
})

command_help.update({
    "userid": "Parameter: -userid\
    \nUsage: Query the userid of the sender of the message you replied to."
})

command_help.update({
    "log": "Parameter: -log\
    \nUsage: Forwards message to logging group."
})

command_help.update({
    "leave": "Parameter: -leave\
    \nUsage: Say goodbye and leave."
})

command_help.update({
    "translate": "Parameter: -translate <text>\
    \nUsage: Translate the target message into English."
})

command_help.update({
    "tts": "Parameter: -tts <text>\
    \nUsage: Generates a voice message."
})

command_help.update({
    "rng": "Parameter: -rng <integer>\
    \nUsage: Automates keyboard spamming."
})

command_help.update({
    "channel": "Parameter: -channel\
    \nUsage: Shows the development channel."
})

command_help.update({
    "source": "Parameter: -source\
    \nUsage: Prints the git repository URL."
})

command_help.update({
    "site": "Parameter: -site\
    \nUsage: Shows the site of Jarvis."
})

command_help.update({
    "owo": "Parameter: -owo <text>\
    \nUsage: Converts messages to OwO."
})
