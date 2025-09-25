import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from config import SENTRY_DSN

def init_sentry():
    if not SENTRY_DSN:
        print("SENTRY_DSN not set. Skipping Sentry initialization.")
        return

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[SqlalchemyIntegration(), FastApiIntegration()],
        traces_sample_rate=1.0, # TODO: Adjust this value in production
        environment="development", # TODO: Change to "production" in production
        send_default_pii=True
    )
    print("Sentry initialized.")
    
# TODO: replace except Exception blocks with sentry capture_exception