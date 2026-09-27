# 失败案例集（neohorse，高置信但答错的 Top 15）

这些是部署中最危险的错误：模型很确定，但确定错了。

1. **[mass_0020｜voice_assistant_routing/route]** 置信度 0.97
   - 原文：请每三十分钟给我一次选举的最新情况
   - 预测：闹钟计时　|　正确：日历安排　|　前三：闹钟计时 0.97，日历安排 0.03，交通出行 0.00

2. **[syn_cs_0012｜ecommerce_cs/escalate]** 置信度 0.95
   - 原文：客服电话打不通，我只能在这说了，退款怎么还没到账，都五天了
   - 预测：true　|　正确：false　|　前三：true 0.95，false 0.05

3. **[syn_risk_0015｜content_moderation/escalate]** 置信度 0.95
   - 原文：您的医保账户已停，请于今日内登录 med-care-claim.top 更新信息
   - 预测：false　|　正确：true　|　前三：false 0.95，true 0.05

4. **[syn_risk_0008｜content_moderation/scam]** 置信度 0.94
   - 原文：冒充客服让我下载屏幕共享软件，还好我留了个心眼，大家小心这种骗局
   - 预测：true　|　正确：false　|　前三：true 0.94，false 0.06

5. **[mass_0017｜voice_assistant_routing/route]** 置信度 0.94
   - 原文：我每一天上午九点都需要一个提醒
   - 预测：闹钟计时　|　正确：日历安排　|　前三：闹钟计时 0.94，日历安排 0.06，交通出行 0.00

6. **[mass_0011｜voice_assistant_routing/route]** 置信度 0.91
   - 原文：请设置提醒我十分钟后上班
   - 预测：闹钟计时　|　正确：日历安排　|　前三：闹钟计时 0.91，日历安排 0.09，交通出行 0.00

7. **[syn_cs_0018｜ecommerce_cs/route]** 置信度 0.90
   - 原文：包裹显示运输破损被退回发件人了，你们怎么处理的，我要个说法
   - 预测：退换售后　|　正确：物流配送　|　前三：退换售后 0.90，物流配送 0.10，支付问题 0.00

8. **[syn_risk_0012｜content_moderation/escalate]** 置信度 0.90
   - 原文：扫码进群每天签到就领现金红包，我已经提现50了，亲测有效
   - 预测：false　|　正确：true　|　前三：false 0.90，true 0.10

9. **[syn_cs_0013｜ecommerce_cs/urgency]** 置信度 0.87
   - 原文：收到货和我拍的图片完全不一样，你们这是欺诈，我要投诉到底
   - 预测：紧急　|　正确：一般　|　前三：紧急 0.87，一般 0.10，不紧急 0.03

10. **[mass_0104｜voice_assistant_routing/route]** 置信度 0.87
   - 原文：请重播当前正在播放的歌曲
   - 预测：音量控制　|　正确：音乐点播　|　前三：音量控制 0.87，音乐点播 0.13，闹钟计时 0.00

11. **[syn_cs_0020｜ecommerce_cs/escalate]** 置信度 0.85
   - 原文：付款的时候一直转圈，卡了十分钟了，不敢再点怕重复扣款
   - 预测：true　|　正确：false　|　前三：true 0.85，false 0.15

12. **[syn_cs_0005｜ecommerce_cs/escalate]** 置信度 0.84
   - 原文：问一下你们家这个电饭煲保修几年啊
   - 预测：true　|　正确：false　|　前三：true 0.84，false 0.16

13. **[mass_0099｜voice_assistant_routing/route]** 置信度 0.82
   - 原文：关闭随机播放
   - 预测：音量控制　|　正确：音乐点播　|　前三：音量控制 0.82，音乐点播 0.18，闹钟计时 0.00

14. **[mass_0044｜voice_assistant_routing/route]** 置信度 0.81
   - 原文：上午或下午
   - 预测：日历安排　|　正确：闹钟计时　|　前三：日历安排 0.81，闹钟计时 0.18，天气查询 0.00

15. **[syn_risk_0006｜content_moderation/scam]** 置信度 0.81
   - 原文：您的快递已滞留，请联系138xxxx重新派送并支付保管费5元
   - 预测：false　|　正确：true　|　前三：false 0.81，true 0.19
