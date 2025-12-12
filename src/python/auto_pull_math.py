from selenium import webdriver
import datetime
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import os
import os.path
from dotenv import load_dotenv

import task_generator

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly", "https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/tasks"]

def main():
    load_dotenv()
    task_generator.init()

    web = 'https://instruct.math.lsa.umich.edu/webwork2/ma116-024-f24'
    path = os.getenv('CHROMEDRIVER_PATH')
    op = webdriver.ChromeOptions()
    # op.add_argument('headless')
    service = Service(executable_path=path)
    driver = webdriver.Chrome(service=service, options=op)

    driver.get(web)

    username = str(os.getenv('USERNAME'))
    password = str(os.getenv('PASSWORD'))

    driver.find_element(By.ID, 'username').send_keys(username)
    driver.find_element(By.ID, 'password').send_keys(password)

    driver.find_element(By.ID, 'loginSubmit').click()

    while True:
        try:
            driver.find_element(By.ID, 'trust-browser-button')
            break
        except:
            time.sleep(1)

    driver.find_element(By.ID, 'trust-browser-button').click()
    while True:
        try:
            driver.find_element(By.ID, 'set-list-container')
            break
        except:
            time.sleep(1)

    print('assignments found!')

    achieve_assignments = driver.find_elements(By.XPATH, '//li[@class="list-group-item d-flex align-items-center justify-content-between"and@data-set-status="open"]')

    # creds = None
    # # The file token.json stores the user's access and refresh tokens, and is
    # # created automatically when the authorization flow completes for the first
    # # time.
    # if os.path.exists("token.json"):
    #     creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # # If there are no (valid) credentials available, let the user log in.
    # if not creds or not creds.valid:
    #     if creds and creds.expired and creds.refresh_token:
    #         creds.refresh(Request())
    #     else:
    #         flow = InstalledAppFlow.from_client_secrets_file(
    #             "credentials.json", SCOPES
    #         )
    #         creds = flow.run_local_server(port=0)
    #     # Save the credentials for the next run
    #     with open("token.json", "w") as token:
    #         token.write(creds.to_json())

    # try:
    #     service = build("calendar", "v3", credentials=creds)
    #     cal_exists=False;
    #     # build(service, "calendar", "v3",credentials=creds)
    #     # Call the Calendar API
    #     calendar_list = service.calendarList().list().execute()
    #     for item in calendar_list['items']:
    #         if item['summary']=='Homework':
    #             cal_exists=True
    #             break
    #     if not cal_exists:
    #         service.calendars().insert(body={
    #                 "description": "An automatically generated homework schedule",  # Description of the calendar. Optional.
    #           #      "etag": "",  # ETag of the resource.
    #           #      "id": "automatedHomework",
    #                 # Identifier of the calendar. To retrieve IDs call the calendarList.list() method.
    #                 "summary": "Homework",  # Title of the calendar.
    #                 # The time zone of the calendar. (Formatted as an IANA Time Zone Database name, e.g. "Europe/Zurich".) Optional.
    #         }).execute()
    #     calendar_list = service.calendarList().list().execute()
    #     cal_id = 'none'
    #     for item in calendar_list['items']:
    #         if item['summary']=='Homework':
    #             cal_id = item['id']
        ###### Item Specific ########
    assignment_name="Test Assignment"
    assignment_date = " September 13, 2024, 11:59:00 PM EDT"
    assignment_link = "https://www.google.com"
        #

    for achieve_assignment in achieve_assignments:
        # already_exists=False
        assignment_name = achieve_assignment.find_element(By.XPATH, './/a[contains(@class,"fw-bold set-id-tooltip")]').text
        # all_events = service.events().list(calendarId=cal_id).execute()
        # for event in all_events['items']:
        #     if event['summary'] == assignment_name:
        #         already_exists=True
        #         break
        # if already_exists:
        #     continue
        assignment_link = achieve_assignment.find_element(By.XPATH, './/a[contains(@class,"fw-bold set-id-tooltip")]').get_attribute('href')
        assignment_date = achieve_assignment.find_element(By.XPATH, './/div[contains(@class,"font-sm")]').text
        assignment_date = str(assignment_date).split(sep=' ',maxsplit=2)[2]
        assignment_description = "<a href = \"" + assignment_link + "\">Assignment Link</a>"
        event_datetime = datetime.datetime.strptime(assignment_date, "%B %d, %Y, %I:%M:%S\u202f%p %Z.")  # 'Z' indicates UTC time


        task_generator.create_event(assignment_name, event_datetime, assignment_link)
    #         print(event_datetime)
    #         service.events().insert(calendarId=cal_id, body={
    #             "summary": assignment_name,
    #             "description": "<a href = \"" + assignment_link + "\">Assignment Link</a>",
    #             "start":{
    #                 "dateTime":event_datetime,
    #                 "timeZone": "America/New_York",
    #             },
    #             "end":{
    #                 "dateTime": event_datetime,
    #                 "timeZone": "America/New_York",
    #             },
    #         }).execute()
    #         print('Assignment: ', assignment_name, ' is due on ', assignment_date, ' and can be accessed at: ', assignment_link)
    # except HttpError as error:
    #     print(f"An error occurred: {error}")
    # empty_task = {
    #   "kind": 'tasks#task',
    #   "id": string,
    #   "etag": string,
    #   "title": string,
    #   "updated": string,
    #   "selfLink": string,
    #   "parent": string,
    #   "position": string,
    #   "notes": string,
    #   "status": string,
    #   "due": string,
    #   # "completed": string,
    #   "deleted": false,
    #   "hidden": false,
    #   "links": [
    #     {
    #       "type": 'website',
    #       "description": 'Link to Assignment',
    #       "link": str(assignment_link)
    #     }
    #   ],
    #   "webViewLink": string,
    #   "assignmentInfo": {}
    # }
    """Shows basic usage of the Google Calendar API.
     Prints the start and name of the next 10 events on the user's calendar.
     """



if __name__ == "__main__":
    main()

# Assignment Link //a[contains(@class,"fw-bold set-id-tooltip")]
# Date XPATH //div[contains(@class,"font-sm")] first element

#while True:
#    time.sleep(1)

