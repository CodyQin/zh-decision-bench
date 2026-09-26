# -*- coding: utf-8 -*-
"""
应用 2026-09-25 人工审定（Cody）对合成数据的修改。
详见 data/review_log.md。运行后需重跑全部模型。
"""
import json
from pathlib import Path

SRC = Path("data/synthetic_items.jsonl")

# 客服场景：选项描述调整（16条决定的连带修改）
OLD_PAY = "扣款、退款到账、优惠券、发票"
NEW_PAY = "扣款、退款到账、优惠券、发票、订阅续费"
OLD_ACC = "盗号、信息泄露、封号、续费设置"
NEW_ACC = "盗号、信息泄露、封号、账户设置"

# 风控场景：问题定义调整（27条决定的连带修改）
OLD_INSTR = "是否疑似诈骗或垃圾信息"
NEW_INSTR = "是否疑似诈骗或违规引流"
OLD_CRIT = "疑似诈骗/垃圾信息"
NEW_CRIT = "疑似诈骗/违规引流"

GOLD_PATCH = {
    "syn_cs_0016": {"route": "支付问题"},
    "syn_cs_0018": {"urgency": "一般"},
    "syn_cs_0020": {"escalate": False},
    "syn_cs_0022": {"urgency": "一般"},
}

NOTES_PATCH = {
    "syn_cs_0016": "续费扣款管理归支付（人工审定 2026-09-25）",
    "syn_cs_0018": "无安全风险/即时止损需求，降为一般（人工审定）",
    "syn_cs_0020": "系统可自动查支付状态，异常才升级（人工审定）",
    "syn_cs_0022": "需赶在发货前处理，具时效性（人工审定）",
    "syn_risk_0002": "站外低价引流：按'诈骗或违规引流'定义判 True（人工审定）",
    "syn_risk_0009": "灰产代充：违规引流而非确证诈骗，审定时存疑后按定义保留 True",
    "syn_risk_0010": "假冒内购：违规引流而非确证诈骗，同上",
}


def main():
    items = [json.loads(l) for l in SRC.read_text(encoding="utf-8").splitlines() if l.strip()]
    for it in items:
        # gold 修改
        for k, v in GOLD_PATCH.get(it["id"], {}).items():
            it["gold"][k] = v
        # 备注修改
        if it["id"] in NOTES_PATCH:
            it["notes"] = NOTES_PATCH[it["id"]]
        # 客服场景选项描述（所有 cs 条目统一）
        if it["domain"] == "ecommerce_cs":
            crit = it["questions"]["route"]["criteria"]
            if "支付问题" in crit:
                crit["支付问题"] = NEW_PAY
            if "账户安全" in crit:
                crit["账户安全"] = NEW_ACC
        # 风控场景问题定义（所有 risk 条目统一）
        if it["domain"] == "content_moderation":
            sc = it["questions"]["scam"]
            sc["instructions"] = NEW_INSTR
            sc["criteria"]["true"] = NEW_CRIT
    SRC.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in items) + "\n",
                   encoding="utf-8")
    print(f"已应用审定修改到 {len(items)} 条")


if __name__ == "__main__":
    main()
