# 失败案例集（laya-multi，高置信但答错的 Top 15）

这些是部署中最危险的错误：模型很确定，但确定错了。

1. **[syn_risk_0002｜content_moderation/escalate]** 置信度 1.00
   - 原文：姐妹们我最近在用的这个面膜真的绝了，需要的加我微信xxx低价出
   - 预测：true　|　正确：false　|　前三：true 1.00，false 0.00

2. **[syn_cs_0012｜ecommerce_cs/route]** 置信度 1.00
   - 原文：客服电话打不通，我只能在这说了，退款怎么还没到账，都五天了
   - 预测：退换售后　|　正确：支付问题　|　前三：退换售后 1.00，支付问题 0.00，物流配送 0.00

3. **[mass_0014｜voice_assistant_routing/route]** 置信度 1.00
   - 原文：我十五日要乘飞机
   - 预测：交通出行　|　正确：日历安排　|　前三：交通出行 1.00，日历安排 0.00，天气查询 0.00

4. **[syn_risk_0008｜content_moderation/scam]** 置信度 1.00
   - 原文：冒充客服让我下载屏幕共享软件，还好我留了个心眼，大家小心这种骗局
   - 预测：true　|　正确：false　|　前三：true 1.00，false 0.00

5. **[syn_risk_0014｜content_moderation/scam]** 置信度 1.00
   - 原文：新店开业全场五折，到店消费送鸡蛋，地址在人民路12号
   - 预测：true　|　正确：false　|　前三：true 1.00，false 0.00

6. **[syn_risk_0009｜content_moderation/escalate]** 置信度 0.99
   - 原文：低价代充话费九折，秒到账，稳定渠道长期接单
   - 预测：true　|　正确：false　|　前三：true 0.99，false 0.01

7. **[syn_cs_0023｜ecommerce_cs/route]** 置信度 0.99
   - 原文：下单半小时了想取消订单，还没发货呢
   - 预测：物流配送　|　正确：退换售后　|　前三：物流配送 0.99，退换售后 0.01，账户安全 0.00

8. **[mass_0017｜voice_assistant_routing/route]** 置信度 0.98
   - 原文：我每一天上午九点都需要一个提醒
   - 预测：闹钟计时　|　正确：日历安排　|　前三：闹钟计时 0.98，音乐点播 0.01，天气查询 0.00

9. **[mass_0011｜voice_assistant_routing/route]** 置信度 0.98
   - 原文：请设置提醒我十分钟后上班
   - 预测：闹钟计时　|　正确：日历安排　|　前三：闹钟计时 0.98，音量控制 0.01，天气查询 0.00

10. **[syn_cs_0013｜ecommerce_cs/route]** 置信度 0.98
   - 原文：收到货和我拍的图片完全不一样，你们这是欺诈，我要投诉到底
   - 预测：物流配送　|　正确：退换售后　|　前三：物流配送 0.98，支付问题 0.01，账户安全 0.01

11. **[syn_risk_0005｜content_moderation/scam]** 置信度 0.96
   - 原文：二手出九成新笔记本电脑，因工作调动便宜出，同城可当面交易
   - 预测：true　|　正确：false　|　前三：true 0.96，false 0.04

12. **[mass_0171｜voice_assistant_routing/route]** 置信度 0.96
   - 原文：下一趟去上海站的火车是什么时候
   - 预测：闹钟计时　|　正确：交通出行　|　前三：闹钟计时 0.96，天气查询 0.02，交通出行 0.02

13. **[mass_0044｜voice_assistant_routing/route]** 置信度 0.93
   - 原文：上午或下午
   - 预测：天气查询　|　正确：闹钟计时　|　前三：天气查询 0.93，音乐点播 0.02，闹钟计时 0.01

14. **[syn_risk_0014｜content_moderation/escalate]** 置信度 0.93
   - 原文：新店开业全场五折，到店消费送鸡蛋，地址在人民路12号
   - 预测：true　|　正确：false　|　前三：true 0.93，false 0.07

15. **[syn_cs_0002｜ecommerce_cs/route]** 置信度 0.93
   - 原文：你们发的货破损了，我要退货退款，包装我都拍好了
   - 预测：物流配送　|　正确：退换售后　|　前三：物流配送 0.93，退换售后 0.07，支付问题 0.00

## 顺序敏感案例（E3 翻转，共 29 条，列前 10）

- **[mass_0030｜voice_assistant_routing/route]** 换顺序后答案改变，最大概率极差 0.31
- **[mass_0008｜voice_assistant_routing/route]** 换顺序后答案改变，最大概率极差 0.55
- **[mass_0044｜voice_assistant_routing/route]** 换顺序后答案改变，最大概率极差 0.65
- **[mass_0145｜voice_assistant_routing/route]** 换顺序后答案改变，最大概率极差 0.48
- **[mass_0003｜voice_assistant_routing/route]** 换顺序后答案改变，最大概率极差 0.10
- **[mass_0022｜voice_assistant_routing/route]** 换顺序后答案改变，最大概率极差 0.26
- **[mass_0020｜voice_assistant_routing/route]** 换顺序后答案改变，最大概率极差 0.43
- **[mass_0025｜voice_assistant_routing/route]** 换顺序后答案改变，最大概率极差 0.34
- **[mass_0083｜voice_assistant_routing/route]** 换顺序后答案改变，最大概率极差 0.33
- **[mass_0018｜voice_assistant_routing/route]** 换顺序后答案改变，最大概率极差 0.23
