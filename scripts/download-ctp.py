import asyncio
import re
from datetime import datetime as dt
from multiprocessing.forkserver import connect_to_new_process

import httpx
from bs4 import BeautifulSoup

CLIENT = httpx.AsyncClient(timeout=10)


def sel_a(li, ctp):
    links = li.css.select('a')
    for link in links:
        if 'api下载' in str(link):
            api_link = 'http://www.sfit.com.cn/' + link.get('href')
            ctp['api_link'] = api_link
        if 'chm下载' in str(link):
            chm_link = 'http://www.sfit.com.cn/' + link.get('href')
            ctp['chm_link'] = chm_link
    update_time = re.match(r'.*<span>更新时间. *(.+)</span></h5>',
                           str(li), re.DOTALL).group(1)
    ctp['update_time'] = update_time


async def parse_history():
    rsp = await CLIENT.get('http://www.sfit.com.cn/5_2_DocumentDown_6.htm')
    soup = BeautifulSoup(rsp.content, 'html.parser')
    lis = soup.css.select('.softdown_ctpapi > ul > li')
    ctps = []
    for li in lis:
        ret1 = re.match(r'.*<h5>(.*)<div.*div>(.+)<span>.+</span></h5>',
                        str(li), re.DOTALL)

        ret2 = re.match(r'.*<h5>(.*)<span>.+</span></h5>', str(li),
                        re.DOTALL)
        ctp = {}
        if ret1 is None and ret2 is None:
            continue
        if ret1:
            title = ret1.group(1) + ret1.group(2)
        if ret2:
            title = ret2.group(1)

        if '期货期权' not in title:
            continue
        if 'IOS' in title:
            continue
        if 'Android' in title:
            continue
        if 'SM' in title:
            continue

        version = re.match(r'.+版本号. *(\S+) ?.*', title).group(1)
        ctp['title'] = title
        ctp['version'] = version
        sel_a(li, ctp)
        ctps.append(ctp)
    return ctps


async def parse_pc():
    rsp = await CLIENT.get('http://www.sfit.com.cn/5_2_DocumentDown_2_2.htm')
    soup = BeautifulSoup(rsp.content, 'html.parser')
    lis = soup.css.select('.softdown_ctpapi > ul > li')
    ctps = []
    for li in lis:
        ret = re.match(r'.*<div.*div>(.+)<span>.+</span></h5>',
                       str(li), re.DOTALL)
        ctp = {}
        if ret is not None:
            title = ret.group(1)
            version = re.match(r'.+版本号. *(\S+) ?.*', title).group(1)
            ctp['title'] = title
            ctp['version'] = version
            if 'FIX' in title:
                continue
            if 'tgate' in title:
                continue
            if 'SM' in title:
                continue
            links = li.css.select('a')
            for link in links:
                if 'api下载' in str(link):
                    api_link = 'http://www.sfit.com.cn/' + link.get('href')
                    ctp['api_link'] = api_link
                if 'chm下载' in str(link):
                    chm_link = 'http://www.sfit.com.cn/' + link.get('href')
                    ctp['chm_link'] = chm_link
            update_time = re.match(r'.*<span>更新时间. *(.+)</span></h5>',
                                   str(li), re.DOTALL).group(1)
            ctp['update_time'] = update_time
            ctps.append(ctp)
    return ctps


async def parse_mac():
    rsp = await CLIENT.get('http://www.sfit.com.cn/5_2_DocumentDown_2_3.htm')
    soup = BeautifulSoup(rsp.content, 'html.parser')
    lis = soup.css.select('.softdown_ctpapi > ul > li')
    ctps = []
    for li in lis:
        ret = re.match(r'.*<div.*div>(.+)<span>.+</span></h5>',
                       str(li), re.DOTALL)
        ctp = {}
        if ret is not None:
            title = ret.group(1)
            version = re.match(r'.+版本号. *(\S+) ?.*', title).group(1)
            ctp['title'] = title
            ctp['version'] = version
            links = li.css.select('a')
            for link in links:
                if 'api下载' in str(link):
                    api_link = 'http://www.sfit.com.cn/' + link.get('href')
                    ctp['api_link'] = api_link
            update_time = re.match(r'.*<span>更新时间. *(.+)</span></h5>',
                                   str(li), re.DOTALL).group(1)
            ctp['update_time'] = update_time
            ctps.append(ctp)
    return ctps


async def download(ctps):
    # todo
    for ctp in ctps:
        pass


async def run():
    t1 = await parse_history()
    t2 = await parse_pc()
    t3 = await parse_mac()

    ctps = t1 + t2 + t3
    ctps = sorted(ctps, key=lambda c: c['version'])


def main():
    start_time = dt.now()
    asyncio.run(run())
    total_seconds = (dt.now() - start_time).total_seconds()
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    print(f"Time cost: {minutes} min {seconds} second")


if __name__ == '__main__':
    main()
