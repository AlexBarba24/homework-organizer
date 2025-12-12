import os
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ["https://www.googleapis.com/auth/calendar.readonly", "https://www.googleapis.com/auth/calendar"]

schedule = {
    datetime(2024, 9, 9, 10, 30): {
        'assignment': 'Reading: Operations Management',
        'link': 'https://www.bdc.ca/en/articles-tools/entrepreneur-toolkit/covid19-operations-management-planning'
    },
    datetime(2024, 9, 15, 23, 59): {
        'assignment': 'Team Contract Due',
        'link': None
    },
    datetime(2024, 9, 20, 23, 59): {
        'assignment': 'Reflective Writing Due',
        'link': None
    },
    datetime(2024, 9, 22, 23, 59): {
        'assignment': '[Proposal] Presentation Slides due',
        'link': None
    },
    datetime(2024, 9, 30, 10, 30): {
        'assignment': 'Reading: Optimization and Queuing Systems Demo',
        'link': 'https://www.lean.org/explore-lean/what-is-lean/'
    },
    datetime(2024, 10, 4, 23, 59): {
        'assignment': '[Proposal] Report Due',
        'link': None
    },
    datetime(2024, 10, 18, 23, 59): {
        'assignment': '[Mid-project] Current State Report Due',
        'link': None
    },
    datetime(2024, 10, 25, 23, 59): {
        'assignment': 'Individual Memo Due',
        'link': None
    },
    datetime(2024, 11, 1, 23, 59): {
        'assignment': '[IOE] Homework Due',
        'link': None
    },
    datetime(2024, 11, 12, 23, 59): {
        'assignment': '[Final] Report Draft Due',
        'link': None
    },
    datetime(2024, 11, 15, 23, 59): {
        'assignment': '[Final] Report Peer Review Due',
        'link': None
    },
    datetime(2024, 11, 19, 23, 59): {
        'assignment': '[Final] Presentation Slides Due',
        'link': None
    },
    datetime(2024, 12, 6, 23, 59): {
        'assignment': '[Final] Report Due',
        'link': None
    },
}

def main():
    creds = None
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

    try:
        service = build("calendar", "v3", credentials=creds)
        cal_exists=False;
        # build(service, "calendar", "v3",credentials=creds)
        # Call the Calendar API
        calendar_list = service.calendarList().list().execute()
        for item in calendar_list['items']:
            if item['summary']=='Homework':
                cal_exists=True
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
            if item['summary']=='Homework':
                cal_id = item['id']
        ###### Item Specific ########
        assignment_name="Test Assignment"
        assignment_date = " September 13, 2024, 11:59:00 PM EDT"
        assignment_link = "https://www.google.com"

        for assignment_date in schedule:
            print(schedule[assignment_date])
            assignment_name = schedule[assignment_date]['assignment']
            if schedule[assignment_date]['link'] is None:
                assignment_link = ''
            else:
                assignment_link = schedule[assignment_date]['link']
            event_datetime = assignment_date.isoformat()
            already_exists=False
            all_events = service.events().list(calendarId=cal_id).execute()
            for event in all_events['items']:
                if event['summary'] == assignment_name:
                    already_exists=True
                    break
            if already_exists:
                continue
            print(event_datetime)
            service.events().insert(calendarId=cal_id, body={
                "summary": assignment_name,
                "description": "<a href = \"" + assignment_link + "\">Assignment Link</a>",
                "start":{
                    "dateTime":event_datetime,
                    "timeZone": "America/New_York",
                },
                "end":{
                    "dateTime": event_datetime,
                    "timeZone": "America/New_York",
                },
            }).execute()
            print('Assignment: ', assignment_name, ' is due on ', assignment_date, ' and can be accessed at: ', assignment_link)
    except HttpError as error:
        print(f"An error occurred: {error}")




if __name__ == '__main__':
    main()
