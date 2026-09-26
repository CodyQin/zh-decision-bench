# -*- coding: utf-8 -*-
"""
冒烟探针：用 3 条中文样例探测 laya-multilingual 的真实输入输出格式。
目的：看清返回的 JSON 结构（概率在哪里、confidence 是什么），
再据此写正式适配器。运行：python src/probe_laya.py
"""
import json
import laya

agent = laya.load("convaiinnovations/laya", subfolder="multilingual")

CASES = [
    # 1. choice：客服工单路由
    {
        "state": "客户来电：我上周买的订单还没到，app上显示已签收但我没收到货，要求投诉。",
        "questions": {
            "route": {
                "type": "choice",
                "instructions": "选择处理部门",
                "criteria": {
                    "物流": "配送、签收、运输问题",
                    "售后": "退换货、维修问题",
                    "投诉": "客户明确要求投诉或曝光",
                },
            }
        },
    },
    # 2. score：紧急度分级（criteria 是有序等级列表）
    {
        "state": "工单：支付页面一直转圈，无法完成付款，客户表示马上要用。",
        "questions": {
            "urgency": {
                "type": "score",
                "instructions": "评估该工单的紧急程度",
                "criteria": ["不紧急", "一般", "紧急"],
            }
        },
    },
    # 3. noul：是否需要人工介入（criteria 用 true/false 键）
    {
        "state": "工单：客户留言询问会员积分怎么兑换，附了截图。",
        "questions": {
            "escalate": {
                "type": "noul",
                "instructions": "是否需要转人工处理",
                "criteria": {"true": "需要人工介入", "false": "可自动回复"},
            }
        },
    },
]

for i, case in enumerate(CASES, 1):
    print(f"\n{'='*60}\n样例 {i}（{case['questions'][list(case['questions'])[0]]['type']}）\n{'='*60}")
    result = agent.predict(state=case["state"], questions=case["questions"])
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
