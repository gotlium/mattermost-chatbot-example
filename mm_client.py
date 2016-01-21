import json
import time

import requests
import websocket


class MattermostApi(object):
    def __init__(self, url):
        self.url = url
        self.token = ""

    def _do_request(self, foo, url, *args, **kwargs):
        kwargs.update({'headers': {"Authorization": "Bearer " + self.token}})
        return json.loads(foo(self.url + url, *args, **kwargs).text)

    def get(self, url):
        return self._do_request(requests.get, url)

    def post(self, url, data=None):
        return self._do_request(requests.post, url, data=json.dumps(data))

    def login(self, name, email, password):
        props = {'name': name, 'email': email, 'password': password}
        p = requests.post(self.url + '/users/login', data=json.dumps(props))
        self.token = p.headers["Token"]
        return json.loads(p.text)

    def create_post(self, uid, cid, msg, files=None, state='loading'):
        created_at = int(time.time() * 1000)
        return self.post('/channels/%s/create' % cid, {
            'user_id': uid,
            'channel_id': cid,
            'message': msg,
            'create_at': created_at,
            'filenames': files or [],
            'pending_post_id': '%s:%d' % (uid, created_at),
            'state': state,
        })


class MattermostClient(object):
    def __init__(self, url):
        self.api = MattermostApi(url)
        self.websocket = None
        self.user = None

    def login(self, team, email, password):
        self.user = self.api.login(team, email, password)

    def send_message(self, c_id, message):
        self.api.create_post(self.user["id"], c_id, message)

    def ws_connect(self):
        host = self.api.url.replace('http', 'ws').replace('https', 'wss')
        url = host + '/websocket?session_token_index=0&1'
        self.websocket = websocket.create_connection(
            url, header=[
                "Cookie: MMTOKEN=%s" % self.api.token,
            ])

    def recv_messages(self, ignore_own_msg=True):
        self.ws_connect()
        while True:
            data = self.websocket.recv()
            try:
                post = json.loads(data)
                if ignore_own_msg is True and post.get("user_id"):
                    if self.user["id"] == post.get("user_id"):
                        continue
                if post.get('props', {}).get('post'):
                    post['props']['post'] = json.loads(
                        post['props']['post'])
                yield post
            except ValueError:
                continue
