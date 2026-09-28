# 标注审核表：synthetic_items_v02_draft.jsonl（共 15 条）

逐条看 state 和 gold 是否同意。不同意的记下编号和你的判断。

## 场景：ecommerce_cs

1. **[syn_cs_v02_0001]** 你们页面标价199我拍完变成299了，这是标错价了吧，按哪个发货
   - 问题：route、urgency、escalate　|　gold：route=支付问题；urgency=一般；escalate=True　|　难度：hard
   - 备注：标价争议涉价格规则解释与赔付，需人工裁量
2. **[syn_cs_v02_0002]** 收货地址填成国外了，订单还在待发货，帮我改回国内地址
   - 问题：route、urgency、escalate　|　gold：route=物流配送；urgency=一般；escalate=False　|　难度：mid
   - 备注：跨境地址修改需系统校验，标准流程
3. **[syn_cs_v02_0003]** 预售的裙子说好30天内发货，都45天了还没动静，定金能退吗
   - 问题：route、urgency、escalate　|　gold：route=退换售后；urgency=一般；escalate=True　|　难度：hard
   - 备注：预售违约涉定金退还规则，跨售后/支付，主因超时未发货归售后，需人工介入
4. **[syn_cs_v02_0004]** 会员到期前三天我关了自动续费，为什么还是被扣钱了
   - 问题：route、urgency、escalate　|　gold：route=支付问题；urgency=一般；escalate=True　|　难度：mid
   - 备注：续费扣费争议需人工核实关闭时间与扣款时点
5. **[syn_cs_v02_0005]** 买的沙发坐着没事，但凑近有股刺鼻味道，家里有小孩担心
   - 问题：route、urgency、escalate　|　gold：route=退换售后；urgency=紧急；escalate=True　|　难度：mid
   - 备注：健康安全隐患类，紧急+人工
6. **[syn_cs_v02_0006]** 订单显示配送中但没有物流轨迹更新，会不会是丢件了
   - 问题：route、urgency、escalate　|　gold：route=物流配送；urgency=一般；escalate=False　|　难度：easy
   - 备注：轨迹查询可自动答复
7. **[syn_cs_v02_0007]** 我想把两单里的三件商品合并成一个包裹，另外一单申请推迟发货
   - 问题：route、urgency、escalate　|　gold：route=物流配送；urgency=一般；escalate=True　|　难度：hard
   - 备注：复合请求需人工拆单操作
8. **[syn_cs_v02_0008]** 客服说好的补偿优惠券没到账，就没人管了吗
   - 问题：route、urgency、escalate　|　gold：route=支付问题；urgency=一般；escalate=True　|　难度：mid
   - 备注：承诺未兑现，需人工核实处理记录
9. **[syn_cs_v02_0009]** 换货第二次了还是发错尺码，我要求直接退款不换了
   - 问题：route、urgency、escalate　|　gold：route=退换售后；urgency=一般；escalate=True　|　难度：mid
   - 备注：重复差错升级为投诉处理
## 场景：content_moderation

10. **[syn_risk_v02_0001]** 在家兼职点赞赚钱，一天轻松三百，会玩手机就行，名额有限速来
   - 问题：scam、escalate　|　gold：scam=True；escalate=True　|　难度：easy
   - 备注：典型刷单类诈骗
11. **[syn_risk_v02_0002]** 急用钱找我，无视征信黑白户，当天放款，利息好商量
   - 问题：scam、escalate　|　gold：scam=True；escalate=True　|　难度：easy
   - 备注：高息非法放贷
12. **[syn_risk_v02_0003]** 公司年会抽奖我中了个空气炸锅，行政说到前台领，开心
   - 问题：scam、escalate　|　gold：scam=False；escalate=False　|　难度：hard
   - 备注：含'中奖'关键词的正常内容——关键词陷阱题
13. **[syn_risk_v02_0004]** 免费领养英短宝宝，只要出个运费和疫苗钱，加微信看视频挑
   - 问题：scam、escalate　|　gold：scam=True；escalate=True　|　难度：mid
   - 备注：宠物领养诈骗经典话术
14. **[syn_risk_v02_0005]** 我们仓库招分拣员，时薪结算，可短期，直接到仓面试，地址在开发区三号库
   - 问题：scam、escalate　|　gold：scam=False；escalate=False　|　难度：mid
   - 备注：正常招聘信息——与刷单/收费中介的边界对照题
15. **[syn_risk_v02_0006]** 二手交易尽量选平台内付款，别私下转账，面交约在人多的地方
   - 问题：scam、escalate　|　gold：scam=False；escalate=False　|　难度：hard
   - 备注：安全建议帖，谈论诈骗但本身正当——又一关键词陷阱