# -- encoding: UTF-8 --
import argparse
import os
import itertools
import posixpath
import sys
import urllib.parse as up

import requests

slack_token = os.environ['SLACK_TOKEN']
sess = requests.session()


def download_image(image_url):
    u = up.urlparse(image_url)
    dest_name = os.path.join('downloads', u.netloc, posixpath.basename(u.path))
    if os.path.exists(dest_name):
        return False
    try:
        i_resp = sess.get(image_url)
        i_resp.raise_for_status()
    except Exception as exc:
        print('[!]->', exc)
        return False

    dest_dir = os.path.dirname(dest_name)
    os.makedirs(dest_dir, exist_ok=True)
    with open(dest_name, 'wb') as outf:
        outf.write(i_resp.content)
        print('->', dest_name, outf.tell())


def slack_download(query):
    for page in itertools.count(1):
        print('Page:', page, file=sys.stderr)
        resp = sess.get('https://slack.com/api/search.all', params={
            'token': slack_token,
            'query': query,
            'count': 20,
            'page': page
        })
        resp.raise_for_status()
        data = resp.json()
        matches = data['messages'].get('matches', ())
        if not matches:
            print('Ran out of matches.', file=sys.stderr)
            break
        for match in matches:
            atts = match.get('attachments', ())
            for att in atts:
                image_url = att.get('image_url')
                if image_url:
                    print(image_url)
                    download_image(image_url)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('query', help='the slack search, e.g. ".jpg from:@akx in:#corgis"')
    args = ap.parse_args()
    slack_download(args.query)
