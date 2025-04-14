import asyncio
from typing import List

import logfire
import nest_asyncio
from dotenv import load_dotenv
from pydantic import BaseModel, create_model
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from openai import AsyncOpenAI
from data.web.scrape import WebScrape

nest_asyncio.apply()

log = logfire.configure()

load_dotenv("../.env")

client = OpenAIProvider(
    openai_client = AsyncOpenAI(_strict_response_validation=False,
                                # api_key="xai-KJ1PfhYMmiFMLm5C6uY9TMfwcl1vvDVFkjGGeNU47ZnfH59LDE3hh34oTt0sA4GuqSSC6Fwqr7cd9wCJ",
                                # base_url="https://api.x.ai/v1",
                                )
)

model = OpenAIModel(model_name="gpt-4o-mini", provider=client)

# Input dictionary defining the model fields
input_dict = {
    "title": (str, ...),  # Field type and required
    "category": (str, ...),
    "votes": (int, ...)
}

# Dynamically create the model
DynamicNewsModel = create_model("DynamicNewsModel", **input_dict)


class NewsList(BaseModel):
    items: List[DynamicNewsModel]

agent = Agent(
    model=model,
    system_prompt="You are a web search assistant with page reading capabilities, category is either TECH or CULTURE",
    instrument=True,
    result_type=NewsList
)

@agent.tool_plain
def scrape_content(_url: str) -> str:
    """Fetch the content of a web page in Markdown format."""
    webscrape = WebScrape()
    markdown = webscrape.retrieve_page_markdown(_url)
    return markdown

async def assistant(_query: str):
    """
    This function is used to get a response from the assistant.
    :param _query:
    :return:
    """
    response = agent.run_sync(_query)
    return response

if __name__ == '__main__':

    async def main():
        query = 'Provide the top 10 articles on https://news.ycombinator.com/'
        res = await assistant(query)
        print(res)

    asyncio.run(main())