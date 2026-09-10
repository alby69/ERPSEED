"""
CRM Services module.
"""


def calculate_lead_score(lead_data):
    """
    Calculates lead score based on lead data fields:
    - Email presence: +10
    - Company presence: +20
    - Web source (website/web): +30
    """
    score = 0
    if not lead_data:
        return score

    # Dict or object attribute access
    email = lead_data.get("email") if isinstance(lead_data, dict) else getattr(lead_data, "email", None)
    company = lead_data.get("company") if isinstance(lead_data, dict) else getattr(lead_data, "company", None)
    source = lead_data.get("source") if isinstance(lead_data, dict) else getattr(lead_data, "source", None)

    if email:
        score += 10
    if company:
        score += 20
    if source and str(source).lower() in ["website", "web", "online"]:
        score += 30

    return score
