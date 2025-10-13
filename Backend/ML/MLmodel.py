import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file (optional but recommended)
load_dotenv()

# ✅ Use environment variable instead of hardcoding the key

client = OpenAI(api_key="yourAPIKEy")
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
    max_completion_tokens=500,
    
)

    return response.choices[0].message.content.strip()