from openai import OpenAI

def categorize_expense(description: str, amount: float):
    prompt = f"""
   You are an expense categorization assistant.

    Categorize the following expense into one of these categories:
    [Food, Transportation, Utilities, Entertainment, Health, Shopping, Education, Bills, Other].

    Rules:
    - The description may be written in English, Filipino/Tagalog, or Cebuano/Bisaya.
    - Always classify based on the most common everyday meaning in the context of personal spending.
    - Do NOT return explanations, only the category name.
    - Use "Other" only if it truly does not fit into any of the listed categories.
    - If the description is vague but suggests a common category, choose that category.
    
    
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
    - "bayad" (if clearly about monthly obligations) → Bills
    - "if theres a word bayad"  → bills
    - "netflix subscription" → Entertainment
    - "sapatos" → Shopping
    - "movie ticket" → Entertainment

    ### Task:
    Description: "{description}"
    Amount: {amount}

    Answer with only the category.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a financial assistant that classifies expenses."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=20,
        temperature=0
    )

    return response.choices[0].message.content.strip()