import os
import time

import requests

BASE_URL = 'https://registry.npmmirror.com/-/binary/python/'
count = 0


def parse_page(url: str, title: str = 'Index of /Python/',
               path: str = '../tools/python-mirrors/',
               filename: str = 'python.html', level: int = 1):
    global count
    if level == 2:
        if count > 5:
            return
        count += 1
        print(title)
    time.sleep(1)
    if not os.path.exists(path):
        os.makedirs(path)
    rsp = requests.get(url)
    data = rsp.json()
    contents = []
    for item in data:
        name = item.get('name')
        date = item.get('date')
        size = str(item.get('size', '-'))
        line = f'\n<a href="{name}">{name}</a>{" " * (52 - len(name))}{date}{size.rjust(20)}'
        if item.get('type') == 'dir':
            parse_page(url + name, title + name, path + name,
                       f'{name.strip("/")}.html', level + 1)
        contents.append(line)

    gen_html(path + filename, title, contents)


def gen_html(filename: str, title: str, contents: list):
    headers = [
        '<html>',
        f'<head><title>{title}</title></head>',
        '<body>',
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
    parse_page(BASE_URL)
