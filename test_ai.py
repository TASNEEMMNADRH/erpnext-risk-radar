import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=300,
    messages=[
        {"role": "user", "content": "Hello Claude, are you working?"}
    ]
)

print(response.content[0].text)
