"""
Starter bot for Slack
Starter code from https://www.fullstackpython.com/blog/build-first-slack-bot-python.html
Modifications by LOHM 2018
"""
import os
import time
import re
from slackclient import SlackClient
import slack_response

# instantiate Slack client
SLACK_CLIENT = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# getref_bot's user ID in Slack: value is assigned after the bot starts up
GETREF_ID = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def parse_bot_commands(slack_events, getref_id):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == getref_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    slash_command = ["/getscripture", "/getquran"]
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(' or '.join(slash_command))

    #this is where you put the command logic
    response = slack_response.SlackResponseBuilder(command, slash_command).response

    # Sends the response back to the channel
    SLACK_CLIENT.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

def main():
    """
        Slack client to fetch Scripture or Quran by reference
    """
    if SLACK_CLIENT.rtm_connect(with_team_state=False):
        print("Refbot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        getref_id = SLACK_CLIENT.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(SLACK_CLIENT.rtm_read(), getref_id)
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")


if __name__ == "__main__":
    main()