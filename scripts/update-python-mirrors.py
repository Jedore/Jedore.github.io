import os
import time

import requests

BASE_URL = 'https://registry.npmmirror.com/-/binary/python/'


def parse_page(url: str, title: str = 'Index of /Python/',
               path: str = '../docs/tools/python-mirrors/',
               filename: str = 'index.html', level: int = 1):
    if level == 2:
        print(title)
    if not os.path.exists(path):
        os.makedirs(path)
    rsp = requests.get(url)
    data = rsp.json()
    contents = []
    for item in data:
        name = item.get('name')
        if level == 1 and not name.replace('.', '').replace('/', '').isdigit():
            continue
        date = item.get('date')
        size = str(item.get('size', '-'))
        if item.get('type') == 'dir':
            href = name
            parse_page(url + name, title + name, path + name,
                       f'{name.strip("/")}.html', level + 1)
        else:
            href = item.get('url')
        line = f'\n<a href="{href}">{name}</a>{" " * (52 - len(name))}{date}{size.rjust(20)}'
        contents.append(line)

    gen_html(path + filename, title, contents)


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
        '</pre><hr></body></html>'
    ]
    with open(filename, 'w') as fp:
        fp.writelines(headers + contents + tails)


if __name__ == '__main__':
    start = time.time()
    parse_page(BASE_URL)
    end = time.time()
    print('duration:', end - start)
