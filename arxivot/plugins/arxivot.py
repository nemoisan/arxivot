import re
import slackbot.bot
import subprocess


ARXIV_URL = re.compile(r'https?://arxiv\.org/(?:abs|pdf)/(?P<id>(?:\d{4}\.\d{4,5})|(?:[a-zA-Z.-]+/\d{7}))(?:\.pdf)?')
ARXIV_ID = re.compile(r'\[(?P<id>(?:\d{4}\.\d{4,5})|(?:[a-zA-Z.-]+/\d{7}))\]')


@slackbot.bot.listen_to(r'https?://arxiv\.org/(?:abs|pdf)/(?:(?:\d{4}\.\d{4,5})|(?:[a-zA-Z.-]+/\d{7}))(?:\.pdf)?')
def listen_string(message):
    match = ARXIV_URL.search(message.body['text'])
    if match:
        message.send(arxiv_information(match.group('id')))

@slackbot.bot.listen_to(r'\[(?:(?:\d{4}\.\d{4,5})|(?:[a-zA-Z.-]+/\d{7}))\]')
def listen_string(message):
    match = ARXIV_ID.search(message.body['text'])
    if match:
        message.send(arxiv_information(match.group('id'), with_link=True))


def arxiv_information(arxiv_id, with_link=False):
    cmd = ['heprefs', 'short_info', '-s', arxiv_id]
    p = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode().strip().split('\n')
    authors = p[0]
    title = p[1] if len(p) >= 1 else ''
    url = p[2] if len(p) >= 2 and with_link else ''

    return f'> [{arxiv_id}] *{authors[0:100]}*\n> {title[0:100]}\n> {url}'.strip()


@slackbot.bot.default_reply()
def default_func(message):
    text = message.body['text']     # メッセージを取り出す
    # 送信メッセージを作る。改行やトリプルバッククォートで囲む表現も可能
    msg = 'あなたの送ったメッセージは\n```' + text + '```'
    message.reply(msg)      # メンション
