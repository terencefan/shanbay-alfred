#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "stdrickforce"  # Tengyuan Fan
# Email: <stdrickforce@gmail.com> <tfan@xingin.com>

import argparse
import json
import sys
import urllib
import urllib2

from workflow import (
    Workflow as WorkflowBase,
)


class Workflow(WorkflowBase):

    def push(self, title, subtitle):
        self.add_item(
            title=title,
            subtitle=subtitle,
            icon='shanbay_favicon.png',
        )


class Shanbay(object):

    HOST = 'https://api.shanbay.com/bdc/'

    def __init__(self, wf):
        self.wf = wf

    def get(self, action, params):
        url = self.HOST + action + '/?' + urllib.urlencode(params)
        content = urllib2.urlopen(url).read()
        return json.loads(content)

    def query(self, word):
        try:
            res = self.get('search', {'word': word})
            wf.push(
                title=res['data']['definition'],
                subtitle="us: [%s], uk: [%s]" % (
                    res['data']['pronunciations']['us'],
                    res['data']['pronunciations']['uk'],
                ),
            )
            return res['data']['id']
        except:
            wf.push(
                title='Ops! The word not exists!',
                subtitle='please check your spelling mistakes.',
            )

    def query_example(self, wid):
        try:
            res = self.get('example', {'vocabulary_id': wid})
            for example in res['data']:
                wf.add_item(title=example['annotation'])
        except Exception:
            pass


def main(wf):

    parser = argparse.ArgumentParser()
    parser.add_argument('query')
    args = parser.parse_args(wf.args)

    c = Shanbay(wf)
    wid = c.query(args.query)
    c.query_example(wid)

    # Send the results to Alfred as XML
    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
