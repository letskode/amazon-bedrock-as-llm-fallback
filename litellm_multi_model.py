from litellm import completion
import os 
from pydantic import BaseModel

#MODEL =   "bedrock/us.meta.llama4-maverick-17b-instruct-v1:0"
MODEL =    "gpt-5-nano" 
#MODEL =   "bedrock/us.meta.llama3-3-70b-instruct-v1:0"
#MODEL = "bedrock/us.anthropic.claude-3-7-sonnet-20250219-v1:0"

# Auto-load .env if present (no shell export needed)
try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except Exception:
    pass


class CalendarEvent(BaseModel):
  name: str
  date: str
  participants: list[str]

class EventsList(BaseModel):
    events: list[CalendarEvent]

response = completion(
  model=MODEL, # specify invoke via `bedrock/invoke/anthropic.claude-3-7-sonnet-20250219-v1:0`
  response_format=EventsList,
  messages=[
    {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
    {"role": "user", "content": "Who won the world series in 2020?"}
  ],
)
print()
print(response.choices[0].message.content)

