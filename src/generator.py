"""Grounded deterministic response generation with an optional API hook."""

from __future__ import annotations

import os
import json
from urllib import request

from .retriever import Evidence


def generate_reply(text: str, intent: str, evidence: list[Evidence]) -> tuple[str, str]:
    """Return a practical fallback reply and its generation mode."""
    if os.getenv("OPENAI_API_KEY"):
        try:
            prompt = (
                "Draft one concise, professional Amazon customer-support reply. "
                "Use only the customer message and historical evidence below. "
                "Do not claim actions were taken or invent order details.\n\n"
                f"Intent: {intent}\nCustomer: {text}\nEvidence:\n"
                + "\n".join(item.amazonhelp_response for item in evidence)
            )
            payload = json.dumps({
                "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
                "max_tokens": 160,
            }).encode("utf-8")
            api_request = request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=payload,
                headers={
                    "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with request.urlopen(api_request, timeout=20) as response:
                body = json.loads(response.read().decode("utf-8"))
            reply = body["choices"][0]["message"]["content"].strip()
            if reply:
                return reply, "llm_api"
        except Exception:
            pass
        mode = "deterministic_fallback_after_api_error"
    else:
        mode = "deterministic_fallback"

    if intent == "Other/Unclear/non-substantive":
        return "Please share the order or product details and describe what you need help with.", mode
    if intent == "Delivery and order fulfillment":
        return "I’m sorry your delivery is unclear. Please share the order number and the latest tracking status so the delivery can be checked.", mode
    if intent == "Returns, refunds, and charges":
        return "Please share the order number and explain whether you need a return, refund, or charge review. Do not include full payment details.", mode
    if intent == "Account access and security":
        return "This may involve account security. Please avoid posting sensitive information and continue through Amazon’s secure support channel.", mode
    if intent == "Customer service escalation and feedback":
        return "I’m sorry this has not been resolved. Please provide the relevant order or case details through a private support channel so it can be reviewed.", mode
    if intent == "Product condition, item accuracy, and seller issues":
        return "Please share the order number and describe the item problem. Photos and return options can be reviewed through the secure order-support flow.", mode
    if intent == "Digital products, devices, and apps":
        return "Please share the device or app name, the exact error, and the steps that cause it so the technical issue can be narrowed down.", mode
    return "Please share the product or order details and the price or availability issue you are seeing.", mode