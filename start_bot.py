from nordvpn_switcher import initialize_VPN, rotate_VPN, terminate_VPN
from src.video_bot import main
import traceback
import os
import sys

visual = 0
url = open("url.txt", "r").readlines()[0].strip()
if url is None:
    print("before start bot set url on url.txt")
    sys.exit()


def initialize():
    initialize_VPN(save=1, area_input=['complete rotation'])
    print(f"connect to: {url}")


def start_bot():
    global visual, url
    while True:
        try:
            print(f"visuals: {visual}")
            try:
                rotate_VPN(google_check=1)
            except:
                continue
            error = main(url)
            if type(error) == str:
                print(error)
                continue
            visual += 1
        except ValueError as err:
            print(err, traceback.format_exc())
            break
        except Exception as err:
            print(err, traceback.format_exc())
            break


def finish():
    terminate_VPN()
    os.remove("settings_nordvpn.txt")


if __name__ == "__main__":
    initialize()
    start_bot()
    finish()
