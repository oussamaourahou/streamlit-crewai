from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import json
import http.client
import os

from dotenv import load_dotenv

load_dotenv()

class MyCustomToolInput(BaseModel):
    """Input schema for MyCustomTool."""
    argument: str = Field(..., description="Description of the argument.")

class CustomSerperDevTool(BaseTool):
    name: str = "Custom Serper Dev Tool"
    description: str = "Search the internet for news"
    

    def _run(self, query: str) -> str:
        conn = http.client.HTTPSConnection("google.serper.dev")
        payload = json.dumps({
            "q": query,
            "gl": "ma",
            "hl": "fr",
            "num": 20,
            "tbs": "qdr:d"
        })
        headers = {
            'X-API-KEY': os.getenv('SERPER_API_KEY'),
            'Content-Type': 'application/json'
        }
        conn.request("POST", "/news", payload, headers)
        res = conn.getresponse()
        data = json.loads(res.read().decode("utf-8"))
        
        # Return only the news array from the response
        return json.dumps(data.get("news", []), ensure_ascii=False, indent=2)
