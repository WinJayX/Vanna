import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from vanna.base import VannaBase
from vanna.chromadb import ChromaDB_VectorStore
from vanna.openai import OpenAI_Chat
from vanna.flask import VannaFlaskApp

from openai import OpenAI
import httpx

# Ollama 兼容 Client（传入假的 api_key，但移除 Authorization 头）
transport = httpx.HTTPTransport(retries=2)
http_client = httpx.Client(
    transport=transport,
    headers={},  # ⚠️ 明确无 Authorization 头
    timeout=httpx.Timeout(300.0)  # 明确设定 300 秒超时
)

openai_client = OpenAI(
    base_url="https://ollama.litsoft.com.cn/v1",
    api_key="ollama-no-auth",  # ✅ 占位符，防止报错
    http_client=http_client
)

# 自定义 Vanna 组合
class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self):
        ChromaDB_VectorStore.__init__(self)
        OpenAI_Chat.__init__(self, client=openai_client, config={
            "model": "qwen3:32b",
            "temperature": 0.0,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个严谨的且专业的SQL 查询生成助手。；负责生成准确的查询语句。你不会考虑用户之前的问题或任何历史上下文。每个问题都是全新的独立请求。"
                }
            ]
        })

# --------------------- ✅ 创建 Vanna 实例 ---------------------
vn = MyVanna()

# --------------------- ✅ 连接 MySQL ---------------------
vn.connect_to_mysql(
    host="10.17.0.20",
    dbname="cost_bi",
    user="root",
    password="Lit-Password",
    port=3306
)

# 可选训练（基础文档）
vn.train(documentation="请注意，在我们公司一般将1作为是，0作为否。")

