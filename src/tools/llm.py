import json, os, random, traceback
from openai import OpenAI
from src.config import settings
from src.tools.logger import info, error


# ============================================================
# System prompts
# ============================================================

_SYSTEM_PROMPTS = {
    "insight": (
        "You are a Customer Insight Agent. Analyze product reviews and extract structured insights.\n\n"
        "Rules:\n"
        "- Identify pain points (negative feedback, complaints, missing features)\n"
        "- Identify advantages (positive feedback, strengths)\n"
        "- Identify customer segments implied by the reviews\n"
        "- Output ONLY valid JSON matching this schema (no markdown, no commentary):\n"
        '{\n'
        '  "pain_points": ["<array of strings>"],\n'
        '  "advantages": ["<array of strings>"],\n'
        '  "customer_segments": ["<array of strings>"],\n'
        '  "confidence_score": <0.0-1.0>\n'
        '}'
    ),
    "marketing": (
        "You are a Marketing Agent. Convert structured customer insights into marketing-ready content.\n\n"
        "Rules:\n"
        "- Use ONLY the provided insight data \u2014 do not invent new pain points\n"
        "- Generate campaign ideas addressing the pain points and highlighting advantages\n"
        "- Target the identified customer segments\n"
        "- Output ONLY valid JSON matching this schema (no markdown, no commentary):\n"
        '{\n'
        '  "campaign_suggestions": ["<array of campaign idea strings>"],\n'
        '  "target_audience": ["<array of segment strings>"],\n'
        '  "key_messaging": ["<array of key message strings>"],\n'
        '  "confidence_score": <0.0-1.0>\n'
        '}'
    ),
    "qa": (
        "You are a QA Evaluation Agent. Evaluate the quality of marketing content based on the original insight.\n\n"
        "Scoring criteria:\n"
        "- Accuracy (0-100): Does marketing accurately reflect the insight?\n"
        "- Score 80+ to approve; below 80 requires improvement\n"
        "- List specific issues if any\n"
        "- Final decision must be APPROVED or REJECTED\n"
        "- Output ONLY valid JSON matching this schema (no markdown, no commentary):\n"
        '{\n'
        '  "overall_score": <0-100>,\n'
        '  "decision": "APPROVED" or "REJECTED",\n'
        '  "issues": ["<array of issue strings>"],\n'
        '  "feedback": "<string>"\n'
        '}'
    ),
}


# ============================================================
# OpenAI-compatible API (covers DeepSeek + ZhipuAI)
# ============================================================

def _call_via_openai(agent_type: str, user_content: str, api_key: str, base_url: str, model: str) -> dict:
    client = OpenAI(api_key=api_key, base_url=base_url)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPTS[agent_type]},
            {"role": "user", "content": user_content},
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
        max_tokens=2048,
    )
    raw = resp.choices[0].message.content
    return json.loads(raw)


# ============================================================
# Mock backend (zero-dependency fallback)
# ============================================================

def _call_mock(agent_type: str, prompt_data: dict) -> dict:
    info("LLM", "Using mock backend")
    if agent_type == "insight":
        return _mock_insight(prompt_data)
    elif agent_type == "marketing":
        return _mock_marketing(prompt_data)
    elif agent_type == "qa":
        return _mock_qa(prompt_data)
    raise ValueError(f"Unknown agent type: {agent_type}")


def _mock_insight(prompt: dict) -> dict:
    reviews = prompt.get("reviews", [])
    pain, adv = [], []
    for r in reviews:
        lower = r.lower()
        is_pain = any(w in lower for w in [
            "bad", "terrible", "hate", "slow", "expensive", "issue", "bug",
            "crash", "crashing", "missing", "broken", "useless", "frustrating",
            "fail", "failed", "error", "worse", "unusable", "buggy",
            "horrible", "pain", "difficult", "confusing", "disappointed",
        ])
        is_adv = any(w in lower for w in [
            "good", "great", "love", "excellent", "amazing", "fast", "useful",
            "responsive", "helpful", "intuitive", "collaboration", "easy",
            "best", "perfect", "smooth", "beautiful", "reliable", "wonderful",
        ])
        if is_pain and not is_adv:
            pain.append(r)
        elif is_adv and not is_pain:
            adv.append(r)
        else:
            pain.append(r)
    total = len(reviews) or 1
    conf = max(0.3, min(0.95, round((len(pain) + len(adv)) / total * 0.9, 2)))
    return {
        "pain_points": pain[:3] or ["No significant pain points identified"],
        "advantages": adv[:3] or ["No notable advantages identified"],
        "customer_segments": ["new_users", "power_users", "enterprise"],
        "confidence_score": conf,
    }


