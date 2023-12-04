import json
from django.conf import settings
from .notifier.firebase_notifier import Notifier

creds_dict = json.loads((settings.FIREBASE_SERVICE_ACCOUNT_CREDENTIAL))
notifier = Notifier(creds_dict)

def pushNotification(fcmtokens, title, description):
    notifier.notify(title, description, fcmtokens, 'title')
