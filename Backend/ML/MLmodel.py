
from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY_HERE")
def categorize_expense(description: str, amount: float):
    prompt = f"""
        You are an intelligent expense categorization assistant.

Your task is to determine the most suitable expense category for a given description.
If the expense does not clearly fit into the common categories below, intelligently CREATE a new category name that best represents it.

Common categories include:
[Food, Transportation, Utilities, Entertainment, Health, Shopping, Education, Bills]

Rules:
- The description may be written in English, Filipino/Tagalog, or Cebuano/Bisaya.
- Always infer meaning based on the most likely real-world spending context.
- Do NOT output explanations — only the category name.
- NEVER output "Other".
- If a new category fits better than the ones above, create it (e.g., "Pet Care", "Travel", "Donations", "Maintenance", etc.).
- Be consistent — similar descriptions should yield the same category.

### Examples:
- "lapis" → Education
- "hotdog" → Food
- "pamasahe" → Transportation
- "pliti" (Cebuano for fare) → Transportation
- "kuryente" → Utilities
- "suga" (Cebuano for electricity/light) → Utilities
- "gamot" → Health
- "bayad sa tubig" → Bills
- "bayad sa kuryente" → Bills
- "bayad" (if referring to recurring obligations) → Bills
- "netflix subscription" → Entertainment
- "sapatos" → Shopping
- "movie ticket" → Entertainment
- "dog food" → Pet Care
- "airplane ticket" → Travel
- "church donation" → Donations

### Task:
Description: "{description}"
Amount: {amount}

Answer with only the category name.
"""

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
        {"role": "system", "content": "You are a financial assistant that classifies expenses."},
        {"role": "user", "content": prompt}
    ],
    max_completion_tokens=500
    
)

    return response.choices[0].message.content.strip()

def generate_smartspend_insights(expense_summary: dict):
    if expense_summary and any(expense_summary.values()):
        prompt = f"""
    You are SmartSpend AI — a friendly and practical personal finance assistant.

    Analyze the user's spending summary below and provide 4–5 short, encouraging insights.

    ### Spending Summary:
    {chr(10).join([f"{cat}: ₱{amt:.2f}" for cat, amt in expense_summary.items()])}

    Rules:
    - Write 1–2 sentence insights.
    - Encourage smarter spending in a positive tone.
    - No bullet points; separate each insight with newlines.
    - Avoid repeating categories unnecessarily.

    Example:
    You spent the most on Food — try planning meals to cut costs.
    Transportation costs decreased — great job!
    Bills are steady this month — consistency is key.
    Entertainment spending increased slightly — maybe review your subscriptions.
    Keep tracking your progress — small savings add up fast!
    """
    else:
        prompt = """
    You are SmartSpend AI — a friendly and practical personal finance assistant.

    The user hasn’t entered any spending data yet.

    Give 4–5 short, encouraging financial tips in a friendly tone. 
    Focus on general advice about budgeting, tracking expenses, saving, and financial habits.

    Example tips:
    Start by tracking even small daily expenses — awareness is the first step to control.
    Set a simple weekly budget goal and review it every Sunday.
    Try the 50/30/20 rule: 50% needs, 30% wants, 20% savings.
    Saving a small amount regularly builds strong money habits over time.
    Review your subscriptions monthly to avoid paying for unused services.
    """

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": "You are a financial assistant generating spending insights."},
            {"role": "user", "content": prompt}
        ],
        max_completion_tokens=1000
    )

    return response.choices[0].message.content.strip()