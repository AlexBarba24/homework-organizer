from os import environ

from openai import OpenAI
# print(environ["OPENAI_API_KEY"])
from openai import OpenAI
import json

def parse_pdf(message):
  client = OpenAI()
  response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
      {
        "role": "system",
        "content": [
          {
            "type": "text",
            "text": "Your task is to read the syllabus provided and call the function add_assignment_to_calendar for each assignment, or exam specified in the syllabus, with the expected details."
          }
        ]
      },
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "{\n\"message\":\"There will be a Google Homework assignment due on January 18th, it can be accessed at www.google.com\"\n\"response-format\":\"json_object\"\n}"
          }
        ]
      },
      {
        "role": "assistant",
        "tool_calls": [
          {
            "id": "manualToolCall_muqbef",
            "type": "function",
            "function": {
              "name": "add_assignment_to_calendar",
              "arguments": "{\n  \"assignment_name\": \"Google Homework 1/18\",\n  \"due_date\": \"2024-01-18T23:59:00m\",\n  \"assignment_link\": \"www.google.com\"\n}"
            }
          }
        ]
      },
      {
        "role": "tool",
        "content": [
          {
            "type": "text",
            "text": "{\n  \"status\": \"success\",\n  \"message\": \"Assignment added to calendar successfully.\",\n  \"data\": {\n    \"assignment_name\": \"Google Homework 1/18\",\n    \"due_date\": \"2024-01-18T23:59:00m\",\n    \"assignment_link\": \"www.google.com\"\n  }\n}"
          }
        ],
        "tool_call_id": "manualToolCall_muqbef"
      },
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "{\n\"message\":\"There will be a Microsoft Homework assignment due on March 12th at 3:00pm, it can be accessed at www.microsoft.com\"\n\"response-format\":\"json_object\"\n}"
          }
        ]
      },
      {
        "role": "assistant",
        "tool_calls": [
          {
            "id": "call_o9XK99mHqt315O24PIG7jc6o",
            "type": "function",
            "function": {
              "name": "add_assignment_to_calendar",
              "arguments": "{\"assignment_name\":\"Microsoft Homework 3/12\",\"due_date\":\"2024-03-12T15:00:00\",\"assignment_link\":\"www.microsoft.com\"}"
            }
          }
        ]
      },
      {
        "role": "tool",
        "content": [
          {
            "type": "text",
            "text": "{\n  \"status\": \"success\",\n  \"message\": \"Assignment added to calendar successfully.\",\n  \"assignment\": {\n    \"assignment_name\": \"Microsoft Homework 3/12\",\n    \"due_date\": \"2024-03-12T15:00:00\",\n    \"assignment_link\": \"www.microsoft.com\"\n  }\n}"
          }
        ],
        "tool_call_id": "call_o9XK99mHqt315O24PIG7jc6o"
      },
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "{\n\"message\":\"There will be another Microsoft Homework assignment due on March 15th at 3:00pm, it can be accessed at www.microsoft.com, there will also be a computer science exam on April 3rd at 10am\"\n\"response-format\":\"json_object\"\n}"
          }
        ]
      },
      {
        "role": "assistant",
        "tool_calls": [
          {
            "id": "call_IBXS3jj3M6oTYGIV8DZeGVKz",
            "type": "function",
            "function": {
              "name": "add_assignment_to_calendar",
              "arguments": "{\"assignment_name\": \"Microsoft Homework 3/15\", \"due_date\": \"2024-03-15T15:00:00\", \"assignment_link\": \"www.microsoft.com\"}"
            }
          },
          {
            "id": "call_XJG0KrU3dEdSm9c298FMtw4g",
            "type": "function",
            "function": {
              "name": "add_assignment_to_calendar",
              "arguments": "{\"assignment_name\": \"Computer Science Exam 4/3\", \"due_date\": \"2024-04-03T10:00:00\", \"assignment_link\": \"\"}"
            }
          }
        ]
      },
      {
        "role": "tool",
        "content": [
          {
            "type": "text",
            "text": "{\n  \"status\": \"success\",\n  \"message\": \"Assignment added to calendar\",\n  \"data\": {\n    \"assignment_name\": \"Microsoft Homework 3/15\",\n    \"due_date\": \"2024-03-15T15:00:00\",\n    \"assignment_link\": \"www.microsoft.com\"\n  }\n}"
          }
        ],
        "tool_call_id": "call_IBXS3jj3M6oTYGIV8DZeGVKz"
      },
      {
        "role": "tool",
        "content": [
          {
            "type": "text",
            "text": "{\n  \"status\": \"success\",\n  \"message\": \"Assignment added to calendar\",\n  \"data\": {\n    \"assignment_name\": \"Computer Science Exam 4/3\",\n    \"due_date\": \"2024-04-03T10:00:00\",\n    \"assignment_link\": \"\",\n    \"calendar_event_id\": \"evt_123456789\"  }\n}"
          }
        ],
        "tool_call_id": "call_XJG0KrU3dEdSm9c298FMtw4g"
      },
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "{\n\"message\":\""+ message +"\":\"json_object\"\n}"
          }
        ]
      },
    ],
    response_format={
      "type": "json_object"
    },
    tools=[
      {
        "type": "function",
        "function": {
          "name": "add_assignment_to_calendar",
          "description": "Adds an assignment to a Google Calendar including a name, due date/time, and optionally an assignment link.",
          "parameters": {
            "type": "object",
            "required": [
              "assignment_name",
              "due_date",
              "assignment_link"
            ],
            "properties": {
              "assignment_name": {
                "type": "string",
                "description": "The name of the assignment"
              },
              "due_date": {
                "type": "string",
                "description": "The due date and time for the assignment in ISO 8601 format"
              },
              "assignment_link": {
                "type": "string",
                "description": "An optional link to the assignment"
              }
            },
            "additionalProperties": False
          },
          "strict": True
        }
      }
    ],
    temperature=1,
    max_completion_tokens=2048,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
  )
  if response.choices[0].model_dump()['message']['tool_calls'] is None:
    return []
  
  assignments = []
  for call in response.choices[0].model_dump()['message']['tool_calls']:
    assignment_data = json.loads(call['function']['arguments'])
    assignments.append({
      'assignment_name': assignment_data.get('assignment_name', ''),
      'due_date': assignment_data.get('due_date', ''),
      'assignment_link': assignment_data.get('assignment_link', '')
    })
  
  return assignments
