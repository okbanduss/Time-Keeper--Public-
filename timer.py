import schedule
import time

print("Timer Triggered")

while True:
    schedule.run_pending()
    time.sleep(1)
    # print("tick")