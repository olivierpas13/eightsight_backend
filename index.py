from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from openai import OpenAI

from dotenv import load_dotenv
import os
load_dotenv()

API_KEY = os.getenv("API_KEY")

client = OpenAI(api_key=API_KEY)


app = FastAPI(title="Pandemic Backend", description="Disease transmition model using ODEs")


@app.get("/", response_class=JSONResponse, tags=["Default"])
async def calculate_default_data(message: str = ""):
    response = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {
          "role": "system",
          "content": [
            {
              "type": "text",
              "text": "Return correct statistical chart for the requested information, you can select from [bar, sunburst, pie], only respond with the type of chart, not data"
            }
          ]
        },
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": message,
            }
          ]
        }
      ],
      temperature=0,
      max_tokens=100,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0,
      response_format={
        "type": "text"
      }
    )
    print(response)
    return response.choices[0].message.content