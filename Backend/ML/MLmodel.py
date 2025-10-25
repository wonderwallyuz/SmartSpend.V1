
from openai import OpenAI

client = OpenAI(api_key="apui")
def categorize_expense(description: str, amount: float):
    prompt = f"""
You are an intelligent assistant that categorizes expenses.

Given an expense description and amount, provide the most suitable category name.  
If it doesn’t clearly fit an existing category, create a new one that best matches its purpose.

Guidelines:
- The description may be in English, Filipino/Tagalog, or Cebuano/Bisaya.
- Infer the category based on real-world context.
- Output only the category name (no explanation).
- Avoid vague terms like "Other" or "Misc".
- Keep category names short, natural, and consistent (e.g., "Food", "Drinks", "Transportation", "Bills", "Groceries", "Shopping", "Health", "Entertainment", "Education", "Savings", "Donations", "Rent", etc.).
- Be consistent across similar inputs.

### Task:
Description: "{description}"
Amount: {amount}

Category:
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