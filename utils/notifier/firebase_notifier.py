import firebase_admin
from firebase_admin import credentials, messaging


class Notifier:
    def notify(self, title, body, tokens, tag):
        message = messaging.MulticastMessage(
            android=messaging.AndroidConfig(
                priority="high",
                notification=messaging.AndroidNotification(
                    title=title,
                    body=body,
                    channel_id="sound_notifier",
                    sound="ringer",
                    tag=tag,
                ),
            ),
            tokens=tokens,
        )

        response = messaging.send_multicast(message)
        response

    def __init__(self, creds):
        cred = credentials.Certificate(creds)
        firebase_admin.initialize_app(cred)
