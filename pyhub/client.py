from __future__ import annotations
from urllib.parse import urlparse, parse_qs
import requests

API_VERSION = "v2"
DOCKER_HUB_URL = f"https://hub.docker.com/{API_VERSION}"

DEFAULT_TAG_FIELDS = ["name", "full_size", "tag_last_pulled", "tag_last_pushed"]


class DockerhubClient:
    base_url = DOCKER_HUB_URL

    def __init__(self, username: str, password: str, org: str) -> None:
        self.username = username
        self.password = password
        self.org = org
        self._token = ""

    @property
    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

    @property
    def logged(self) -> bool:
        return bool(self._token)

    def _get_url(self, endpoint: str) -> str:
        return f"{self.base_url}/{endpoint}"

    def login(self) -> None:
        """Auth method to retrieve token"""

        response = requests.post(
            self._get_url("users/login/"),
            data={"username": self.username, "password": self.password},
        )
        self._token = response.json().get("token")

    def _make_request(self, method: str, endpoint: str, params: dict):
        if not self.logged:
            self.login()

        make_request = requests.get if method == "GET" else requests.post
        vals = {"params": params} if method == "GET" else {"json": params}

        response = make_request(self._get_url(endpoint), headers=self.headers, **vals)
        return response.json()

    def _get(self, endpoint: str, params: dict) -> dict:
        return self._make_request("GET", endpoint, params)

    def _post(self, endpoint: str, data: dict) -> dict:
        return self._make_request("POST", endpoint, data)

    def create_repository(self, name: str, private: bool = True) -> bool:
        """Create a new repository"""

        res = self._post(
            "repositories/",
            {
                "is_private": private,
                "name": name,
                "namespace": self.org,
            },
        )

        return res.get(name) == name

    def get_repositories(
        self, page_size: int = 25, ordering: str = "last_updated"
    ) -> list[str]:
        """Fetch repositories from organization"""

        res = self._get(
            f"repositories/{self.org}",
            {
                "page_size": page_size,
                "ordering": ordering,
            },
        )

        return [item["name"] for item in res["results"]]

    def get_groups(self, page: int = 1, page_size: int = 25) -> dict:
        """Fetch groups (aka teams) from organization"""

        res = self._get(
            f"orgs/{self.org}/groups",
            {
                "page": page,
                "page_size": page_size,
            },
        )
        return {item["name"]: item["id"] for item in res["results"]}

    def get_tags(
        self,
        repository: str,
        page: int = 1,
        page_size: int = 100,
        ordering="last_updated",
        fields=["name"],
        follow: bool = True,
    ) -> dict:
        """List all tags from a repository"""

        results = []
        while page:
            res = self._get(
                f"repositories/{self.org}/{repository}/tags",
                {
                    "page": page,
                    "page_size": page_size,
                    "ordering": ordering,
                },
            )
            url = res.get("next")
            parsed_url = urlparse(url)
            query = parse_qs(parsed_url.query)

            if "page" in query:
                page = int(query.get("page")[0])
            else:
                page = False

            if not follow:
                break

            results += res["results"]

        if len(fields) == 1:
            return [v for item in results for k, v in item.items() if k == fields[0]]

        def _filter(vals):
            return {k: v for k, v in vals.items() if k in fields}

        return list(map(_filter, results))

    def get_group_by_name(self, name: str) -> int | None:
        groups = self.get_groups()
        return groups.get(name)

    def set_permissions(
        self, repository: str, group_id: int, permission: str = "write"
    ):
        """Apply group and permission on a repository"""

        self._post(
            f"repositories/{self.org}/{repository}/groups/",
            {
                "group_id": group_id,
                "permission": permission,
            },
        )
