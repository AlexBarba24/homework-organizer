from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import sys
import os
from datetime import datetime

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar",
]


def init():
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
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def add_assignments_to_calendar(assignments):
    creds = init()

    try:
        service = build("calendar", "v3", credentials=creds)

        # Check if Homework calendar exists, create if not
        cal_exists = False
        calendar_list = service.calendarList().list().execute()
        for item in calendar_list["items"]:
            if item["summary"] == "Homework":
                cal_exists = True
                break

        if not cal_exists:
            service.calendars().insert(
                body={
                    "description": "An automatically generated homework schedule",
                    "summary": "Homework",
                }
            ).execute()

        # Get the calendar ID
        calendar_list = service.calendarList().list().execute()
        cal_id = None
        for item in calendar_list["items"]:
            if item["summary"] == "Homework":
                cal_id = item["id"]
                break

        if not cal_id:
            return {
                "success": False,
                "error": "Could not find or create Homework calendar",
            }

        # Get existing events to avoid duplicates
        all_events = service.events().list(calendarId=cal_id).execute()
        existing_summaries = set()
        for event in all_events.get("items", []):
            if event.get("summary"):
                existing_summaries.add(event["summary"])

        added_count = 0
        skipped_count = 0
        errors = []

        # Add each assignment
        for assignment in assignments:
            assignment_name = assignment.get("assignment_name", "")
            due_date_str = assignment.get("due_date", "")
            assignment_link = assignment.get("assignment_link", "")

            # Skip if already exists
            if assignment_name in existing_summaries:
                skipped_count += 1
                continue

            try:
                # Parse the due date (expecting ISO 8601 format)
                # Handle various formats
                try:
                    if "T" in due_date_str:
                        event_datetime = datetime.fromisoformat(
                            due_date_str.replace("Z", "+00:00")
                        )
                    else:
                        event_datetime = datetime.fromisoformat(due_date_str)
                except:
                    # Try parsing as string with timezone
                    event_datetime = datetime.fromisoformat(
                        due_date_str.replace("m", "")
                    )  # Handle 'm' suffix

                # Format for Google Calendar API
                event_datetime_iso = event_datetime.isoformat()

                # Create description with link if provided
                description = ""
                if assignment_link:
                    description = f'<a href="{assignment_link}">Assignment Link</a>'

                # Insert event
                service.events().insert(
                    calendarId=cal_id,
                    body={
                        "summary": assignment_name,
                        "description": description,
                        "start": {
                            "dateTime": event_datetime_iso,
                            "timeZone": "America/New_York",
                        },
                        "end": {
                            "dateTime": event_datetime_iso,
                            "timeZone": "America/New_York",
                        },
                    },
                ).execute()

                added_count += 1
                existing_summaries.add(
                    assignment_name
                )  # Track added to avoid duplicates in same batch

            except Exception as e:
                errors.append(f"Error adding {assignment_name}: {str(e)}")

        result = {
            "success": True,
            "added": added_count,
            "skipped": skipped_count,
            "total": len(assignments),
        }
        if errors:
            result["errors"] = errors

        return result

    except HttpError as error:
        return {"success": False, "error": f"HTTP error occurred: {error}"}
    except Exception as e:
        return {"success": False, "error": f"An error occurred: {str(e)}"}


if __name__ == "__main__":
    try:
        # Read JSON from stdin
        input_data = sys.stdin.read()
        if not input_data:
            print(
                json.dumps({"success": False, "error": "No input data received"}),
                file=sys.stderr,
            )
            sys.exit(1)

        assignments = json.loads(input_data)

        if not isinstance(assignments, list):
            error_msg = json.dumps(
                {"success": False, "error": "Expected a JSON array of assignments"}
            )
            print(error_msg, file=sys.stderr)
            sys.exit(1)

        result = add_assignments_to_calendar(assignments)

        # Always output to stdout, even on error
        output = json.dumps(result)
        print(output)
        sys.stdout.flush()  # Ensure output is flushed

        if not result.get("success"):
            sys.exit(1)

    except json.JSONDecodeError as e:
        error_msg = json.dumps({"success": False, "error": f"Invalid JSON: {str(e)}"})
        print(error_msg)  # Print to stdout so it can be parsed
        print(error_msg, file=sys.stderr)  # Also print to stderr for debugging
        sys.exit(1)
    except Exception as e:
        error_msg = json.dumps(
            {"success": False, "error": str(e), "exception_type": type(e).__name__}
        )
        print(error_msg)  # Print to stdout so it can be parsed
        print(error_msg, file=sys.stderr)  # Also print to stderr for debugging
        sys.exit(1)
