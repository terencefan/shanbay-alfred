#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "stdrickforce"  # Tengyuan Fan
# Email: <stdrickforce@gmail.com> <tfan@xingin.com>

import argparse
import json
import os
import sys
import time

from workflow import Workflow as WorkflowBase
from workflow import web
from workflow.notify import notify

TOKEN_FILE = os.path.abspath('access_token')


class Workflow(WorkflowBase):

    def push(self, title, subtitle, query=''):
        self.add_item(
            title=title,
            subtitle=subtitle,
            arg=query,
            valid=True,
            icon='shanbay_favicon.png',
        )


class Shanbay(object):

    HOST = 'https://api.shanbay.com/bdc/'

    def __init__(self, wf):
        self.wf = wf

    @property
    def access_token(self):
        if not os.path.isfile(TOKEN_FILE):
            return ''
        with open(TOKEN_FILE) as f:
            data = json.loads(f.read().strip())
        if time.time() < data['expire_at']:
            return data['access_token']
        return ''

    def get(self, action, params):
        url = self.HOST + action + '/'
        return web.get(url, params=params).json()

    def post(self, action, params={}, data={}):
        url = self.HOST + action + '/'
        return web.post(url, params=params, data=data).json()

    def query(self, word):
        try:
            res = self.get('search', {'word': word})
            wf.push(
                res['data']['definition'],
                "us: [%s], uk: [%s]" % (
                    res['data']['pronunciations']['us'],
                    res['data']['pronunciations']['uk'],
                ),
                str(res['data']['id']),
            )
            return res['data']['id']
        except:
            wf.push(
                'Ops! The word not exists!',
                'please check your spelling mistakes.',
            )

    def add(self, wid):
        if not self.access_token:
            notify(
                u'您必须填写授权码才能添加单词进词库',
                u'请访问github主页了解详情',
            )
            return
        self.post('learning', {
            'access_token': self.access_token,
        }, {
            'id': wid,
        })

    def query_example(self, wid):
        try:
            res = self.get('example', {
                'vocabulary_id': wid,
                'access_token': self.access_token,
            })
            for example in res['data']:
                title = example['annotation']
                title = title.replace('<vocab>', '[')
                title = title.replace('</vocab>', ']')
                wf.push(title, example['translation'])
        except Exception as e:  # noqa
            pass

    def auth(self, token):
        with open(TOKEN_FILE, 'w') as f:
            f.write(json.dumps({
                'access_token': token,
                'expire_at': int(time.time()) + 24 * 30 * 60 * 60,
            }))
        notify(u'授权成功', u'您已成功授权，有效期为30天')


def main(wf):

    parser = argparse.ArgumentParser()
    parser.add_argument('command')
    parser.add_argument('query')
    args = parser.parse_args(wf.args)

    c = Shanbay(wf)
    if args.command == 'query':
        wid = c.query(args.query)
        c.query_example(wid)
    elif args.command == 'add':
        c.add(args.query)
    elif args.command == 'auth':
        c.auth(args.query)

    # Send the results to Alfred as XML
    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
