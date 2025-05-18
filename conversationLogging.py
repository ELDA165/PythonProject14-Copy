import json
from otree.api import *
from constant import *
from datetime import datetime

"""Requirement player has a the fields msg and ChatLog"""


class Log():

    def startLog(player):
        player.msg = json.dumps([{"role": "system", "content": "-Starting"}])

    def log(player, message, bot):
        messages = json.loads(player.msg)
        if bot:
            msg = {'role': 'bot', 'content': message}
        else:
            msg = {'role': player.getId(), 'content': message}
        messages.append(msg)
        player.msg = json.dumps(messages)

    # custom export of chatLog
    def custom_export(players):
        # header row
        yield ['session_code', 'participant_code', 'sender', 'text', 'timestamp']
        for p in players:
            participant = p.participant
            session = p.session

            # expand chatLog
            log = p.field_maybe_none('chatLog')
            if log:
                json_log = json.loads(log)
                for r in json_log:
                    sndr = r['sender']
                    txt = r['text']
                    time = r['timestamp']
                    yield [session.code, participant.code, sndr, txt, time]