import os

from dotenv import load_dotenv


load_dotenv()


def env_bool(
    name: str,
    default: bool = False,
) -> bool:
    value = os.getenv(
        name,
        str(default),
    )

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


MOCK_INSTAGRAM_ENABLED = env_bool(
    "MOCK_INSTAGRAM_ENABLED",
    True,
)

META_INSTAGRAM_ENABLED = env_bool(
    "META_INSTAGRAM_ENABLED",
    False,
)

META_FACEBOOK_ENABLED = env_bool(
    "META_FACEBOOK_ENABLED",
    False,
)


META_ACCESS_TOKEN = os.getenv(
    "META_ACCESS_TOKEN"
)

META_APP_ID = os.getenv(
    "META_APP_ID"
)

META_APP_SECRET = os.getenv(
    "META_APP_SECRET"
)
MONITORING_ENABLED = env_bool(
    "MONITORING_ENABLED",
    True,
)

MONITORING_INTERVAL_MINUTES = int(
    os.getenv(
        "MONITORING_INTERVAL_MINUTES",
        "60",
    )
)
META_INSTAGRAM_USER_ID = os.getenv(
    "META_INSTAGRAM_USER_ID"
)