import asyncio
import agentops
from agentops.enums import EndState
import os
from dotenv import load_dotenv
from pathlib import Path

from crewai.flow.flow import Flow, listen, start, or_, and_
from litellm import completion
from crew import Day7
from pydantic import BaseModel
#from tools.custom_file_writer_tool import CustomFileWriterTool
from file_writer_crew import FileWriterCrew



root_dir = Path(__file__).parent.parent.parent  # This goes up to day7 directory
env_paths = [
    root_dir.parent / '.env',  # Try root directory first
    root_dir / '.env',         # Try day7 directory
    Path('.env')               # Try current directory
]

env_loaded = False
for env_path in env_paths:
    if env_path.exists():
        print(f"Found .env file at: {env_path.absolute()}")
        load_dotenv(env_path)
        env_loaded = True
        break

if not env_loaded:
    print("Warning: No .env file found in any of the expected locations")

class News(BaseModel):
    news: str = ""

class NewsFlow(Flow[News]):
    model = "gpt-4o-mini"
    model_4o = "gpt-4o"

    @start()
    def generate_news_topic(self):
        print("Starting flow")

        response = completion(
            model=self.model_4o,
            messages=[
                {
                    "role": "user",
                    "content": """Return a topic within the startup world that is trending.  
                    This should be 1 - 4 words.""",
                },
            ],
        )

        news_topic = response["choices"][0]["message"]["content"]

        print(f"News Topic: {news_topic}")

        return news_topic

    @listen(generate_news_topic)
    def generate_news(self, news_topic):
        print("Generating news with Crew")

        inputs = {
            'topic': news_topic
        }

        result = Day7().crew().kickoff(inputs=inputs)

        # get raw output then save to state
        output = result.raw
        self.state.news = output

        return output

    @listen(generate_news)
    def write_news(self):
        print("Saving news")

        news = self.state.news

        print(f"News: {news}")

        inputs = {
            'news': news
        }

        FileWriterCrew().crew().kickoff(inputs=inputs)

        print(f"File successfully written.")


    @listen(generate_news)
    def generate_best_news(self, input):
        print("Generating best news")
        
        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": f"Choose the most important news from the following and return it: {input}",
                },
            ],
        )

        important_news = response["choices"][0]["message"]["content"]
        return important_news
    
    @listen(and_(generate_news_topic, generate_news, write_news, generate_best_news))
    def logger(self, result):
        print(f"Logger: {result}")
        print("*" * 100)
        print("News Complete!")


async def run_flow():
    api_key = os.getenv("AGENTOPS_API_KEY")
    print(f"Current working directory: {os.getcwd()}")
    print(f"AgentOps API Key found: {api_key is not None}")
    if not api_key:
        raise ValueError("AGENTOPS_API_KEY not found in environment variables")
    
    agentops.init(api_key=api_key, auto_start_session=False)
  
    #agentops.init(api_key=os.getenv("AGENTOPS_API_KEY"),auto_start_session=False)
    session=agentops.start_session()
    flow = NewsFlow()
    #await flow.kickoff()
    await flow.kickoff_async()
    session.end_session(EndState.SUCCESS.value)
    # flow.plot("automated_news_flow")

async def main():
    print("Flow scheduled to run every 1 minute. Press Ctrl+C to stop.")

    while True:
        await run_flow()
        await asyncio.sleep(120)  # Wait for 2 minute

if __name__ == "__main__":
    asyncio.run(main())