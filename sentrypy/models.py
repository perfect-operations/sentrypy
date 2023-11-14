from dataclasses import dataclass, field, InitVar
from typing import Any, Dict, Iterator, List, Optional, Union
from enum import Enum

from sentrypy.transceiver import Transceiver


@dataclass
class BaseModel:
    """Base class for all model classes like :class:`Project` or :class:`Event`.

    Responsible for pythonic attribute access to API json responses.

    If an API endpoint returns a response::

        {
            "id": 42,
            "title": ...
        }

    every object ``child_object`` of an inheriting class allows to access the attributes like this::

        # via dot, not working for keys that are not legal attribute names
        child_object.id

        # via brackets, works always
        child_object["id"]

    As :class:`BaseModel` is inherited by all models, all children support this access styles.
    """

    transceiver: Transceiver
    """HTTP level API wrapper."""

    json: Dict
    """Raw json data from API response.

    Accessible via brackets ``[]`` and ``dot.access`` of object.

    For more information see :class:`BaseModel` documentation."""

    def __getitem__(self, key):
        """Implements bracket access to :attr:`json` as described in :class:`BaseModel`."""

        # Implemented as dotted attribute access by __getattr__ fails when keys have spaces etc.
        return self.json[key]

    def __getattr__(self, key):
        """Implements dotted access to :attr:`json` as described in :class:`BaseModel`."""
        # Only called if instance has no attribute named `key`
        # See: https://docs.python.org/3/reference/datamodel.html#object.__getattr__
        # Implemented to allow simple access to json model attributes via dot: model.json_key
        try:
            return self.json[key]
        except KeyError as e:
            raise AttributeError(e)


@dataclass
class Organization(BaseModel):
    def project(self, project_slug: str) -> "Project":
        """Get the specified :class:`Project`

        Official API Docs:
            `GET /api/0/projects/{organization_slug}/{project_slug}/ <https://docs.sentry.io/api/projects/retrieve-a-project/>`_
        """
        endpoint = f"https://sentry.io/api/0/projects/{self.slug}/{project_slug}/"
        return self.transceiver.get(endpoint, model=Project)

    def teams(self) -> Iterator["Team"]:
        """Get an iterator over all :class:`Teams <Team>`

        Official API Docs:
            `GET /api/0/organizations/{organization_slug}/teams/ <https://docs.sentry.io/api/teams/list-an-organizations-teams/>`_
        """
        endpoint = f"https://sentry.io/api/0/organizations/{self.slug}/teams/"
        return self.transceiver.paginate_get(endpoint, model=Team, organization_slug=self.slug)

    def team(self, team_slug: str) -> "Team":
        """Get the specified :class:`Team`

        Official API Docs:
            `GET /api/0/teams/{organization_slug}/{team_slug}/ <https://docs.sentry.io/api/teams/retrieve-a-team/>`_
        """
        endpoint = f"https://sentry.io/api/0/teams/{self.slug}/{team_slug}/"
        return self.transceiver.get(endpoint, model=Team, organization_slug=self.slug)

    def create_team(self, team_slug: str) -> "Team":
        """Create an instance of :class:`Team`, send it to API, and return it

        Args:
            team_slug (str): The slug to assign to the team

        Official API Docs:
            `POST /api/0/organizations/{organization_slug}/teams/ <https://docs.sentry.io/api/teams/create-a-new-team/>`_
        """
        endpoint = f"https://sentry.io/api/0/organizations/{self.slug}/teams/"
        data = {"slug": team_slug}
        return self.transceiver.post(endpoint, data=data, model=Team, organization_slug=self.slug)


@dataclass
class Team(BaseModel):
    organization_slug: str

    def delete(self):
        """Mark :class:`Team` for deletion

        Official API Docs:
            `DELETE /api/0/teams/{organization_slug}/{team_slug}/ <https://docs.sentry.io/api/teams/delete-a-team/>`_
        """
        endpoint = f"https://sentry.io/api/0/teams/{self.organization_slug}/{self.slug}/"
        return self.transceiver.delete(endpoint)


@dataclass
class Project(BaseModel):
    class EventResolution(Enum):
        """Timespan to aggregate events counts

        Allowed values specified by project endpoint.
        """

        SECONDS = "10s"
        HOUR = "1h"
        DAY = "1d"

    @property
    def organization_slug(self):
        return self.organization["slug"]

    def issues(self) -> Iterator["Issue"]:
        endpoint = f"https://sentry.io/api/0/projects/{self.organization_slug}/{self.slug}/issues/"
        return self.transceiver.paginate_get(
            endpoint, model=Issue, organization_slug=self.organization_slug
        )

    def event_counts(self, resolution: Optional[EventResolution] = None) -> List:
        """Returns project event counts

        Sentry endpoint documentation: https://docs.sentry.io/api/projects/retrieve-event-counts-for-a-project/

        Args:
            resolution: Aggregate counts according to set value of :class:`Project.EventResolution`
        """
        endpoint = f"https://sentry.io/api/0/projects/{self.organization_slug}/{self.slug}/stats/"
        params = dict()
        if resolution is not None:
            params["resolution"] = resolution.value
        return self.transceiver.get(endpoint, params=params)

    def tag_values(self, key: str) -> List[Dict]:
        """Get a list of all used values of given tag

        Args:
            key (str): The tag name to look up

        Official API Docs:
            `GET /api/0/projects/{organization_slug}/{project_slug}/tags/{key}/values/ <https://docs.sentry.io/api/projects/list-a-tags-values/>`_
        """
        endpoint = f"https://sentry.io/api/0/projects/{self.organization_slug}/{self.slug}/tags/{key}/values/"
        return self.transceiver.get(endpoint)


@dataclass
class Issue(BaseModel):
    organization_slug: str

    def events(self) -> Iterator["Event"]:
        endpoint = f"https://sentry.io/api/0/organizations/{self.organization_slug}/issues/{self.id}/events/"
        return self.transceiver.paginate_get(endpoint, model=Event)


@dataclass
class Event(BaseModel):
    @property
    def tags(self):
        return {tag["key"]: tag["value"] for tag in self.json["tags"]}


@dataclass
class EventCount(BaseModel):
    pass
