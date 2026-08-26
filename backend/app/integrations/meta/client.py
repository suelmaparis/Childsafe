import json
import urllib.error
import urllib.parse
import urllib.request

from app.core.settings import (
    META_ACCESS_TOKEN,
)


class MetaApiError(Exception):
    pass


class MetaClient:

    def __init__(
        self,
        access_token: str | None = None,
        api_version: str = "v24.0",
    ):
        self.access_token = (
            access_token
            or META_ACCESS_TOKEN
        )

        self.api_version = api_version

        self.base_url = (
            f"https://graph.facebook.com/"
            f"{self.api_version}"
        )

    def is_configured(self) -> bool:
        return bool(
            self.access_token
        )

    def get(
        self,
        path: str,
        params: dict | None = None,
    ) -> dict:
        if not self.access_token:
            raise MetaApiError(
                "Meta access token is not configured."
            )

        query = dict(
            params or {}
        )

        query["access_token"] = (
            self.access_token
        )

        url = (
            f"{self.base_url}/"
            f"{path.lstrip('/')}"
        )

        encoded_query = (
            urllib.parse.urlencode(
                query
            )
        )

        request_url = (
            f"{url}?{encoded_query}"
        )

        return self.get_url(
            request_url
        )

    def get_url(
        self,
        url: str,
    ) -> dict:
        request = urllib.request.Request(
            url,
            method="GET",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=20,
            ) as response:
                body = response.read()

        except urllib.error.HTTPError as exc:
            body = exc.read()

            try:
                error_data = json.loads(
                    body.decode("utf-8")
                )

                message = (
                    error_data
                    .get("error", {})
                    .get(
                        "message",
                        str(exc),
                    )
                )

            except Exception:
                message = str(exc)

            raise MetaApiError(
                message
            ) from exc

        except urllib.error.URLError as exc:
            raise MetaApiError(
                f"Unable to reach Meta API: "
                f"{exc.reason}"
            ) from exc

        try:
            return json.loads(
                body.decode("utf-8")
            )

        except json.JSONDecodeError as exc:
            raise MetaApiError(
                "Meta API returned invalid JSON."
            ) from exc

    def get_all_pages(
        self,
        path: str,
        params: dict | None = None,
        max_pages: int = 10,
    ) -> list[dict]:
        items = []

        data = self.get(
            path,
            params=params,
        )

        page_count = 0

        while (
            data
            and page_count < max_pages
        ):
            page_count += 1

            items.extend(
                data.get(
                    "data",
                    []
                )
            )

            next_url = (
                data.get(
                    "paging",
                    {}
                ).get(
                    "next"
                )
            )

            if not next_url:
                break

            data = self.get_url(
                next_url
            )

        return items

    def get_instagram_media(
        self,
        instagram_user_id: str,
        limit: int = 25,
    ) -> list[dict]:
        return self.get_all_pages(
            f"{instagram_user_id}/media",
            params={
                "fields": (
                    "id,"
                    "caption,"
                    "media_type,"
                    "media_url,"
                    "permalink,"
                    "timestamp"
                ),
                "limit": limit,
            },
        )
    def get_facebook_posts(
    self,
    page_id: str,
    limit: int = 25,
) -> list[dict]:
        return self.get_all_pages(
        f"{page_id}/posts",
        params={
            "fields": (
                "id,"
                "message,"
                "permalink_url,"
                "created_time"
            ),
            "limit": limit,
        },
    )