import random

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

client = OpenAIProvider(
    api_key="xai-KJ1PfhYMmiFMLm5C6uY9TMfwcl1vvDVFkjGGeNU47ZnfH59LDE3hh34oTt0sA4GuqSSC6Fwqr7cd9wCJ",
    base_url="https://api.x.ai/v1",
)

model = OpenAIModel(model_name="grok-3-latest", provider=client)
agent = Agent(model=model, system_prompt="You are a dice-roll assistant, tell me if I'm right or wrong", instrument=True)

@agent.tool_plain
def roll_die() -> str:
    """Roll a six-sided die and return the result."""
    return str(random.randint(1, 6))

async def assistant(query: str):
    """
    This function is used to get a response from the assistant.
    :param query:
    :return:
    """
    response = agent.run_sync(query)
    return response

