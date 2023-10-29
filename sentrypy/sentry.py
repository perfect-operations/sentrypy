from dataclasses import dataclass, field, InitVar
from typing import Any, Dict, Iterator, List, Optional, Union
from enum import Enum

from .sentryrequesthandler import SentryRequestHandler, ResponseAttribute


@dataclass
class Sentry:
    """Top-level class to connect to the sentry.io API"""

    token: InitVar[str]
    handler: SentryRequestHandler = field(init=False)

    def __post_init__(self, token):
        self.handler = SentryRequestHandler(sentry=self, token=token)

    def organization(self, organization_slug: str) -> "Organization":
        """Returns the specified organization"""
        endpoint = f"https://sentry.io/api/0/organizations/{organization_slug}/"
        return self.handler.get(endpoint, model=Organization)

    def project(self, organization_slug: str, project_slug: str) -> "Project":
        """Returns the specified project"""
        endpoint = f"https://sentry.io/api/0/projects/{organization_slug}/{project_slug}/"
        return self.handler.get(endpoint, model=Project)

    def projects(self) -> Iterator["Project"]:
        """Returns an iterator over all projects"""
        endpoint = "https://sentry.io/api/0/projects/"
        return self.handler.paginate_get(endpoint, model=Project)


@dataclass
class BaseModel:
    sentry: Sentry
    json: Dict

    def __getitem__(self, key):
        return self.json[key]

    def __getattr__(self, key):
        # Only called if instance has no attribute named `key`
        # See: https://docs.python.org/3/reference/datamodel.html#object.__getattr__
        # Implemented to allow simple access to json model attributes via dot: model.json_key
        try:
            return self.json[key]
        except KeyError as e:
            raise AttributeError(e)


@dataclass
class Organization(BaseModel):
    pass


@dataclass
class Project(BaseModel):
    class EventResolution(Enum):
        S10 = "10s"
        H = "1h"
        D = "1d"

    @property
    def organization_slug(self):
        return self.organization["slug"]

    def issues(self) -> Iterator["Issue"]:
        endpoint = f"https://sentry.io/api/0/projects/{self.organization_slug}/{self.slug}/issues/"
        return self.sentry.handler.paginate_get(
            endpoint, model=Issue, organization_slug=self.organization_slug
        )

    def event_counts(self, resolution: Optional[EventResolution] = None) -> List:
        """Returns project event counts

        Endpoint documentation: https://docs.sentry.io/api/projects/retrieve-event-counts-for-a-project/
        """
        endpoint = f"https://sentry.io/api/0/projects/{self.organization_slug}/{self.slug}/stats/"
        params = dict()
        if resolution is not None:
            params["resolution"] = resolution.value
        return self.sentry.handler.get(endpoint, params=params)


@dataclass
class Issue(BaseModel):
    organization_slug: str

    def events(self) -> Iterator["Event"]:
        endpoint = f"https://sentry.io/api/0/organizations/{self.organization_slug}/issues/{self.id}/events/"
        return self.sentry.handler.paginate_get(endpoint, model=Event)


@dataclass
class Event(BaseModel):
    @property
    def tags(self):
        return {tag["key"]: tag["value"] for tag in self.json["tags"]}


@dataclass
class EventCount(BaseModel):
    pass
