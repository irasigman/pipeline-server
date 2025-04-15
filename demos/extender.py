import asyncio
import os
from typing import List

import logfire
import nest_asyncio
from dotenv import load_dotenv
from pydantic import BaseModel, create_model, Field
from pydantic_ai import Agent, Tool
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from openai import AsyncOpenAI

from app.model import data_model
from app.model.data_model import DataModel
from data.web.scrape import WebScrape

nest_asyncio.apply()

log = logfire.configure()

client = OpenAIProvider(
    openai_client = AsyncOpenAI(_strict_response_validation=False,
                                api_key="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"
                                # api_key="xai-KJ1PfhYMmiFMLm5C6uY9TMfwcl1vvDVFkjGGeNU47ZnfH59LDE3hh34oTt0sA4GuqSSC6Fwqr7cd9wCJ",
                                # base_url="https://api.x.ai/v1",
                                )
)

model = OpenAIModel(model_name="gpt-4o-mini", provider=client)

# Input dictionary defining the model fields with descriptions
# input_dict = {
#     "title": (str, Field(..., description="The title of the news article.")),
#     "ai": (bool, Field(..., description="Is the article likely to be about AI or ML?")),
#     "category": (str, Field(..., description="The category of the news article, e.g., TECH, BUSINESS, CULTURE, HEALTH")),
#     "votes": (int, Field(..., description="The number of votes the news article has received."))
# }


async def scrape_content(_url: str) -> str:
    """Fetch the content of a web page in Markdown format."""
    webscrape = WebScrape()
    markdown = webscrape.retrieve_page_markdown(_url)
    return markdown

scrape_tool = Tool(scrape_content)



async def assistant(_query: str, _data_model: DataModel):
    """
    This function is used to get a response from the assistant.
    :param _data_model:
    :param _query:
    :return:
    """
    print(_query)
    # transform DataModel to a pydantic model
    # Create a new model dynamically based on the DataModel fields
    # Use `type_` for Pydantic v1 compatibility
    dynamic_model = data_model.convert_to_dynamic_model(_data_model, as_list=True)
    # Iterate over all fields and concatenate their descriptions
    field_descriptions = data_model.get_field_descriptions(dynamic_model)
    _system_prompt = "You are a web search assistant with page reading capabilities. You will assist in completing a data model. Descriptions for each field are provided." + field_descriptions
    agent = Agent(
        model=model,
        instrument=True,
        system_prompt=_system_prompt,
        result_type=dynamic_model,
        tools=[scrape_tool],
    )
    response = agent.run_sync(_query)
    return response

if __name__ == '__main__':

    async def main():
        query = 'Provide the top 10 articles on https://news.ycombinator.com/'
        res = await assistant(query)
        print(res)

    asyncio.run(main())