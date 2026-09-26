# 标注审核表：synthetic_items.jsonl（共 40 条）

逐条看 state 和 gold 是否同意。不同意的记下编号和你的判断。

## 场景：ecommerce_cs

1. **[syn_cs_0001]** 我的快递三天了一直显示在揽收，到底发没发货啊
   - 问题：route、urgency、escalate　|　gold：route=物流配送；urgency=一般；escalate=False　|　难度：easy
   - 备注：标准物流咨询
2. **[syn_cs_0002]** 你们发的货破损了，我要退货退款，包装我都拍好了
   - 问题：route、urgency、escalate　|　gold：route=退换售后；urgency=一般；escalate=False　|　难度：easy
   - 备注：标准退货，材料齐全可自动流程
3. **[syn_cs_0003]** 刚才支付的时候钱扣了两笔！订单只显示一笔，多扣的钱去哪了
   - 问题：route、urgency、escalate　|　gold：route=支付问题；urgency=紧急；escalate=True　|　难度：easy
   - 备注：重复扣款涉资金，紧急且需对账
4. **[syn_cs_0004]** 我账号被盗了，有人改了我的手机号，快帮我冻结
   - 问题：route、urgency、escalate　|　gold：route=账户安全；urgency=紧急；escalate=True　|　难度：easy
   - 备注：盗号必须人工核身
5. **[syn_cs_0005]** 问一下你们家这个电饭煲保修几年啊
   - 问题：route、urgency、escalate　|　gold：route=退换售后；urgency=不紧急；escalate=False　|　难度：easy
   - 备注：保修咨询属售后知识问答
6. **[syn_cs_0006]** 快递员把我的包裹放在丰巢了但根本没通知我，找了半天
   - 问题：route、urgency、escalate　|　gold：route=物流配送；urgency=一般；escalate=False　|　难度：easy
7. **[syn_cs_0007]** 买的鞋子尺码不对想换一双42的
   - 问题：route、urgency、escalate　|　gold：route=退换售后；urgency=一般；escalate=False　|　难度：easy
8. **[syn_cs_0008]** app上优惠券用不了，一直报错说活动已结束，可是我领的时候没过期
   - 问题：route、urgency、escalate　|　gold：route=支付问题；urgency=一般；escalate=False　|　难度：mid
   - 备注：优惠券归支付/订单优惠
9. **[syn_cs_0009]** 我在你们平台买的手机充电发烫严重，会不会爆炸啊，太危险了
   - 问题：route、urgency、escalate　|　gold：route=退换售后；urgency=紧急；escalate=True　|　难度：mid
   - 备注：产品安全隐患需人工加急
10. **[syn_cs_0010]** 物流信息显示已签收但我没收到货，联系快递员也不回
   - 问题：route、urgency、escalate　|　gold：route=物流配送；urgency=紧急；escalate=True　|　难度：mid
   - 备注：虚假签收需人工向承运方核实
11. **[syn_cs_0011]** 帮我查下我的订单什么时候到，单号忘了，账号是这个手机号
   - 问题：route、urgency、escalate　|　gold：route=物流配送；urgency=不紧急；escalate=False　|　难度：easy
12. **[syn_cs_0012]** 客服电话打不通，我只能在这说了，退款怎么还没到账，都五天了
   - 问题：route、urgency、escalate　|　gold：route=支付问题；urgency=一般；escalate=False　|　难度：easy
   - 备注：退款进度可自动查询答复
13. **[syn_cs_0013]** 收到货和我拍的图片完全不一样，你们这是欺诈，我要投诉到底
   - 问题：route、urgency、escalate　|　gold：route=退换售后；urgency=一般；escalate=True　|　难度：mid
   - 备注：货不对板+强烈投诉情绪，需人工安抚
14. **[syn_cs_0014]** 怎么修改收货地址啊，下单才发现填错了
   - 问题：route、urgency、escalate　|　gold：route=物流配送；urgency=一般；escalate=False　|　难度：easy
   - 备注：地址修改需尽快但流程标准
15. **[syn_cs_0015]** 你们泄露了我的个人信息！我刚接到自称你们客服的诈骗电话，能报出我的订单号！
   - 问题：route、urgency、escalate　|　gold：route=账户安全；urgency=紧急；escalate=True　|　难度：hard
   - 备注：表面是诈骗电话，实质是信息泄露指控，归账户安全
16. **[syn_cs_0016]** 会员自动续费怎么关闭
   - 问题：route、urgency、escalate　|　gold：route=支付问题；urgency=不紧急；escalate=False　|　难度：mid
   - 备注：续费扣款管理归支付（人工审定 2026-09-25）
17. **[syn_cs_0017]** 昨天下的单今天降价了50块，能补差价吗
   - 问题：route、urgency、escalate　|　gold：route=退换售后；urgency=一般；escalate=False　|　难度：mid
   - 备注：价保在售后类
18. **[syn_cs_0018]** 包裹显示运输破损被退回发件人了，你们怎么处理的，我要个说法
   - 问题：route、urgency、escalate　|　gold：route=物流配送；urgency=一般；escalate=True　|　难度：mid
   - 备注：无安全风险/即时止损需求，降为一般（人工审定）
19. **[syn_cs_0019]** 开发票可以吗，电子发票发我邮箱
   - 问题：route、urgency、escalate　|　gold：route=支付问题；urgency=不紧急；escalate=False　|　难度：easy
   - 备注：发票归支付/订单类
