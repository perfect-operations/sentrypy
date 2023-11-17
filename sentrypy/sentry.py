from dataclasses import dataclass, field, InitVar
from typing import Any, Dict, Iterator, List, Optional, Union

from sentrypy.transceiver import Transceiver
from sentrypy.models import (
    Organization,
    Project,
)


@dataclass
class Sentry:
    """Top-level class to connect to the sentry.io API

    Args:
        token: Your Sentry API token
    """

    token: str
    transceiver: Transceiver = field(init=False)

    def __post_init__(self):
        self.transceiver = Transceiver(token=self.token)

    def organization(self, organization_slug: str) -> Organization:
        """Get a specific :class:`Organization`

        Args:
            organization_slug (str): The slug of the organization to get

        Official API Docs:
            `GET /api/0/organizations/{organization_slug}/ <https://docs.sentry.io/api/organizations/retrieve-an-organization/>`_
        """
        endpoint = f"https://sentry.io/api/0/organizations/{organization_slug}/"
        return self.transceiver.get(endpoint, model=Organization)

    def projects(self) -> Iterator[Project]:
        """Get an iterator over all :class:`Projects <Project>`

        Official API Docs:
            `GET /api/0/projects/ <https://docs.sentry.io/api/projects/list-your-projects>`_
        """
        endpoint = "https://sentry.io/api/0/projects/"
        return self.transceiver.paginate_get(endpoint, model=Project)
