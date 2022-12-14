from threading import Thread
import schedule
import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from datetime import datetime

load_dotenv()

app = App(token=os.getenv("SLACK_BOT_TOKEN"))
client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
channel_id = "XXXXXXXX" # Your Slack User ID

# Find the last conversation and the latest message
def fetch_conversations():
    result = client.conversations_list(
        types="im"
    )
    conversations = result["channels"]
    conversation = conversations[0]
    global conversation_id
    conversation_id = conversation["id"]
    message_ts = client.conversations_history(
        channel = conversation_id,
    ).data
    conversation_history = message_ts["messages"]
    conversation_history.sort(key=lambda x: x["ts"], reverse=True)
    latest_message = conversation_history[0]
    global timestamp
    timestamp = latest_message["ts"]

# Clock in script
def clock_in_reminder():
    client.chat_postMessage (
        channel = channel_id,
        text = "Reminder to clock in today",
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Hey loser, it's that time again! Clock in now!* :clown_face:"
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Clock in"
                        },
                        "value": "Clock in",
                        "action_id": "button_click"
                    }
                ]
            }
        ]
    )

# Button click listen event
@app.action("button_click")
def action_button_click(ack):
    ack()
    fetch_conversations()
    client.chat_update (
        channel = conversation_id,
        ts = timestamp,
        text = "Processing",
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "_Processing..._"
                },
            }
        ]
    )
    from clockin import clockin
    clockin()

# Trigger clockout script
def clock_out():
    from clockout import clockout
    clockout()

# Format the clockin/out time to readable format
def format_time():
    current_time = datetime.now()
    global formatted_time
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

# Clock in successful message
def reply_signedin():
    format_time()
    client.chat_postMessage (
        channel = channel_id,
        text = "Signed in",
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*You're now clocked in, now work till you're dead!* :skull:"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "_Clock in date & time: {formatted_time}_".format(formatted_time=formatted_time)
                }
            }
        ]
    )

# Clock out successful message
def reply_signedout():
    format_time()
    client.chat_postMessage (
        channel = channel_id,
        text = "Signed out",
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Just clocked out for you, now GTFO!* :middle_finger:"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "_Clock out date & time: {formatted_time}_".format(formatted_time=formatted_time)
                }
            }
        ]
    )

# Error: already clocked in message
def reply_already_signedout():
    client.chat_postMessage (
        channel = channel_id,
        text = "Signed out",
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Something's wrong... Tried to clock you out, but you're already clocked out... :face_with_monocle: Please login to your <https://mlytics.webhr.co/hr/login/|WebHR>"
                }
            }
        ]
    )

# Error: general error message
def error():
    client.chat_postMessage (
        channel = channel_id,
        text = "Signed out",
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Cannot clock you in, you're maybe currently clocked in? :face_with_monocle: Please login to your <https://mlytics.webhr.co/hr/login/|WebHR> for more info or click \"Retry\" to try again. You can also type \"clock out\" to manually clock yourself out."
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Try again"
                        },
                        "value": "Try again",
                        "action_id": "retry_click"
                    }
                ]
            }
        ]
    )

# Button click listen event
@app.action("retry_click")
def retry_button_click(ack):
    ack()
    fetch_conversations()
    client.chat_update (
        channel = conversation_id,
        ts = timestamp,
        text = "Processing",
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "_Retrying..._"
                },
            }
        ]
    )
    from clockin import clockin
    clockin()
    
@app.message("clock out")
def manual_clockout():
    client.chat_postMessage (
        channel = channel_id,
        text = "_Processing..._"
    )
    from clockout import clockout
    clockout()

@app.message("test")
def manual_clockout():
    clock_in_reminder()

# Trigger reminder every morning
schedule.every().monday.at("10:00").do(clock_in_reminder)
schedule.every().tuesday.at("10:00").do(clock_in_reminder)
schedule.every().wednesday.at("01:48").do(clock_in_reminder)
schedule.every().thursday.at("10:00").do(clock_in_reminder)
schedule.every().friday.at("10:00").do(clock_in_reminder)

# Auto sign out every evening at 19:00
schedule.every().monday.at("19:00").do(clock_out)
schedule.every().tuesday.at("19:00").do(clock_out)
schedule.every().wednesday.at("19:00").do(clock_out)
schedule.every().thursday.at("19:00").do(clock_out)
schedule.every().friday.at("19:00").do(clock_out)

def timer():
    import timer

Thread(target = timer).start()

if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()