import re
import slackbot.bot
import subprocess


ARXIV_URL = re.compile(r'https?://arxiv\.org/(?:abs|pdf)/(?P<id>(?:\d{4}\.\d{4,5})|(?:[a-zA-Z.-]+/\d{7}))(?:\.pdf)?')


@slackbot.bot.listen_to(r'https?://arxiv\.org/(?:abs|pdf)/(?:(?:\d{4}\.\d{4,5})|(?:[a-zA-Z.-]+/\d{7}))(?:\.pdf)?')
def listen_arxiv1(message):
    match = ARXIV_URL.search(message.body['text'])
    if match:
        result = arxiv_information(match.group('id'))
        in_thread = bool(message.body.get('thread_ts'))
        if result:
            if in_thread:
                message.reply(result, in_thread=True)
            else:
                message.send(result)


ARXIV_ID = re.compile(r'\[(?P<id>(?:\d{4}\.\d{4,5})|(?:[a-zA-Z.-]+/\d{7}))\]')


@slackbot.bot.listen_to(r'\[(?:(?:\d{4}\.\d{4,5})|(?:[a-zA-Z.-]+/\d{7}))\]')
def listen_arxiv2(message):
    match = ARXIV_ID.search(message.body['text'])
    if match:
        result = arxiv_information(match.group('id'), with_link=True)
        in_thread = bool(message.body.get('thread_ts'))
        if result:
            if in_thread:
                message.reply(result, in_thread=True)
            else:
                message.send(result)


UNITS = re.compile(r'^(.+) in (.+)$')


@slackbot.bot.respond_to(r'^.+ in .+$')
def listen_units(message):
    match = UNITS.search(message.body['text'])
    if match:
        result = natural_units(match.group(1), match.group(2))
        if result:
            message.reply(result, in_thread=True)


def arxiv_information(arxiv_id, with_link=False):
    cmd = ['heprefs', 'short_info', '-s', arxiv_id]
    try:
        p = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode().strip().split('\n')
    except:
        return None
    authors = p[0]
    title = p[1] if len(p) >= 1 else ''
    url = p[2] if len(p) >= 2 and with_link else ''
    return f'> [{arxiv_id}] *{authors[0:100]}*\n> {title[0:100]}\n> {url}'.strip()


def natural_units(convert, to):
    cmd = ['units', '-f', '/home/misho/bots/natural_units/natural.units', '--verbose', '--quiet', convert, to]
    try:
        output, stderr = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()
    except:
        return None
    p = output.decode().strip()
    p = re.sub(r'\s*\n\s*', ';; ', p)
    p = re.sub(r'\s\s+', ' ', p)
    return p


@slackbot.bot.default_reply()
def default_func(message):
    text = message.body['text']     # メッセージを取り出す
    # 送信メッセージを作る。改行やトリプルバッククォートで囲む表現も可能
    msg = 'あなたの送ったメッセージは\n```' + text + '```'
    message.reply(msg)      # メンション
