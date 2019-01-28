import re
import slackbot.bot
import subprocess
import slackbot.settings

ARXIV_URL = re.compile(r'https?://arxiv\.org/(?:abs|pdf)/(?P<id>(?:\d{4}\.\d{4,5})|(?:[a-zA-Z.-]+/\d{7}))(?:\.pdf)?')


# @slackbot.bot.listen_to(r'https?://arxiv\.org/(?:abs|pdf)/(?:(?:\d{4}\.\d{4,5})|(?:[a-zA-Z.-]+/\d{7}))(?:\.pdf)?')
@slackbot.bot.listen_to(r'https?://arxiv\.org/(?:pdf)/(?:(?:\d{4}\.\d{4,5})|(?:[a-zA-Z.-]+/\d{7}))(?:\.pdf)?')
def listen_arxiv1(message):
    match = ARXIV_URL.search(message.body['text'])
    if match:
        result, attachments = arxiv_information(match.group('id'))
        in_thread = bool(message.body.get('thread_ts'))
        if result:
            if in_thread:
                message.reply_webapi(result, attachments=attachments, in_thread=True)
            else:
                message.send_webapi(result, attachments=attachments)


ARXIV_ID = re.compile(r'\[(?P<id>(?:\d{4}\.\d{4,5})|(?:[a-zA-Z.-]+/\d{7}))\]')
BARE_ARXIV_ID = re.compile(r'(?P<id>(?:\d{4}\.\d{4,5})|(?:[a-zA-Z.-]+/\d{7}))')
CHANNEL = re.compile(r'#(?P<id>\w+)\|(?P<name>[\w-]+)')
FAILED_CHANNEL = re.compile(r'\s#(?P<name>[\w-]+)')


@slackbot.bot.listen_to(r'\[(?:(?:\d{4}\.\d{4,5})|(?:[a-zA-Z.-]+/\d{7}))\]')
def listen_arxiv2(message):
    match = ARXIV_ID.search(message.body['text'])
    if match:
        result, attachments = arxiv_information(match.group('id'))
        in_thread = bool(message.body.get('thread_ts'))
        if result:
            if in_thread:
                message.reply_webapi(result, attachments=attachments, in_thread=True)
            else:
                message.send_webapi(result, attachments=attachments)


@slackbot.bot.respond_to(r'\Arec .+\d{4}')
def listen_recommendation(message):
    def fail(msg):
        message.reply(msg, in_thread=False)

    id_match = BARE_ARXIV_ID.search(message.body['text'])
    if not id_match:
        fail('arXiv id not recognized.')
        return
    result, attachments = arxiv_information(id_match.group('id'))
    if not result:
        fail('arXiv article not found.')
        return

    sender = message.body.get('user')
    sender_line = ('<@{}>'.format(sender) if sender else 'Someone') + ' recommends:\n'

    channel_match = CHANNEL.search(message.body['text'])
    failed_channel_match = FAILED_CHANNEL.search(message.body['text'])
    if channel_match:
        channel_id, channel_name = channel_match.group('id'), channel_match.group('name')
    elif failed_channel_match:
        fail('no channel #{} or not allowed to post there.'.format(failed_channel_match.group('name')))
        return
    else:
        try:
            channel_name = slackbot.settings.raw_config.get('arxivot', 'rec_default_ch')
            channel_id = [(k, v) for k, v in message._client.channels.items() if v.get('name') == channel_name][0][0]
        except:   # configparser.NoSectionError or NameError
            channel_id = channel_name = ''

    channel = message._client.channels.get(channel_id)
    if not channel:
        fail('channel "{}" not found'.format(channel_name) if channel_name else 'channel not specified.')
        return
    if not channel['is_member']:
        fail('arXivot not allowed to post #{}.'.format(channel_name))
        return

    message._client.send_message(
        channel_id,
        sender_line + result,
        attachments=attachments)
    fail('ok.')


UNITS = re.compile(r'^(.+) in (.+)$')


@slackbot.bot.respond_to(r'^.+ in .+$')
def listen_units(message):
    match = UNITS.search(message.body['text'])
    if match:
        result = natural_units(match.group(1), match.group(2))
        if result:
            message.reply(result, in_thread=True)


def arxiv_information(arxiv_id):
    cmd = ['heprefs', 'short_info', '-s', arxiv_id]
    try:
        p = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode().strip().split('\n')
    except:
        return None, None
    authors = p[0]
    title = p[1] if len(p) >= 1 else ''
    url = p[2] if len(p) >= 2 else ''
    attachments = None if not url else [{'text': url}]
    return f'> [{arxiv_id}] *{authors[0:100]}*\n> {title[0:100]}\n>'.strip(), attachments


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


@slackbot.bot.respond_to(r'^help$')
def listen_help(message):
    message.reply("""*I accept these commands:*
`X in Y` to do natural-unit conversion
`rec X` to recommend an arXiv article

`help` to show this help
`morehelp` to give more help
""")


@slackbot.bot.respond_to(r'^morehelp$')
def listen_morehelp(message):
    message.reply("""
*in*: natural-unit conversion    
`100GeV in fm`
`1pc in m`

*rec*: arXiv article recommendation
`rec 1901.00001 #fun`
`rec 1901.00001`
but be careful because you cannot remove the recommendation message!
If channel name is not specified, recommendation is send to default channel.
""")


@slackbot.bot.default_reply()
def default_func(message):
    text = message.body['text']     # メッセージを取り出す
    # 送信メッセージを作る。改行やトリプルバッククォートで囲む表現も可能
    msg = 'You have sent the following message; try sending "help" for instruction.\n```' + text + '```'
    message.reply(msg)      # メンション
