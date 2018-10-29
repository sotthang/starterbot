import json
import os
import time
import re
import urllib.request

from slackclient import SlackClient

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1  # 1 second delay between reading from RTM
EXAMPLE_COMMAND = {"오늘의날씨"}
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"


def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
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


def get_weather_data():
    res = urllib.request.urlopen(
        "https://lazzy-dev.kakao.com/v0.7/card/weather?lat=37.4018632&lon=127.1081415&test=1")
    data = json.load(res)

    return "{}의 {} 수치는 *{}* 입니다.".format(data['Content']['AirPollution']['combineAir']['now']['observatoryName'],
                                         data['Content']['AirPollution']['combineAir']['now']['text'],
                                         data['Content']['AirPollution']['combineAir']['now']['desc'])


def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "못알아먹겠다!! 한번 이렇게 말해보지 않을래? *{}*.".format(EXAMPLE_COMMAND.__str__())

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if EXAMPLE_COMMAND.__contains__(command):
        response = get_weather_data()

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text="몰라 안알랴쥼 파업할거야"
    )


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
