---
title: "openctp-ctp 连接TTS、华鑫股票、中泰XTP等其他柜台"
description:
date: 2024-07-24T12:37:02+08:00
math: false
image:
license:
hidden: false
comments: false
draft: false
tags:
  - ctp
  - openctp
categories:
  - ctp
style:
keywords:
---

[openctp-ctp](https://github.com/Jedore/openctp-ctp-python) 是由 openctp 使用Swig技术制作的Python版CTPAPI。 简化了对接CTPAPI的过程，节省精力，快速上手 🚀

但 openctp-ctp 库默认只支持CTP柜台，如需连接TTS、XTP、TORA等柜台，需要使用openctp的CTPAPI兼容接口方式，将CTP的dll（如thosttraderapi_se.dll）替换为相应柜台的版本即可。

由于一些新手对 openctp-ctp 不够熟悉，替换过程中容易出现一些奇奇怪怪的问题，所以现在有了一个更便捷的方式: **[openctp-ctp-channels](https://github.com/Jedore/openctp-ctp-channels)**

```bash
$ pip install openctp-ctp-channels.
# 支持通道柜台
$ openctp-channels show
Support channels:
        ctp - 上期技术CTPAPI
        tts - openctp TTS 7x24
        tts-s - openctp TTS仿真(接实盘行情)
        emt - 东方财富EMT
        xtp - 中泰证券XTP
        tora - 华鑫证券奇点股票
        qq - 腾讯财经(只有行情)
        sina - 新浪财经(只有行情)
# 当前通道柜台
$ openctp-channels check
Current channel: ctp

# 切换通道柜台
$ openctp-channels switch tts
```

更多示例参考 [ctp.examples](https://github.com/Jedore/ctp.examples)