def _mock_marketing(prompt: dict) -> dict:
    insight = prompt.get("insight", {})
    pain = insight.get("pain_points", [])
    adv = insight.get("advantages", [])
    segs = insight.get("customer_segments", [])
    campaigns = []
    if pain:
        campaigns.append(f"Address: {pain[0]}")
    if adv:
        campaigns.append(f"Highlight: {adv[0]}")
    if not campaigns:
        campaigns.append("General awareness campaign")
    return {
        "campaign_suggestions": campaigns,
        "target_audience": segs,
        "key_messaging": [
            f"Solve {pain[0][:60]}" if pain else "Quality product",
            f"Best for {segs[0]}" if segs else "Broad appeal",
        ],
        "confidence_score": round(random.uniform(0.5, 1.0), 2),
    }


def _mock_qa(prompt: dict) -> dict:
    score = round(random.uniform(50, 100), 1)
    issues = []
    insight_conf = prompt.get("insight", {}).get("confidence_score", 1)
    mkt_conf = prompt.get("marketing", {}).get("confidence_score", 1)
    if insight_conf < 0.5:
        issues.append("Low insight confidence score")
    if mkt_conf < 0.5:
        issues.append("Low marketing confidence score")
    if score < 60:
        issues.append("Overall quality below threshold")
    if not issues:
        issues.append("No critical issues found")
    decision = "APPROVED" if score >= 80 else "REJECTED"
    return {
        "overall_score": score,
        "decision": decision,
        "issues": issues,
        "feedback": f"QA score: {score}. {'Approved.' if decision == 'APPROVED' else 'Needs improvement.'}",
    }


# ============================================================
# Prompt formatting
# ============================================================

def _format_prompt(agent_type: str, data: dict) -> str:
    if agent_type == "insight":
        lines = ["Please analyze the following product reviews and extract insights."]
        reviews = data.get("reviews", [])
        if reviews:
            lines.append("\nReviews:")
            for i, r in enumerate(reviews, 1):
                lines.append(f"  {i}. {r}")
        pi = data.get("product_info")
        if pi:
            lines.append(f"\nProduct Info: {json.dumps(pi, ensure_ascii=False)}")
        bb = data.get("business_brief")
        if bb:
            lines.append(f"\nBusiness Brief (use as context):\n{json.dumps(bb, indent=2, ensure_ascii=False)}")
        return "\n".join(lines)
    elif agent_type == "marketing":
        lines = ["Based on this customer insight, generate marketing content:\n"]
        lines.append(json.dumps(data.get("insight", {}), indent=2, ensure_ascii=False))
        bb = data.get("business_brief")
        if bb:
            lines.append(f"\nBusiness Brief (use as context):\n{json.dumps(bb, indent=2, ensure_ascii=False)}")
        return "\n".join(lines)
    elif agent_type == "qa":
        lines = ["Evaluate this marketing output against the original insight:\n"]
        lines.append(f"Insight:\n{json.dumps(data.get('insight', {}), indent=2, ensure_ascii=False)}")
        lines.append(f"\nMarketing:\n{json.dumps(data.get('marketing', {}), indent=2, ensure_ascii=False)}")
        bb = data.get("business_brief")
        if bb:
            lines.append(f"\nBusiness Brief (use as context for evaluation):\n{json.dumps(bb, indent=2, ensure_ascii=False)}")
        return "\n".join(lines)
    return json.dumps(data, ensure_ascii=False)


# ============================================================
# Public API
# ============================================================

_REAL_BACKENDS = {
    "deepseek": {
        "api_key_attr": "deepseek_api_key",
        "base_url": "https://api.deepseek.com",
        "model_attr": "deepseek_model",
    },
    "zhipuai": {
        "api_key_attr": "zhipuai_api_key",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "model_attr": "zhipuai_model",
    },
}


def call(agent_type: str, prompt_data: dict) -> dict:
    backend = settings.llm_backend
    info("LLM", f"Backend={backend}, agent={agent_type}")

    if backend == "mock":
        return _call_mock(agent_type, prompt_data)

    if backend not in _REAL_BACKENDS:
        error("LLM", f"Unknown backend '{backend}', falling back to mock")
        return _call_mock(agent_type, prompt_data)

    cfg = _REAL_BACKENDS[backend]
    api_key = getattr(settings, cfg["api_key_attr"])
    if not api_key:
        error("LLM", f"{backend} API key not set, falling back to mock")
        return _call_mock(agent_type, prompt_data)

    try:
        user_content = _format_prompt(agent_type, prompt_data)
        return _call_via_openai(
            agent_type, user_content,
            api_key=api_key,
            base_url=cfg["base_url"],
            model=getattr(settings, cfg["model_attr"]),
        )
    except Exception as e:
        error("LLM", f"{backend} call failed: {e}")
        error("LLM", traceback.format_exc())
        return _call_mock(agent_type, prompt_data)
