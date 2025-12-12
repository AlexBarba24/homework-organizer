import os
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly", "https://www.googleapis.com/auth/calendar"]

schedule = {
    datetime(2024, 8, 26): {
        'topic': 'Reading: Course Organization'
    },
    datetime(2024, 8, 27): {
        'topic': 'Reading: Vectors, Sections 1.1–1.7'
    },
    datetime(2024, 8, 28): {
        'topic': 'Reading: Vectors, Sections 1.8–1.10'
    },
    datetime(2024, 8, 29): {
        'topic': 'Reading: Vectors, Sections 1.8–1.10'
    },
    datetime(2024, 8, 30, 23, 59): {
        'mastering_physics_due': 'MP-00 due 11:59 pm'
    },
    datetime(2024, 9, 3): {
        'topic': 'Reading: 1D Kinematics, Sections 2.1–2.3'
    },
    datetime(2024, 9, 3, 8, 55): {
        'achieve_due': 'A-01 due 08:55 am'
    },
    datetime(2024, 9, 4): {
        'topic': 'Reading: 1D Kinematics, Sections 2.4–2.6'
    },
    datetime(2024, 9, 5): {
        'topic': 'Reading: 3D Kinematics, Sections 3.1–3.2'
    },
    datetime(2024, 9, 5, 8, 55): {
        'achieve_due': 'A-02 due 08:55 am'
    },
    datetime(2024, 9, 6, 23, 59): {
        'mastering_physics_due': 'MP-01 due 11:59 pm'
    },
    datetime(2024, 9, 9): {
        'topic': 'Reading: Projectile Motion, Section 3.3'
    },
    datetime(2024, 9, 10): {
        'topic': 'Reading: Circular Motion, Sections 3.4'
    },
    datetime(2024, 9, 10, 8, 55): {
        'achieve_due': 'A-03 due 08:55 am'
    },
    datetime(2024, 9, 11): {
        'topic': 'Reading: Relative Motion, Section 3.5'
    },
    datetime(2024, 9, 12): {
        'topic': 'Reading: Newton’s Laws, Sections 4.1–4.4'
    },
    datetime(2024, 9, 12, 8, 55): {
        'achieve_due': 'A-04 due 08:55 am'
    },
    datetime(2024, 9, 13, 23, 59): {
        'mastering_physics_due': 'MP-02 due 11:59 pm'
    },
    datetime(2024, 9, 16): {
        'topic': 'Reading: Newton’s Laws, Sections 4.5–4.6'
    },
    datetime(2024, 9, 16, 18, 0): {
        'exam': 'Exam 1 at 06:00 pm (Chapters 1–3)'
    },
    datetime(2024, 9, 17): {
        'topic': 'Reading: Forces, Sections 5.1–5.2, 5.5'
    },
    datetime(2024, 9, 17, 8, 55): {
        'achieve_due': 'A-05 due 08:55 am'
    },
    datetime(2024, 9, 19, 23, 59): {
        'mastering_physics_due': 'MP-03 due 11:59 pm'
    },
    datetime(2024, 9, 23): {
        'topic': 'Reading: Friction, Section 5.3'
    },
    datetime(2024, 9, 23, 8, 55): {
        'achieve_due': 'A-06 due 08:55 am'
    },
    datetime(2024, 9, 24): {
        'topic': 'Reading: Friction, Section 5.3'
    },
    datetime(2024, 9, 25): {
        'topic': 'Reading: Fluid Resistance, Section 5.3'
    },
    datetime(2024, 9, 26): {
        'topic': 'Reading: Dynamics of Circular Motion, Section 5.4'
    },
    datetime(2024, 9, 27, 23, 59): {
        'mastering_physics_due': 'MP-04 due 11:59 pm'
    },
    datetime(2024, 9, 30): {
        'topic': 'Reading: Work, Sections 6.1, 6.3'
    },
    datetime(2024, 9, 30, 8, 55): {
        'achieve_due': 'A-07 due 08:55 am'
    },
    datetime(2024, 10, 1): {
        'topic': 'Reading: Work-Energy Theorem, Sections 6.2–6.3'
    },
    datetime(2024, 10, 1, 8, 55): {
        'achieve_due': 'A-08 due 08:55 am'
    },
    datetime(2024, 10, 2): {
        'topic': 'Reading: Conservative Forces, Potential Energy, Sections 7.1–7.3'
    },
    datetime(2024, 10, 2, 8, 55): {
        'achieve_due': 'A-09 due 08:55 am'
    },
    datetime(2024, 10, 3): {
        'topic': 'Reading: Conservation of Energy, Sections 7.3–7.5'
    },
    datetime(2024, 10, 4, 23, 59): {
        'mastering_physics_due': 'MP-05 due 11:59 pm'
    },
    datetime(2024, 10, 7): {
        'topic': 'Reading: Energy Diagrams, Momentum, Sections 8.1–8.2'
    },
    datetime(2024, 10, 7, 18, 0): {
        'exam': 'Exam 2 at 06:00 pm (Sections 4.1–7.3)'
    },
    datetime(2024, 10, 8): {
        'topic': 'Reading: Momentum, Sections 8.1–8.2'
    },
    datetime(2024, 10, 8, 8, 55): {
        'achieve_due': 'A-10 due 08:55 am'
    },
    datetime(2024, 10, 9): {
        'topic': 'Reading: Conservation of Momentum, Sections 8.2–8.3'
    },
    datetime(2024, 10, 9, 8, 55): {
        'achieve_due': 'A-11-12 due 08:55 am'
    },
    datetime(2024, 10, 10): {
        'topic': 'Reading: Collisions, Sections 8.3–8.4'
    },
    datetime(2024, 10, 11, 23, 59): {
        'mastering_physics_due': 'MP-06 due 11:59 pm'
    },
    datetime(2024, 10, 16): {
        'topic': 'Reading: Collisions, Center of Mass, Sections 8.3–8.5'
    },
    datetime(2024, 10, 17): {
        'topic': 'Reading: Center of Mass, Section 8.5'
    },
    datetime(2024, 10, 18, 23, 59): {
        'mastering_physics_due': 'MP-07 due 11:59 pm'
    },
    datetime(2024, 10, 21): {
        'topic': 'Reading: Angular Kinematics, Sections 9.1–9.3'
    },
    datetime(2024, 10, 21, 8, 55): {
        'achieve_due': 'A-13 due 08:55 am'
    },
    datetime(2024, 10, 22): {
        'topic': 'Reading: Moment of Inertia, Sections 9.4–9.6'
    },
    datetime(2024, 10, 23): {
        'topic': 'Reading: Moment of Inertia, Parallel-Axis Theorem, Sections 9.5–9.6'
    },
    datetime(2024, 10, 23, 8, 55): {
        'achieve_due': 'A-14 due 08:55 am'
    },
    datetime(2024, 10, 24): {
        'topic': 'Reading: Torque, Section 10.1'
    },
    datetime(2024, 10, 25, 23, 59): {
        'mastering_physics_due': 'MP-08 due 11:59 pm'
    },
    datetime(2024, 10, 28): {
        'topic': 'Reading: Rotational Dynamics, Section 10.2'
    },
    datetime(2024, 10, 28, 8, 55): {
        'achieve_due': 'A-15 due 08:55 am'
    },
    datetime(2024, 10, 28, 18, 0): {
        'exam': 'Exam 3 at 06:00 pm (Sections 7.4–9.6)'
    },
    datetime(2024, 10, 29): {
        'topic': 'Reading: Rotational Dynamics, Sections 10.2–10.3'
    },
    datetime(2024, 10, 30): {
        'topic': 'Reading: Rolling without Slipping, Section 10.3'
    },
    datetime(2024, 10, 31): {
        'topic': 'Reading: Angular Momentum, Sections 10.5–10.6'
    },
    datetime(2024, 10, 31, 8, 55): {
        'achieve_due': 'A-16-17 due 08:55 am'
    },
    datetime(2024, 11, 1, 23, 59): {
        'mastering_physics_due': 'MP-09 due 11:59 pm'
    },
    datetime(2024, 11, 4): {
        'topic': 'Reading: Angular Momentum, Sections 10.5–10.6'
    },
    datetime(2024, 11, 5): {
        'topic': 'Reading: Static Equilibrium, Sections 11.1–11.3'
    },
    datetime(2024, 11, 5, 8, 55): {
        'achieve_due': 'A-18-19 due 08:55 am'
    },
    datetime(2024, 11, 6): {
        'topic': 'Reading: Static Equilibrium, Sections 11.1–11.3'
    },
    datetime(2024, 11, 7): {
        'topic': 'Reading: Gravitational Force, Sections 13.1–13.2'
    },
    datetime(2024, 11, 8, 23, 59): {
        'mastering_physics_due': 'MP-10 due 11:59 pm'
    },
    datetime(2024, 11, 11): {
        'topic': 'Reading: Gravitational Force, Sections 13.1–13.2'
    },
    datetime(2024, 11, 12): {
        'topic': 'Reading: Gravitational Potential Energy, Sections 13.1–13.3'
    },
    datetime(2024, 11, 13): {
        'topic': 'Reading: Circular Orbits, Escape Velocity, Sections 13.3–13.4, 13.8'
    },
    datetime(2024, 11, 14): {
        'topic': 'Reading: Kepler’s Laws, Apparent Weight, Sections 13.5, 13.7'
    },
    datetime(2024, 11, 15, 23, 59): {
        'mastering_physics_due': 'MP-11 due 11:59 pm'
    },
    datetime(2024, 11, 18): {
        'topic': 'Reading: Shell Theorem, Section 13.6'
    },
    datetime(2024, 11, 18, 18, 0): {
        'exam': 'Exam 4 at 06:00 pm (Chapters 10–11 and 13)'
    },
    datetime(2024, 11, 19): {
        'topic': 'Reading: Simple Harmonic Motion, Sections 14.1–14.2'
    },
    datetime(2024, 11, 19, 8, 55): {
        'achieve_due': 'A-20 due 08:55 am'
    },
    datetime(2024, 11, 20): {
        'topic': 'Reading: Simple Harmonic Motion, Pendula, Sections 14.4–14.6'
    },
    datetime(2024, 11, 20, 8, 55): {
        'achieve_due': 'A-21 due 08:55 am'
    },
    datetime(2024, 11, 21): {
        'topic': 'Reading: Energy in Simple Harmonic Motion, Section 14.3'
    },
    datetime(2024, 11, 22, 23, 59): {
        'mastering_physics_due': 'MP-12 due 11:59 pm'
    },
    datetime(2024, 11, 25): {
        'topic': 'Reading: Damped Oscillations, Driven Oscillations, Sections 14.7–14.8'
    },
    datetime(2024, 11, 26): {
        'topic': 'Reading: Mechanical Waves, Sections 15.1–15.4'
    },
    datetime(2024, 11, 26, 8, 55): {
        'achieve_due': 'A-22 due 08:55 am'
    },
    datetime(2024, 11, 29, 23, 59): {
        'mastering_physics_due': 'MP-13 due 11:59 pm'
    },
    datetime(2024, 12, 2): {
        'topic': 'Reading: Harmonic Waves, Sections 15.2–15.4'
    },
    datetime(2024, 12, 3): {
        'topic': 'Reading: Standing Waves, Normal Modes, Sections 15.6–15.8'
    },
    datetime(2024, 12, 3, 8, 55): {
        'achieve_due': 'A-23 due 08:55 am'
    },
    datetime(2024, 12, 4): {
        'topic': 'Reading: Fluid Statics, Sections 12.1–12.2'
    },
    datetime(2024, 12, 4, 8, 55): {
        'achieve_due': 'A-24 due 08:55 am'
    },
    datetime(2024, 12, 5): {
        'topic': 'Reading: Fluid Statics, Buoyancy, Sections 12.1–12.3'
    },
    datetime(2024, 12, 6, 23, 59): {
        'mastering_physics_due': 'MP-14 due 11:59 pm'
    },
    datetime(2024, 12, 9): {
        'topic': 'Reading: Buoyancy, Section 12.3'
    },
    datetime(2024, 12, 11, 19, 30): {
        'exam': 'Final Exam at 07:30 pm (All Chapters 1–15)'
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
            if 'topic' in schedule[assignment_date]:
                assignment_name = schedule[assignment_date]['topic']
                assignment_link = ''
            if 'mastering_physics_due' in schedule[assignment_date]:
                assignment_name = schedule[assignment_date]['mastering_physics_due']
                assignment_link = 'https://login.pearson.com/v1/piapi/piui/signin?client_id=dN4bOBG0sGO9c9HADrifwQeqma5vjREy&okurl=https:%2F%2Fmycourses.pearson.com%2Fcourse-home&siteid=8313'
            if 'achieve_due' in schedule[assignment_date]:
                assignment_name = schedule[assignment_date]['achieve_due']
                assignment_link = 'https://iam.macmillanlearning.com/login?retURL=https://achieve.macmillanlearning.com/courses'
            if 'exam' in schedule[assignment_date]:
                assignment_name = schedule[assignment_date]['exam']
                assignment_link = ''
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
