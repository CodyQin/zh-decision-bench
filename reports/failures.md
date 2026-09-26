# 失败案例集（qwen，高置信但答错的 Top 15）

这些是部署中最危险的错误：模型很确定，但确定错了。

1. **[syn_risk_0008｜content_moderation/scam]** 置信度 1.00
   - 原文：冒充客服让我下载屏幕共享软件，还好我留了个心眼，大家小心这种骗局
   - 预测：true　|　正确：false　|　前三：true 1.00，false 0.00

2. **[mass_0011｜voice_assistant_routing/route]** 置信度 0.99
   - 原文：请设置提醒我十分钟后上班
   - 预测：闹钟计时　|　正确：日历安排　|　前三：闹钟计时 0.99，日历安排 0.01，音乐点播 0.00

3. **[syn_cs_0018｜ecommerce_cs/route]** 置信度 0.99
   - 原文：包裹显示运输破损被退回发件人了，你们怎么处理的，我要个说法
   - 预测：退换售后　|　正确：物流配送　|　前三：退换售后 0.99，物流配送 0.01，支付问题 0.00

4. **[syn_cs_0001｜ecommerce_cs/escalate]** 置信度 0.99
   - 原文：我的快递三天了一直显示在揽收，到底发没发货啊
   - 预测：true　|　正确：false　|　前三：true 0.99，false 0.01

5. **[syn_cs_0012｜ecommerce_cs/escalate]** 置信度 0.99
   - 原文：客服电话打不通，我只能在这说了，退款怎么还没到账，都五天了
   - 预测：true　|　正确：false　|　前三：true 0.99，false 0.01

6. **[syn_cs_0006｜ecommerce_cs/escalate]** 置信度 0.98
   - 原文：快递员把我的包裹放在丰巢了但根本没通知我，找了半天
   - 预测：true　|　正确：false　|　前三：true 0.98，false 0.02

7. **[syn_risk_0013｜content_moderation/scam]** 置信度 0.98
   - 原文：租房中介跑路了，我们十几个租客的钱要不回来，求媒体关注
   - 预测：true　|　正确：false　|　前三：true 0.98，false 0.02

8. **[syn_cs_0008｜ecommerce_cs/escalate]** 置信度 0.97
   - 原文：app上优惠券用不了，一直报错说活动已结束，可是我领的时候没过期
   - 预测：true　|　正确：false　|　前三：true 0.97，false 0.03

9. **[syn_cs_0025｜ecommerce_cs/escalate]** 置信度 0.97
   - 原文：我买的生鲜到的时候都化冻了，一箱子水
   - 预测：true　|　正确：false　|　前三：true 0.97，false 0.03

10. **[syn_risk_0011｜content_moderation/scam]** 置信度 0.97
   - 原文：请问有人捡到一只橘猫吗？走丢两天了，酬谢
   - 预测：true　|　正确：false　|　前三：true 0.97，false 0.03

11. **[syn_cs_0013｜ecommerce_cs/urgency]** 置信度 0.97
   - 原文：收到货和我拍的图片完全不一样，你们这是欺诈，我要投诉到底
   - 预测：紧急　|　正确：一般　|　前三：紧急 0.97，不紧急 0.02，一般 0.01

12. **[mass_0017｜voice_assistant_routing/route]** 置信度 0.96
   - 原文：我每一天上午九点都需要一个提醒
   - 预测：闹钟计时　|　正确：日历安排　|　前三：闹钟计时 0.96，日历安排 0.04，音乐点播 0.00

13. **[syn_cs_0002｜ecommerce_cs/escalate]** 置信度 0.95
   - 原文：你们发的货破损了，我要退货退款，包装我都拍好了
   - 预测：true　|　正确：false　|　前三：true 0.95，false 0.05

14. **[syn_risk_0011｜content_moderation/escalate]** 置信度 0.94
   - 原文：请问有人捡到一只橘猫吗？走丢两天了，酬谢
   - 预测：true　|　正确：false　|　前三：true 0.94，false 0.06

15. **[syn_cs_0014｜ecommerce_cs/escalate]** 置信度 0.92
   - 原文：怎么修改收货地址啊，下单才发现填错了
   - 预测：true　|　正确：false　|　前三：true 0.92，false 0.08

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
