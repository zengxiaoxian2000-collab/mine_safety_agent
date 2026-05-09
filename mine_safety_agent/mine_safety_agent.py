import time
import json

# ==========================================
# 模拟核心工具库：规程检索与电气计算 (Tools)
# ==========================================
def tool_search_safety_rules(keyword):
    """
    模拟 RAG 知识库检索：针对注安考试及《煤矿安全规程》
    """
    db = {
        "带式输送机": "《煤矿安全规程》第三百七十三条：必须装设防滑、防跑偏、防烟雾、超温洒水装置。",
        "供电系统": "《煤矿安全规程》：主要通风机、提升人员的立井提升机等重要负荷，必须具备双回路供电。",
        "电缆压降": "工业通用标准：正常运行工况下，末端设备电压偏移不应超过额定电压的 ±5%。"
    }
    return db.get(keyword, "未找到特定条款，请参考通用安全生产标准执行。")

def tool_voltage_drop_calc(power_kw, distance_m, voltage_v=380):
    """
    模拟电气计算 Agent 调用：验证 1200米、500kW 等工况下的压降合规性
    """
    # 模拟简化计算逻辑 (Delta U)
    drop_percentage = (power_kw * distance_m) / 100000  # 仅作逻辑演示
    is_safe = drop_percentage <= 5
    return {"drop_p": f"{drop_percentage:.2f}%", "is_safe": is_safe}

# ==========================================
# 核心智能体定义 (Agents)
# ==========================================

def agent_data_parser(input_text):
    """
    Agent 1: 现场数据解析专家
    任务：从口语化描述中提取设备对象与电气参数
    """
    print("▶ [Agent 1] 正在提取现场关键信息...")
    # 模拟 LLM 提取结果
    return {
        "target": "带式输送机",
        "params": {"power": 500, "distance": 1200},
        "issue": "防滑保护失灵，且电缆末端电压似乎不稳"
    }

def agent_compliance_expert(data):
    """
    Agent 2: 合规审查专家
    任务：匹配法律法规与计算校验
    """
    print("▶ [Agent 2] 正在调取规程知识库并进行电气校核...")
    target = data["target"]
    rules = tool_search_safety_rules(target)
    
    # 联动电气计算工具
    p, d = data["params"]["power"], data["params"]["distance"]
    calc_result = tool_voltage_drop_calc(p, d)
    
    data["matched_rules"] = rules
    data["calc_result"] = calc_result
    return data

def agent_decision_maker(context):
    """
    Agent 3: 首席安全决策官 (CoT 思维链推理)
    任务：结合知行合一理念，输出最终整改指令
    """
    print("▶ [Agent 3] 启动思维链推理，生成闭环报告...")
    time.sleep(1)
    
    calc = context["calc_result"]
    safety_status = "❌ 违规" if not calc["is_safe"] else "✅ 合规"
    
    report = f"""
==================================================
        智慧矿山安全审计报告 (AI Agent 协作版)
==================================================
【核查对象】 {context['target']}
【异常描述】 {context['issue']}

【合规依据】
{context['matched_rules']}

【电气校核结果】
- 预估压降值：{calc['drop_p']} (限值 5%)
- 状态判定：{safety_status}

【思维链推理 (Reasoning)】
1. 现场报告显示防滑保护传感器失效，直接违反《规程》第373条硬性要求。
2. 结合 1200米 远距离供电参数，计算得出末端压降超标，可能导致控制回路动作不可靠。
3. 结论：安全隐患等级为“高”，必须立即停机检查保护回路与供电质量。

【闭环整改指令 (知行合一)】
1. 立即停止皮带机运行，排查防滑保护传感器接线。
2. 针对压降问题，建议校核电缆截面积是否满足 500kW 负荷长距离运行要求。
3. 更新安全记录台账，确保护理记录与法规要求对齐。
==================================================
"""
    return report

# ==========================================
# 工作流编排 (Workflow)
# ==========================================
def run_safety_audit(text):
    raw_info = agent_data_parser(text)
    full_context = agent_compliance_expert(raw_info)
    final_report = agent_decision_maker(full_context)
    print(final_report)

if __name__ == "__main__":
    # 测试输入
    user_input = "报告，1200米外那个500kW的皮带机防滑保护灯不亮了，而且电压好像掉得厉害"
    run_safety_audit(user_input)