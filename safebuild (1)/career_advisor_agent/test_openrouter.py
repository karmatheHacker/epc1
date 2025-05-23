from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)

completion = client.chat.completions.create(
  extra_headers={
    "HTTP-Referer": "https://career-advisor-agent.com",  # Optional. Site URL for rankings on openrouter.ai.
    "X-Title": "Career Advisor Agent",  # Optional. Site title for rankings on openrouter.ai.
  },
  model="openai/gpt-4o-mini",
  messages=[
    {
      "role": "user",
      "content": "What are the top 3 skills for software engineers?"
    }
  ]
)
print(completion.choices[0].message.content) 