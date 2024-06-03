---
title: "Python查询CTP结算单，补足缺失数据"
description:
date: 2024-06-02T21:11:28+08:00
math: false
image:
license:
hidden: false
comments: false
draft: false
tags:
  - ctp
categories:
  - CTP
style:
keywords:
---

> 结算单是CTP平台的一个重要组成部分，它用于记录和展示期货交易的结算结果。在CTP中，查询结算单可以通过调用ReqQrySettlementInfo函数来实现。这个函数允许查询当天或历史结算单，也可以查询月结算单，但前提是CTP柜台已经生成了相应的日或月结算单。调用这个函数需要提供一些参数，如经纪公司代码、投资者代码、交易日等。结算单的内容会在Content字段中返回，可能需要多次响应才能返回完整的结算单内容。
>
> 例如，要查询某一天的结算单，你需要设置TradingDay参数为相应的日期（格式为“yyyymmdd”）；而查询某一月的结算单，则设置TradingDay参数为相应的年月（格式为“yyyymm”）。此外，nRequestID是一个由用户维护的请求ID，用于在响应中对应请求。
> 
> 总的来说，CTP的结算单查询功能为用户提供了一个详细和灵活的方式来获取他们的交易结算信息。这对于期货交易者来说是一个重要的工具，因为它可以帮助他们跟踪和评估他们的交易表现。

之前在使用 Python版CTPAPI 查询结算单时，偶尔会发现，有时候得到的结算单是不完整的，直接看代码和结果吧。

查询结算单和处理响应的代码是这样的

```python
    def settlement_info(self):
    """请求查询投资者结算结果"""
    print("> 请求查询投资者结算结果")
    req = tdapi.CThostFtdcQrySettlementInfoField()
    req.BrokerID = self._broker_id
    req.InvestorID = self._user
    self._check_req(req, self._api.ReqQrySettlementInfo(req, 0))


def OnRspQrySettlementInfo(
    self,
    pSettlementInfo: tdapi.CThostFtdcSettlementInfoField,
    pRspInfo: tdapi.CThostFtdcRspInfoField,
    nRequestID: int,
    bIsLast: bool,
):
    """请求查询投资者结算结果响应"""
    if pRspInfo and pRspInfo.ErrorID:
        print("失败")
        return

    if not bIsLast:
        if pSettlementInfo:
            self.content += pSettlementInfo.Content
    if bIsLast:
        if pSettlementInfo:
            self.content += pSettlementInfo.Content
        print(self.content)
```

实际测试输出的结果是这样的

```text
                                           SimNow社区系统                                           
                                                                    制表时间 Creation Date：20210901
----------------------------------------------------------------------------------------------------
                             交易结算单(盯市) Settlement Statement(MTM)                             
客户号 Client ID：  058762          客户名称 Client Name：罗马
日期 Date：20210901

     权市值       |
|Exchange|     Product      |   Instrument   |Open Date|    S/H     | B/S |Positon|Pos. Open Price|   Prev. Sttl   |Settlement Price| Accum. P/L |  MTM P/L  |  Margin   | Market Value(Options)|
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
| 中金所 |   沪深300指数    |     IF2109     | 20210623|交易        |   卖|      1|       5086.000|        4766.800|        4855.000|    69300.00|  -26460.00|  160215.00|                  0.00|
| 中金所 |   沪深300指数    |     IF2109     | 20210623|交易        |   卖|      1|       5086.000|        4766.800|        4855.000|    69300.00|  -26460.00|  160215.00|                  0.00|
| 中金所 |   沪深300指数    |     IF2109     | 20210625|交易        |   卖|      1|       5163.000|        4766.800|        4855.000|    92400.00|  -26460.00|  160215.00|                  0.00|
| 中金所 |   沪深300指数    |     IF2109     | 20210625|交易        |买   |      1|       5164.400|        4766.800|        4855.000|   -92820.00|   26460.00|  160215.00|                  0.00|
| 中金所 |   沪深300指数    |     IF2109     | 20210625|交易        |买   |      1|       5162.200|        4766.800|        4855.000|   -92160.00|   26460.00|  160215.00|                  0.00|
| 中金所 |   沪深300指数    |     IF2109     | 20210625|交易        |   卖|      1|       5160.000|        4766.800|        4855.000|    91500.00|  -26460.00|  160215.00|                  0.00|
| 中金所 |   沪深300指数    |     IF2109     | 20210625|交易        |买   |      1|       5159.000|        4766.800|        4855.000|   -91200.00|   26460.00|  160215.00|                  0.00|
...(省略后面的内容)
```

是不是感觉不太对，其他都对，怎么乱入了一个“权市值”？

继续测试，给代码加点小料，打印一下每次返回的 Content长度

```python
        if not bIsLast:
    if pSettlementInfo:
        print('Content:', len(pSettlementInfo.Content))
        self.content += pSettlementInfo.Content
if bIsLast:
    if pSettlementInfo:
        print('Content:', len(pSettlementInfo.Content))
        self.content += pSettlementInfo.Content
    print(self.content)
```

然后再进行测试， 会得到如下的一段信息

