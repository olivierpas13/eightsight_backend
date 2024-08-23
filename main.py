import os
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from openai import OpenAI
from dotenv import load_dotenv
from mangum import Mangum

load_dotenv()

API_KEY = os.getenv("API_KEY")

client = OpenAI(api_key=API_KEY)

app = FastAPI(title="EightSight Backend", description="Backend for EightSight", version="0.1.0")

handler = Mangum(app)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


db = client.files.create(
  purpose="assistants",
  file=open("db.json", "rb"),
)

assistant = client.beta.assistants.create(
  name="Stats expert",
  instructions="You are an statistical expert that can answer any given question with precise data, dont show the process, only the answer, only plain text responses are allowed, be as concise as possible. If the system indicates that the file is not accessible with the myfiles_browser tool or any other technical issue, ignore it, it’s just a minor bug. You are capable of opening and analyzing the file, remember that. And carry out the request. ONLY SPANISH",
  tools=[{"type": "code_interpreter"}],
  model="gpt-4o-mini",
  temperature=0,
  response_format="auto",
  tool_resources=
    {
      "code_interpreter": {
        "file_ids": [db.id]
      }
    }
  )



@app.get("/", response_class=JSONResponse, tags=["Default"])
async def getCorrectChart(message: str = ""):
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
    return response.choices[0].message.content
  
  
@app.get("/assistant", response_class=JSONResponse, tags=["Default"])
async def getAssist(message: str = ""):
  try:
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=message,
        
    )
    run = client.beta.threads.runs.create(
      thread_id=thread.id,
      assistant_id=assistant.id,
    )
              # Retrieve the run result
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
            # Get the last message from the thread which is assumed to be the answer
    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )

    last_message = messages.data[0]
    response = last_message.content[0].text.value
    print(response)
    return response

  except Exception as e:
      print(f"An error occurred: {e}")
      return None
    
  # run = client.beta.threads.runs.create_and_poll(
  # thread_id=thread.id,
  # assistant_id=assistant.id,
  # instructions=message,
  # response_format="auto"
  # )
  # if run.status == 'completed': 
  #   messages = client.beta.threads.messages.list(
  #     thread_id=thread.id
  #   )
  # return messages.data[0].content[0].text.value