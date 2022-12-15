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
channel_id = "XXXXX" # Replace with your Slack user ID
clocked_in = False

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
        text = "Hey loser, it's that time again! Clock in now! :clown_face:",
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
        text = "Processing...",
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
    clockin_check()

# Format the clockin/out time to readable format
def format_time():
    current_time = datetime.now()
    global formatted_time
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

# Clock in successful message
def reply_clockedin():
    print(clocked_in)
    format_time()
    client.chat_postMessage (
        channel = channel_id,
        text = "You're now clocked in, now work till you're dead! :skull:",
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
def reply_clockedout():
    format_time()
    client.chat_postMessage (
        channel = channel_id,
        text = "Just clocked out for you, now GTFO! :middle_finger:",
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

# Error: already clocked out message
def reply_already_clockedout():
    client.chat_postMessage (
        channel = channel_id,
        text = "Seems like you're already clocked out... :face_with_monocle:",
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Seems like you're already clocked out... :face_with_monocle: Please login to your <https://mlytics.webhr.co/hr/login/|WebHR>"
                }
            }
        ]
    )
    
# Error: already clocked in message
def reply_already_clockedin():
    client.chat_postMessage (
        channel = channel_id,
        text = "Seems like you're already clocked in... :face_with_monocle:",
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Seems like you're already clocked in... :face_with_monocle: Please login to your <https://mlytics.webhr.co/hr/login/|WebHR> for more info or click \"Try again\" to retry. You can click \"clock out\" to manually clock yourself out."
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
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Clock out"
                        },
                        "value": "Clock out",
                        "action_id": "clockout_click"
                    }
                ]
            }
        ]
    )

# Error: unknown
def reply_error():
    client.chat_postMessage (
        channel = channel_id,
        text = "Something's not right... :face_with_monocle:",
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Something's not right... :face_with_monocle: Please login to your <https://mlytics.webhr.co/hr/login/|WebHR>"
                }
            }
        ]
    )

# Button click listen event: retry to clock in
@app.action("retry_click")
def retry_button_click(ack):
    ack()
    fetch_conversations()
    client.chat_update (
        channel = conversation_id,
        ts = timestamp,
        text = "Retrying...",
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
    clockin_check()

# Button click listen event: retry to clock out
@app.action("clockout_click")
def clockout_button_click(ack):
    ack()
    fetch_conversations()
    client.chat_update (
        channel = conversation_id,
        ts = timestamp,
        text = "Processing...",
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
    clockout_check()
    

# Command to manually clock in
@app.message("clock in")
def manual_clockin():
    clockin_check()

# Command to manually clock out
@app.message("clock out")
def manual_clockout():
    client.chat_postMessage (
        channel = channel_id,
        text = "_Processing..._"
    )
    clockout_check()

# Check if a user is clocked in, if True, trigger error, else execute
def clockin_check():
    global clocked_in
    if clocked_in == True:
        reply_already_clockedin()
    elif clocked_in == False:
        clocked_in = True
        from clockin import clockin
        clockin()

# Check if a user is clocked out, if True, execute, else trigger error
def clockout_check():
    global clocked_in
    if clocked_in == True:
        clocked_in = False
        from clockout import clockout
        clockout()
    elif clocked_in == False:
        reply_already_clockedout()


# For testing only
@app.message("start")
def manual_reminder():
    clock_in_reminder()

@app.message("switch")
def switch_status():
    global clocked_in
    if clocked_in == True:
        clocked_in = False
        print("Clock in status:", clocked_in)
    else:
        clocked_in = True
        print("Clock in status:", clocked_in)

@app.message("print")
def print_status():
    print(clocked_in)


# Trigger reminder every morning
schedule.every().monday.at("10:00").do(clock_in_reminder)
schedule.every().tuesday.at("10:00").do(clock_in_reminder)
schedule.every().wednesday.at("10:00").do(clock_in_reminder)
schedule.every().thursday.at("10:00").do(clock_in_reminder)
schedule.every().friday.at("10:00").do(clock_in_reminder)

# Auto sign out every evening at 19:00
schedule.every().monday.at("19:00").do(clockout_check)
schedule.every().tuesday.at("19:00").do(clockout_check)
schedule.every().wednesday.at("19:00").do(clockout_check)
schedule.every().thursday.at("19:00").do(clockout_check)
schedule.every().friday.at("19:00").do(clockout_check)

def timer():
    import timer

Thread(target = timer).start()

if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()