# --------------------- ✅ 加入你自定义的训练数据 ---------------------
training_data = [
    {
        "question": "统计收入分析的7个核心经营指标，包括不含税收入、税金、直接成本、间接费用、毛利率、利润金额、利润率。",
        "sql": """
            select ifnull(sum(excluding_tax_income), 0) as excludingTaxIncome,
                   ifnull(sum(taxes), 0) as taxes,
                   ifnull(sum(subquotient_cost + special_business_reimbursement + capacity_payroll + bonus_tax + compensation_back_social_security), 0)  directCostAmount,
                   ifnull(sum(special_business_reimbursement + cp + no_capacity_payroll + recruitment_cost), 0)  indirectExpensesAmount,
                   (ifnull(sum(excluding_tax_income), 0) - sum(subquotient_cost + special_business_reimbursement + capacity_payroll + bonus_tax + compensation_back_social_security)) / ifnull(sum(excluding_tax_income), 0) as grossProfitRate,
                   ifnull(sum(excluding_tax_income), 0) - ifnull(sum(taxes), 0) - sum(subquotient_cost + special_business_reimbursement + capacity_payroll + bonus_tax + compensation_back_social_security) - sum(special_business_reimbursement + cp + no_capacity_payroll + recruitment_cost) as profitAmount,
                   (ifnull(sum(excluding_tax_income), 0) - ifnull(sum(taxes), 0) - sum(subquotient_cost + special_business_reimbursement + capacity_payroll + bonus_tax + compensation_back_social_security) - sum(special_business_reimbursement + cp + no_capacity_payroll + recruitment_cost)) / ifnull(sum(excluding_tax_income), 0) as profitRate
            from bi_dm_project_income
            where 1 = 1
            [AND dept_id IN ( ... )]
            [AND (year * 100 + month) IN ( ... )]
            [AND ( ... )]
        """
    },
    {
        "question": "统计各部门每月的收入总额。",
        "sql": """
            select year, month, quarter, dept_code code, dept_name `key`, sum(excluding_tax_income) `value`
            from bi_dm_project_income
            where 1 = 1
            [AND dept_id IN ( ... )]
            [AND (year * 100 + month) IN ( ... )]
            [AND ( ... )]
            group by year, month, dept_name
            order by year desc, month, dept_name
        """
    },
    {
        "question": "统计每月的利润总额。",
        "sql": """
            select year, month, quarter, dept_code code, dept_name `key`, sum(profit_month) `value`
            from bi_dm_project_income
            where 1 = 1
            [AND dept_id IN ( ... )]
            [AND (year * 100 + month) IN ( ... )]
            [AND ( ... )]
            group by year, month
            order by year desc, month
        """
    },
    {
        "question": "统计每月的累计收入金额。",
        "sql": """
            select year, month, quarter, sum(excluding_tax_income) `value`
            from bi_dm_project_income
            where 1 = 1
            [AND dept_id IN ( ... )]
            [AND (year * 100 + month) IN ( ... )]
            [AND ( ... )]
            group by year, month
            order by year, month
        """
    },
    {
        "question": "统计每月的累计利润金额（收入-税金-成本-费用）。",
        "sql": """
            select year, month, quarter, sum(excluding_tax_income) - sum(taxes) - sum(subquotient_cost + special_business_reimbursement + capacity_payroll + bonus_tax + compensation_back_social_security) - sum(special_business_reimbursement + cp + no_capacity_payroll + recruitment_cost) `value`
            from bi_dm_project_income
            where 1 = 1
            [AND dept_id IN ( ... )]
            [AND (year * 100 + month) IN ( ... )]
            [AND ( ... )]
            group by year, month
            order by year, month
        """
    },
    {
        "question": "统计各部门的收入总额。",
        "sql": """
            select dept_code code, dept_name `key`, sum(excluding_tax_income) `value`
            from bi_dm_project_income
            where 1 = 1
            [AND dept_id IN ( ... )]
            [AND (year * 100 + month) IN ( ... )]
            [AND ( ... )]
            group by dept_name
            order by value desc
        """
    },
    {
        "question": "统计各部门的利润总额。",
        "sql": """
            select dept_code code, dept_name `key`, sum(profit_month) `value`
            from bi_dm_project_income
            where 1 = 1
            [AND dept_id IN ( ... )]
            [AND (year * 100 + month) IN ( ... )]
            [AND ( ... )]
            group by dept_name
            order by value desc
        """
    },
    {
        "question": "统计不同项目类型的收入总额。",
        "sql": """
            select project_type code, project_type `key`, sum(excluding_tax_income) `value`
            from bi_dm_project_income
            where 1 = 1
            [AND dept_id IN ( ... )]
            [AND (year * 100 + month) IN ( ... )]
            [AND ( ... )]
            group by project_type
            order by value desc
        """
    },
    {
        "question": "统计各客户的收入总额。",
        "sql": """
            select client_name code, client_name `key`, sum(excluding_tax_income) `value`
            from bi_dm_project_income
            where 1 = 1
            [AND dept_id IN ( ... )]
            [AND (year * 100 + month) IN ( ... )]
            [AND ( ... )]
            group by client_name
            order by value desc
        """
    },
    {
        "question": "统计各项目的收入总额。",
        "sql": """
            select project_no code, project_name `key`, sum(excluding_tax_income) `value`
            from bi_dm_project_income
            where 1 = 1
            [AND dept_id IN ( ... )]
            [AND (year * 100 + month) IN ( ... )]
            [AND ( ... )]
            group by project_name
            order by value desc
        """
    },
    {
        "question": "统计各项目的利润总额。",
        "sql": """
            select project_no code, project_name `key`, sum(profit_month) `value`
            from bi_dm_project_income
            where 1 = 1
            [AND dept_id IN ( ... )]
            [AND (year * 100 + month) IN ( ... )]
            [AND ( ... )]
            group by project_name
            order by value desc
        """
    },
    {
        "question": "统计各客户的利润总额（收入-税金-成本-费用）。",
        "sql": """
            select client_name code, client_name `key`, ifnull(sum(excluding_tax_income), 0) - ifnull(sum(taxes), 0) - sum(subquotient_cost + special_business_reimbursement + capacity_payroll + bonus_tax + compensation_back_social_security) - sum(special_business_reimbursement + cp + no_capacity_payroll + recruitment_cost) `value`
            from bi_dm_project_income
            where 1 = 1
            [AND dept_id IN ( ... )]
            [AND (year * 100 + month) IN ( ... )]
            [AND ( ... )]
            group by client_name
            order by value desc
        """
    },
    {
        "question": "统计每月的收入、毛利率、利润金额。",
        "sql": """
            select year, month, quarter, ifnull(sum(excluding_tax_income), 0) as excludingTaxIncome,
                   ifnull(ROUND((ifnull(sum(excluding_tax_income), 0) - sum(subquotient_cost + special_business_reimbursement + capacity_payroll + bonus_tax + compensation_back_social_security)) / ifnull(sum(excluding_tax_income), 0), 2), 0) as grossProfitRate,
                   ifnull(sum(excluding_tax_income), 0) - ifnull(sum(taxes), 0) - sum(subquotient_cost + special_business_reimbursement + capacity_payroll + bonus_tax + compensation_back_social_security) - sum(special_business_reimbursement + cp + no_capacity_payroll + recruitment_cost) as profitAmount
            from bi_dm_project_income
            where 1 = 1
            [AND dept_id IN ( ... )]
            [AND (year * 100 + month) IN ( ... )]
            [AND ( ... )]
            group by year, month
            order by year, month
        """
    },
    {
        "question": "导出收入分析的所有原始数据。",
        "sql": """
            select *
            from bi_dm_project_income
            where 1 = 1
            [AND dept_id IN ( ... )]
            [AND (year * 100 + month) IN ( ... )]
            [AND ( ... )]
            order by year, month
        """
    },
    {
        "question": "统计每月的总成本金额。",
        "sql": """
            select year, month, quarter, dept_code code, dept_name `key`, sum(total_cost) `value`
            from bi_dm_project_income
            where 1 = 1
            [AND dept_id IN ( ... )]
            [AND (year * 100 + month) IN ( ... )]
            [AND ( ... )]
            group by year, month
            order by year desc, month
        """
    }
    # 👉 如有更多项，请继续补充在此处
]

for item in training_data:
    vn.train(question=item["question"], sql=item["sql"])

# --------------------- ✅ 训练完成 ---------------------

# --------------------- ✅ 启动 Flask Web 服务 ---------------------
flask_app = VannaFlaskApp(
    vn,
    debug=False,
    allow_llm_to_see_data=True,
    title="联和利泰SQL生成系统",
    subtitle="数据库问答系统"
).run(host='0.0.0.0', port=8084)

'''
//参数具体含义
    chart=True,
    csv_download=True,
    summarization=True,
    ask_results_correct=True,
    table=True,
    sql=True,
    show_training_data=True
auth：要使用的身份验证方法。
debug：控制是否显示调试控制台。
allow_llm_to_see_data：指示是否允许LLM查看数据。
logo：用户界面中显示的标志。默认为Vanna标志。
title：设置要在UI中显示的标题。
subtitle：设置要在UI中显示的副标题。
show_training_data：控制是否在UI中显示训练数据。
sql：控制是否在UI中显示SQL输入。
table：控制是否在UI中显示表格输出。
csv_download：指示是否允许将表格输出作为CSV文件下载。
chart：控制是否在UI中显示图表输出。
ask_results_correct：指示是否询问用户结果是否正确。
summarization：控制是否显示摘要。
'''

if __name__ == "__main__":
    flask_app.run(host='0.0.0.0', port=8084, debug=True)

