# agent.py
import os
import time
import json
from dotenv import load_dotenv
from newsapi import NewsApiClient
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from typing import List, TypedDict

load_dotenv()

news_api_key = os.getenv("NEWS_API_KEY")
newsapi = NewsApiClient(api_key=news_api_key)

class SupplierRiskReport(TypedDict):
    supplier: str
    score: int
    reasoning: str
    risk_factors: List[str]

def fetch_supplier_news(supplier_name: str) -> list[dict]:
    """Fetches news articles for a given supplier and returns a clean list of dictionaries containing only the title and description."""
    try:
        response = newsapi.get_everything(
            q=supplier_name,
            language='en',
            sort_by='relevancy',
            page_size=5
        )
        if response.get('status') == 'ok':
            articles = response.get('articles', [])
            clean_list = [
                {
                    'title': article.get('title'),
                    'description': article.get('description'),
                }
                for article in articles
            ]
            return clean_list
        else:
            print(f"Error: {response.get('message')}")
            return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def score_supplier_risk(supplier_name: str) -> dict:
    articles = fetch_supplier_news(supplier_name)
    articles_text = "\n\n".join(
        [f"Title: {a.get('title')}\nDescription: {a.get('description')}" for a in articles]
    )
    
    prompt = ChatPromptTemplate.from_template(
     """You are a Supply Chain Risk Analyst specialising in the automotive industry.

    You have been given {num_articles} recent news articles about the supplier "{supplier_name}".

    Articles:
    {articles_text}

    Based on these articles, evaluate the supplier's risk profile and return a JSON object with exactly these keys:
    - "supplier": the supplier name
    - "score": an integer from 1 to 10 where 1 is no risk and 10 is critical risk
    - "reasoning": one sentence explaining the score
    - "risk_factors": a list of strings, each describing one specific risk identified

    Return JSON only. No explanation, no markdown, no code blocks."""
    )
    
    base_llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)

    structured_llm = base_llm.with_structured_output(SupplierRiskReport)

    chain = prompt | structured_llm

    result = chain.invoke({
        "supplier_name": supplier_name,
        "num_articles": len(articles),
        "articles_text": articles_text
    })

    return result

def build_risk_report(all_reports: list[dict]):
    """
    Sorts risk reports, extracts high-risk suppliers for an alert section,
    and returns the full report in markdown.
    """
    sorted_reports = sorted(all_reports, key=lambda x: x['score'], reverse=True)
    high_risk_list = [r for r in sorted_reports if r['score'] >= 5]
    
    report_lines = []
    report_lines.append("# Supplier Risk Report — June 2026\n")
    
    if high_risk_list:
        report_lines.append("## ⚠️ HIGH RISK SUPPLIERS (Action Required)")
        for supplier in high_risk_list:
            report_lines.append(f"- **{supplier['supplier']}**: Score {supplier['score']} - {supplier['reasoning']}")
        report_lines.append("\n---\n")

    report_lines.append("## All Supplier Assessments")
    report_lines.append("| Supplier | Risk Score | Risk Factors | Reasoning |")
    report_lines.append("| :--- | :--- | :--- | :--- |")
    
    for report in sorted_reports:
        factors_str = ", ".join(report['risk_factors'])
        report_lines.append(f"| {report['supplier']} | {report['score']} | {factors_str} | {report['reasoning']} |")

    return "\n".join(report_lines)

def flag_high_risk(reports: list[dict]) -> list[dict]:
    return [r for r in reports if r['score'] >= 7]

def main():
    suppliers = ["Bosch", "Aptiv", "Magna International", "Samsung SDI", "BASF"]
    all_reports = []

    for supplier in suppliers:
        report = score_supplier_risk(supplier)
        all_reports.append(report)
        time.sleep(2)

    flag_high_risk(all_reports)
    print(build_risk_report(all_reports))

if __name__ == "__main__":
    main()