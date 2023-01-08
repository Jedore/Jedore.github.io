import os
import time

import requests

BASE_URL = 'https://registry.npmmirror.com/-/binary/python/'

count = 0

def parse_page(url: str, title: str = 'Index of /Python/',
               path: str = 'docs/tools/python-mirrors/', level: int = 1):
    global count
    if level == 2:
        if count > 5:
            return
        count += 1
        print(title)
    if not os.path.exists(path):
        os.makedirs(path)
    rsp = requests.get(url)
    data = rsp.json()
    contents = []
    sorts = []
    for item in data:
        name = item.get('name')
        _sort = name.replace('.', '').replace('/', '')
        if level == 1:
            if not _sort.isdigit():
                continue
        date = item.get('date')
        size = str(item.get('size', '-'))
        if item.get('type') == 'dir':
            href = name
            parse_page(url + name, title + name, path + name, level + 1)
        else:
            href = item.get('url')
        line = f'\n<a href="{href}">{name}</a>{" " * (52 - len(name))}{date}{size.rjust(20)}'
        if level == 1:
            sorts.append((_sort, line))
        else:
            contents.append(line)
    if sorts:
        print('Sync python version count:', len(sorts))
        sorts.sort(key=lambda n: n[0])
        contents = [i[1] for i in sorts]
    gen_html(path + 'index.html', title, contents)


def gen_html(filename: str, title: str, contents: list):
    headers = [
        '<html>',
        f'<head><title>Jedore</title>',
        '<link rel="shortcut icon" href="favicon.ico" >',
        f'</head><body>',
        f'<h1>{title}</h1>',
        '<hr><pre>',
        '<a href="../">../</a>',
    ]
    tails = [
        '\n</pre><hr></body></html>'
    ]
    with open(filename, 'w') as fp:
        fp.writelines(headers + contents + tails)


if __name__ == '__main__':
    start = time.time()
    parse_page(BASE_URL)
    end = time.time()
    print('duration:', end - start)
