import json
import urllib.request
import urllib.parse
import boto3

secrets_client = boto3.client("secretsmanager")

ROUTES = {
    "alarm": {
        "secret_key": "opg-default",
        "emoji": ":warning:",
        "template": lambda e: (
            f":warning: *Deputy Reporting Integration OPG Alert* - {e.get('AlarmName', 'Unknown').capitalize()}\n\n "
            f"*Description:* {e.get('AlarmDescription', 'Unknown Description').capitalize()}\n\n "
            f"Please check cloudwatch logs in the relevant *Deputy Reporting Integration* account\n"
        ),
    },
    "critical_alarm": {
        "secret_key": "opg-default",
        "emoji": ":alert_slow:",
        "template": lambda e: (
            ":alert_slow: *CRITICAL ALERT - DEPUTY REPORTING INTEGRATION ACCOUNT* :alert_slow:\n\n"
            f"*Alarm:* {e.get('AlarmName', 'Unknown')}\n"
            f"*Description:* {e.get('AlarmDescription', 'Unknown Description').capitalize()}\n\n"
            "*Status:* CRITICAL\n\n"
            "Service may be degraded or unavailable. Actions should be taken immediately to investigate this alarm."
        ),
    },
}


def get_secret_value(secret_key: str) -> str:
    resp = secrets_client.get_secret_value(SecretId="slack-webhooks")
    return json.loads(resp["SecretString"])[secret_key]


def send_to_slack(webhook_url: str, text: str, emoji: str):
    payload = {"username": "aws", "icon_emoji": emoji, "text": text}
    data = urllib.parse.urlencode({"payload": json.dumps(payload)}).encode("utf-8")
    req = urllib.request.Request(webhook_url, data=data)
    with urllib.request.urlopen(req) as resp:
        return {"status": resp.getcode()}


REASONS_FOR_CRITICAL_ALARM = ["rest-api-5xx-errors"]


def handler(event, context):
    message = event
    event_type = ""

    try:
        if isinstance(event, dict) and "Records" in event:
            for record in event.get("Records", []):
                if not isinstance(record, dict):
                    continue

                sns = record.get("Sns")
                if not isinstance(sns, dict):
                    continue

                raw_message = sns.get("Message")
                if not isinstance(raw_message, str):
                    continue

                topic_arn = sns.get("TopicArn", "")
                if not isinstance(topic_arn, str):
                    continue

                if (
                    "custom_cloudwatch_alarms" in topic_arn
                    and "breakglass" not in raw_message
                ):
                    continue

                try:
                    parsed = json.loads(raw_message)
                except json.JSONDecodeError as e:
                    print(
                        f"Failed to parse SNS message as JSON: {e}, raw_message={raw_message}"
                    )
                    continue

                if not isinstance(parsed, dict):
                    continue

                message = parsed

                if "AlarmName" in parsed:
                    alarm_name = parsed.get("AlarmName", "")
                    alarm_state = parsed.get("NewStateValue", "")

                    if alarm_state != "ALARM":
                        print(
                            f"Ignoring {alarm_state} Slack notification for {alarm_name}"
                        )
                        return {"status": 200}

                    if any(
                        reason.lower() in alarm_name.lower()
                        for reason in REASONS_FOR_CRITICAL_ALARM
                    ):
                        event_type = "critical_alarm"
                    else:
                        event_type = "alarm"
                else:
                    event_type = parsed.get("type", "")

                break
    except Exception as e:
        print(f"Unexpected error while processing event: {e}")

    if not event_type:
        if isinstance(message, dict):
            event_type = message.get("type")
        else:
            event_type = ""

    if not event_type or event_type not in ROUTES:
        raise ValueError(f"Unknown event type: {event_type}, message: {message}")

    route = ROUTES[event_type]
    text = route["template"](message)
    emoji = route["emoji"] or (
        "✅" if message.get("status", "").lower() == "success" else "❌"
    )
    webhook_url = get_secret_value(route["secret_key"])

    print(f"Sending to Slack: {text}")

    return send_to_slack(webhook_url, text, emoji)
