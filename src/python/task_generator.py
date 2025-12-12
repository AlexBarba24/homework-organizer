from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime
import os

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly", "https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/tasks"]
creds = None

def init():
    global creds
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
def create_task(name, date: datetime, description):
    global creds
    credentials = creds
    try:
        service = build("tasks", "v1", credentials=credentials)
        taskl_exists = False;
        # build(service, "calendar", "v3",credentials=creds)
        # Call the Calendar API
        task_list = service.tasklists().list().execute()
        for item in task_list['items']:
            #if item['title'] == 'Homework':
                taskl_exists = True
                break
        if not taskl_exists:
            service.tasklists().insert(body={
                #"description": "An automatically generated homework schedule",  # Description of the calendar. Optional.
                #      "etag": "",  # ETag of the resource.
                #      "id": "automatedHomework",
                # Identifier of the calendar. To retrieve IDs call the calendarList.list() method.
                "title": "Homework",  # Title of the calendar.
                # The time zone of the calendar. (Formatted as an IANA Time Zone Database name, e.g. "Europe/Zurich".) Optional.
            }).execute()
        task_list = service.tasklists().list().execute()
        taskl_id = 'none'
        for item in task_list['items']:
            if item['title'] == 'Homework':
                taskl_id = item['id']
        all_tasks = service.tasks().list(tasklist=taskl_id).execute()
        already_exists = False
        for event in all_tasks['items']:
            if event['title'] == name:
                already_exists=True
                break
        if already_exists:
            return
        event_datetime = date.isoformat()
        service = build("tasks", "v1", credentials=credentials)
        service.tasks().insert(tasklist=taskl_id, body={
            #"<a href = \"" + link + "\">Assignment Link</a>"
            "title": name,
            "notes": description,
            "due": event_datetime,
            # "start": {
            #     "dateTime": event_datetime,
            #     "timeZone": "America/New_York",
            # },
            # "end": {
            #     "dateTime": event_datetime,
            #     "timeZone": "America/New_York",
            # },
        }).execute()

    except HttpError as error:
        print(f"An error occurred: {error}")

def create_event(name, date: datetime, description):
    global creds
    try:
        service = build("calendar", "v3", credentials=creds)
        cal_exists = False;
        # build(service, "calendar", "v3",credentials=creds)
        # Call the Calendar API
        calendar_list = service.calendarList().list().execute()
        for item in calendar_list['items']:
            if item['summary'] == 'Homework':
                cal_exists = True
                break
        if not cal_exists:
            service.calendars().insert(body={
                "description": "An automatically generated homework schedule",  # Description of the calendar. Optional.
                #      "etag": "",  # ETag of the resource.
                #      "id": "automatedHomework",
                # Identifier of the calendar. To retrieve IDs call the calendarList.list() method.
                "summary": "Homework",  # Title of the calendar.
                # The time zone of the calendar. (Formatted as an IANA Time Zone Database name, e.g. "Europe/Zurich".) Optional.
            }).execute()
        calendar_list = service.calendarList().list().execute()
        cal_id = 'none'
        for item in calendar_list['items']:
            if item['summary'] == 'Homework':
                cal_id = item['id']
        all_events = service.events().list(calendarId=cal_id).execute()
        already_exists = False
        for event in all_events['items']:
          if event.get('summary'):
            if event['summary'] == name:
                already_exists=True
                break
        if already_exists:
            return
        event_datetime = date.isoformat()
        service.events().insert(calendarId=cal_id, body={
            #"<a href = \"" + link + "\">Assignment Link</a>"
            "summary": name,
            "description": description,
            "start": {
                "dateTime": event_datetime,
                "timeZone": "America/New_York",
            },
            "end": {
                "dateTime": event_datetime,
                "timeZone": "America/New_York",
            },
        }).execute()

    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == '__main__':
    init()
    create_task('Homework', datetime.datetime(2024, 9, 17), 'test')
