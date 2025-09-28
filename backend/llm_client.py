from config import openai_client

def generate_project_name(messages: list[dict]) -> str:
    convo = "\n".join([f"{m['role']}: {m['content']}" for m in messages])

    prompt = f"""
    You are a helpful assistant. Based on this conversation, generate a short, clear, descriptive project name.
    Keep it under 6 words, title-style.

    Conversation:
    {convo}
    """

    response = openai_client.chat.completions.create(
        model="gpt-4-turbo",  # or whichever model you’re using
        messages=[{"role": "user", "content": prompt}],
        max_tokens=20,
    )

    content = response.choices[0].message.content
    name = content.strip() if content is not None else None
    return name or "New Conversation"