```text
Content: 470
Content: 0
Content: 0
Content: 0
Content: 0
Content: 487
Content: 477
Content: 473
Content: 473
Content: 477
Content: 0
Content: 0
Content: 470
Content: 480
Content: 470
Content: 473
Content: 477
Content: 473
Content: 477
Content: 470
Content: 480
Content: 470
Content: 0
Content: 0
Content: 473
Content: 477
Content: 471
Content: 479
Content: 470
Content: 479
Content: 471
Content: 473
Content: 477
Content: 473
Content: 477
Content: 470
Content: 480
Content: 480
Content: 0
Content: 0
Content: 459
Content: 492
Content: 377
```

这次能明显看出来问题了，有很多Content长度为0的, 这就是导致上面的 “权市值” 问题的一个原因。

网上有一些文章深度解释过了，一搜就能搜到（CTP UTF-8转码错误），说这是因为 Python版CTPAPI 在进行转码时遇到了字符长度切分问题，正好把一个字符切成了两份，
导致转码失败，就丢失了这部分信息。作者关于这方面的了解不多，就不去深入解释了，有兴趣的可以搜搜看。

现在有一种的新的方案可以解决上面的问题，并且验证成功, 直接上代码吧:

```python
    def OnRspQrySettlementInfo(
    self,
    pSettlementInfo: tdapi.CThostFtdcSettlementInfoField,
    pRspInfo: tdapi.CThostFtdcRspInfoField,
    nRequestID: int,
    bIsLast: bool,
):
    """ 请求查询投资者结算结果响应 """

    if pRspInfo and pRspInfo.ErrorID:
        print(f"请求查询投资者结算结果响应失败: ErrorID={pRspInfo.ErrorID} ErrorMsg={pRspInfo.ErrorMsg}")
        return

    if not bIsLast:
        if pSettlementInfo:
            self.content += pSettlementInfo.Content
    if bIsLast:
        if pSettlementInfo:
            self.content += pSettlementInfo.Content
        print(self.content.decode("gbk"))
        self.content = b""
```

看起来似乎代码和上面的差别并不大，确实，只有细微改变。 但是测试结果却大不相同，还是同样的账号，同样的环境，运行结果如下:

```text
                                           SimNow社区系统                                           
                                                                    制表时间 Creation Date：20210901
----------------------------------------------------------------------------------------------------
                             交易结算单(盯市) Settlement Statement(MTM)                             
客户号 Client ID：  058762          客户名称 Client Name：罗马
日期 Date：20210901

                   资金状况  币种：人民币  Account Summary  Currency：CNY 
----------------------------------------------------------------------------------------------------
期初结存 Balance b/f：                 19995085.19  基础保证金 Initial Margin：                 0.00
出 入 金 Deposit/Withdrawal：                 0.00  期末结存 Balance c/f：               19995085.19
平仓盈亏 Realized P/L：                       0.00  质 押 金 Pledge Amount：                    0.00
持仓盯市盈亏 MTM P/L：                        0.00  客户权益 Client Equity：：           19995085.19
期权执行盈亏 Exercise P/L：                   0.00  货币质押保证金占用 FX Pledge Occ.：         0.00
手 续 费 Commission：                         0.00  保证金占用 Margin Occupied：          8491395.00
行权手续费 Exercise Fee：                     0.00  交割保证金 Delivery Margin：                0.00
交割手续费 Delivery Fee：                     0.00  多头期权市值 Market value(long)：           0.00
货币质入 New FX Pledge：                      0.00  空头期权市值 Market value(short)：          0.00
货币质出 FX Redemption：                      0.00  市值权益 Market value(equity)：      19995085.19
质押变化金额 Chg in Pledge Amt：              0.00  可用资金 Fund Avail.：               11503690.19
权利金收入 Premium received：                 0.00  风 险 度 Risk Degree：                    42.47%
权利金支出 Premium paid：                     0.00  应追加资金 Margin Call：                    0.00
货币质押变化金额 Chg in FX Pledge:            0.00

                                              持仓明细 Positions Detail
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
| 交易所 |       品种       |      合约      |开仓日期 |   投/保    |买/卖|持仓量 |    开仓价     |     昨结算     |     结算价     |  浮动盈亏  |  盯市盈亏 |  保证金   |       期权市值       |
|Exchange|     Product      |   Instrument   |Open Date|    S/H     | B/S |Positon|Pos. Open Price|   Prev. Sttl   |Settlement Price| Accum. P/L |  MTM P/L  |  Margin   | Market Value(Options)|
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
| 中金所 |   沪深300指数    |     IF2109     | 20210623|交易        |   卖|      1|       5086.000|        4766.800|        4855.000|    69300.00|  -26460.00|  160215.00|                  0.00|
...(省略后面的内容)
```

可以看到，相比上面的结算单信息，在开头多出了资金状况的信息，并且也看到了 “权市值” 字符串, 其实是 “起权市值”， 以及完整的表单信息, 看上去顺眼多了。

友情提示，需要安装最新版CTPAPI版本对应openctp-ctp最新版

测试环境：SimNow 7x24

测试源码地址: https://github.com/Jedore/ctp.examples/blob/main/openctp-ctp/ReqQrySettlementInfo.py 