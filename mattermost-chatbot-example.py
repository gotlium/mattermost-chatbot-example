# -*- encoding: utf-8 -*-

from mm_client import MattermostClient

URL = 'http://mattermost.example.org:8080/api/v1'
LOGIN = 'bot@example.org'
PASSWORD = 'bot-password'
TEAM = 'team-name'


class MattermostBot(object):
    def __init__(self):
        self.mm_cli = MattermostClient(URL)
        self.msg = None

    def get_message(self):
        return self.msg['props']['post']['message']

    def send(self, msg, ch_id=None):
        self.mm_cli.send_message(ch_id or self.msg['channel_id'], msg)

    def command_is(self, *args):
        message = self.get_message()
        if message and message.split().pop(0) in args:
            return True

    def process_message(self):
        if self.command_is('hello', 'hi'):
            self.send("> hi")
        elif self.command_is('ping'):
            self.send("pong")
        else:
            self.send("Error usage")

    def run(self):
        self.mm_cli.login(TEAM, LOGIN, PASSWORD)
        for self.msg in self.mm_cli.recv_messages():
            if self.msg.get('action') == 'posted':
                self.process_message()


if __name__ == '__main__':
    try:
        MattermostBot().run()
    except KeyboardInterrupt:
        pass