20. **[syn_cs_0020]** 付款的时候一直转圈，卡了十分钟了，不敢再点怕重复扣款
   - 问题：route、urgency、escalate　|　gold：route=支付问题；urgency=紧急；escalate=False　|　难度：mid
   - 备注：系统可自动查支付状态，异常才升级（人工审定）
21. **[syn_cs_0021]** 退货的快递你们签收一个星期了退款还没处理
   - 问题：route、urgency、escalate　|　gold：route=退换售后；urgency=一般；escalate=True　|　难度：hard
   - 备注：跨售后+支付（退款），主因是售后超时，需人工催办
22. **[syn_cs_0022]** 我在你们店买了三单，想合并成一个包裹发货
   - 问题：route、urgency、escalate　|　gold：route=物流配送；urgency=一般；escalate=False　|　难度：easy
   - 备注：需赶在发货前处理，具时效性（人工审定）
23. **[syn_cs_0023]** 下单半小时了想取消订单，还没发货呢
   - 问题：route、urgency、escalate　|　gold：route=退换售后；urgency=一般；escalate=False　|　难度：mid
   - 备注：取消订单走售后流程，需赶在发货前
24. **[syn_cs_0024]** 骚扰电话太多了，你们把我号码卖了吧？我要投诉你们平台
   - 问题：route、urgency、escalate　|　gold：route=账户安全；urgency=紧急；escalate=True　|　难度：hard
   - 备注：信息泄露投诉，情绪激烈
25. **[syn_cs_0025]** 我买的生鲜到的时候都化冻了，一箱子水
   - 问题：route、urgency、escalate　|　gold：route=退换售后；urgency=紧急；escalate=False　|　难度：hard
   - 备注：紧急但理赔流程标准可自动——紧急度与转人工解耦的案例
## 场景：content_moderation

26. **[syn_risk_0001]** 【官方】您的账户存在异常，请点击链接 verification-secure.xyz 核实身份，否则将冻结
   - 问题：scam、escalate　|　gold：scam=True；escalate=True　|　难度：easy
   - 备注：仿官方钓鱼链接
27. **[syn_risk_0002]** 姐妹们我最近在用的这个面膜真的绝了，需要的加我微信xxx低价出
   - 问题：scam、escalate　|　gold：scam=True；escalate=False　|　难度：easy
   - 备注：站外低价引流：按'诈骗或违规引流'定义判 True（人工审定）
28. **[syn_risk_0003]** 小区群里通知：明天上午停电检修，请大家提前准备
   - 问题：scam、escalate　|　gold：scam=False；escalate=False　|　难度：easy
29. **[syn_risk_0004]** 恭喜您被抽中为幸运用户，领取888元红包，24小时内有效，加客服QQ领取
   - 问题：scam、escalate　|　gold：scam=True；escalate=True　|　难度：easy
   - 备注：典型中奖诈骗
30. **[syn_risk_0005]** 二手出九成新笔记本电脑，因工作调动便宜出，同城可当面交易
   - 问题：scam、escalate　|　gold：scam=False；escalate=False　|　难度：easy
   - 备注：正常二手交易
31. **[syn_risk_0006]** 您的快递已滞留，请联系138xxxx重新派送并支付保管费5元
   - 问题：scam、escalate　|　gold：scam=True；escalate=True　|　难度：mid
   - 备注：快递保管费诈骗
32. **[syn_risk_0007]** 今晚球赛有人一起看吗，老地方
   - 问题：scam、escalate　|　gold：scam=False；escalate=False　|　难度：easy
33. **[syn_risk_0008]** 冒充客服让我下载屏幕共享软件，还好我留了个心眼，大家小心这种骗局
   - 问题：scam、escalate　|　gold：scam=False；escalate=False　|　难度：hard
   - 备注：反诈提醒帖，谈论诈骗但本身不是诈骗——关键词陷阱
34. **[syn_risk_0009]** 低价代充话费九折，秒到账，稳定渠道长期接单
   - 问题：scam、escalate　|　gold：scam=True；escalate=False　|　难度：mid
   - 备注：灰产代充：违规引流而非确证诈骗，审定时存疑后按定义保留 True
35. **[syn_risk_0010]** 公司内部渠道茅台，价格美丽，数量不多先到先得
   - 问题：scam、escalate　|　gold：scam=True；escalate=True　|　难度：mid
   - 备注：假冒内购：违规引流而非确证诈骗，同上
36. **[syn_risk_0011]** 请问有人捡到一只橘猫吗？走丢两天了，酬谢
   - 问题：scam、escalate　|　gold：scam=False；escalate=False　|　难度：easy
37. **[syn_risk_0012]** 扫码进群每天签到就领现金红包，我已经提现50了，亲测有效
   - 问题：scam、escalate　|　gold：scam=True；escalate=True　|　难度：mid
   - 备注：拉人头类骗局，涉资金需人工
38. **[syn_risk_0013]** 租房中介跑路了，我们十几个租客的钱要不回来，求媒体关注
   - 问题：scam、escalate　|　gold：scam=False；escalate=True　|　难度：hard
   - 备注：真实求助：不是诈骗内容但需要人工介入——scam与escalate解耦案例
39. **[syn_risk_0014]** 新店开业全场五折，到店消费送鸡蛋，地址在人民路12号
   - 问题：scam、escalate　|　gold：scam=False；escalate=False　|　难度：easy
   - 备注：正常商家促销
40. **[syn_risk_0015]** 您的医保账户已停，请于今日内登录 med-care-claim.top 更新信息
   - 问题：scam、escalate　|　gold：scam=True；escalate=True　|　难度：easy
   - 备注：仿医保钓鱼