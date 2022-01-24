"""
A small script to generate pyrogram session string
"""
from pyrogram import Client

try:
    print(
        "Make sure you have API Client ID and Hash , If not goto my.telegram.org and generate it.\n\n"
    )
    API_ID = input("Enter Your API ID - 16126827 ")
    API_HASH = input("Enter Your API HASH - d20e26deea812797eb00e731122a8372  ")

    print(
        "\n\nNow it will ask you to enter your phone number(+918553324207) and then follow the steps"
    )

    client = Client(":memory:", api_id=API_ID, api_hash=API_HASH)

    with client:
        session = client.export_session_string()
        print(
            "\nDone your session string will be saved in your saved messages! Don't Share it with anyone else."
        )
        client.send_message(
            "me",
            f"Your session String :\n\n`{session}`\n\nBy @vcplayerbot | [SkTechHub Product](https://t.me/sktechhub)",
        )
except Exception as ex:
    print(f"\nSome error occurred : {ex}")
