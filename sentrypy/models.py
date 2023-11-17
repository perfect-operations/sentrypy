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
    """Implements an :class:`Organization`"""

    def project(self, project_slug: str) -> "Project":
        """Get a specific :class:`Project`

        Args:
            project_slug (str): The slug of the project to get

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
        """Get a specific :class:`Team`

        Args:
            team_slug (str): The slug of the team to get

        Official API Docs:
            `GET /api/0/teams/{organization_slug}/{team_slug}/ <https://docs.sentry.io/api/teams/retrieve-a-team/>`_
        """
        endpoint = f"https://sentry.io/api/0/teams/{self.slug}/{team_slug}/"
        return self.transceiver.get(endpoint, model=Team, organization_slug=self.slug)

    def create_team(self, team_slug: str) -> "Team":
        """Create a new :class:`Team`

        Args:
            team_slug (str): The slug of the team to create

        Official API Docs:
            `POST /api/0/organizations/{organization_slug}/teams/ <https://docs.sentry.io/api/teams/create-a-new-team/>`_
        """
        endpoint = f"https://sentry.io/api/0/organizations/{self.slug}/teams/"
        data = {"slug": team_slug}
        return self.transceiver.post(endpoint, data=data, model=Team, organization_slug=self.slug)

    def issue(self, id: str) -> "Issue":
        """Get a specific :class:`Issue`

        Args:
            id (str): The ID of the issue to retrieve.

        Official API Docs:
            `GET /api/0/organizations/{organization_slug}/issues/{issue_id}/ <https://docs.sentry.io/api/events/retrieve-an-issue/>`_
        """
        endpoint = f"https://sentry.io/api/0/organizations/{self.slug}/issues/{id}/"
        return self.transceiver.get(endpoint, model=Issue, organization_slug=self.slug)

    def integrations(
        self, provider_key: Optional[str] = None, features: Optional[List[str]] = None
    ) -> Iterator["Integration"]:
        """Get an iterator over all or specific :class:`Integrations <Integration>`

        Args:
            provider_key (str): Specific integration provider to filter by such as slack.
            features (List[str]): Integration features to filter by.

        Official API Docs:
            `GET  /api/0/organizations/{organization_slug}/integrations/ <https://docs.sentry.io/api/integrations/list-an-organizations-available-integrations/>`_
        """
        endpoint = f"https://sentry.io/api/0/organizations/{self.slug}/integrations/"
        print(endpoint)

        params_map = {"providerKey": provider_key, "features": features}
        params = {key: value for key, value in params_map.items() if value is not None}
        return self.transceiver.paginate_get(endpoint, params=params, model=Integration)


@dataclass
class Integration(BaseModel):
    """Implements an :class:`Integration`"""

    pass


@dataclass
class Team(BaseModel):
    """Implements a :class:`Team`"""

    organization_slug: str

    def delete(self):
        """Delete this :class:`Team`

        Official API Docs:
            `DELETE /api/0/teams/{organization_slug}/{team_slug}/ <https://docs.sentry.io/api/teams/delete-a-team/>`_
        """
        endpoint = f"https://sentry.io/api/0/teams/{self.organization_slug}/{self.slug}/"
        return self.transceiver.delete(endpoint)


@dataclass
class Project(BaseModel):
    """Implements a :class:`Project`"""

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

    def issues(self, query: Optional[str] = "unresolved") -> Iterator["Issue"]:
        """Get an iterator of all or specified :class:`Issues <Issue>` in the :class:`Project`

        Args:
            query (Optional[str]):
                An optional Sentry structured search query. If explicitly set to ``None``, an implied ``unresolved`` is assumed.

        Official API Docs:
            `GET /api/0/projects/{organization_slug}/{project_slug}/issues/ <https://docs.sentry.io/api/events/list-a-projects-issues/>`_
        """
        endpoint = f"https://sentry.io/api/0/projects/{self.organization_slug}/{self.slug}/issues/"
        params_map = {"query": "" if query is None else f"is:{query}"}
        params = {key: value for key, value in params_map.items() if value is not None}
        return self.transceiver.paginate_get(
            endpoint, params=params, model=Issue, organization_slug=self.organization_slug
        )

    def event_counts(self, resolution: Optional[EventResolution] = None) -> List:
        """Get event counts of project

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
        """Get all tag values of the project

        Args:
            key (str): The tag name to look up

        Official API Docs:
            `GET /api/0/projects/{organization_slug}/{project_slug}/tags/{key}/values/ <https://docs.sentry.io/api/projects/list-a-tags-values/>`_
        """
        endpoint = f"https://sentry.io/api/0/projects/{self.organization_slug}/{self.slug}/tags/{key}/values/"
        return self.transceiver.get(endpoint)

    def update_issues(
        self,
        *,
        by_id: Optional[Union[int, List[int]]] = None,
        by_status: Optional[str] = None,
        status: Optional[str] = None,
        status_details: Optional[str] = None,
        ignore_duration: Optional[int] = None,
        is_public: Optional[bool] = None,
        merge: Optional[bool] = None,
        assigned_to: Optional[str] = None,
        has_seen: Optional[bool] = None,
        is_bookmarked: Optional[bool] = None,
    ) -> List:
        """Update attributes of multiple issues of a project

        If any IDs are out of scope this operation will succeed without any data mutation.

        Args:
            by_id (Optional[Union[int, List[int]]]):
                A single ID or a list of IDs of the issues to be mutated. It is optional only
                if a status is mutated in which case an implicit update all is assumed.
            by_status (Optional[str]):
                Optionally limits the query to issues of the specified status. Valid values
                are ``resolved``, ``reprocessing``, ``unresolved``, and ``ignored``.
            status (str):
                The new status for the issues. Valid values are ``resolved``,
                ``resolvedInNextRelease``, ``unresolved``, and ``ignored``.
            status_details (object):
                Additional details about the resolution. Valid values are ``inRelease``,
                ``inNextRelease``, ``inCommit``, ``ignoreDuration``, ``ignoreCount``,
                ``ignoreWindow``, ``ignoreUserCount``, and ``ignoreUserWindow``.
            ignore_duration (int):
                The number of minutes to ignore this issue.
            is_public (bool):
                Sets the issue to public or private.
            merge (bool):
                Allows to merge or unmerge different issues.
            assigned_to (str):
                The actor ID (or username) of the user or team that should be assigned to this issue.
            has_seen (bool):
                In case this API call is invoked with a user context this allows changing of the
                flag that indicates if the user has seen the event.
            is_bookmarked (bool):
                In case this API call is invoked with a user context this allows changing of the bookmark flag.

        Official API Docs:
            `PUT /api/0/projects/{organization_slug}/{project_slug}/issues/ <https://docs.sentry.io/api/events/bulk-mutate-a-list-of-issues/>`_
        """
        endpoint = f"https://sentry.io/api/0/projects/{self.organization_slug}/{self.slug}/issues/"

        # How to use the same parameter multiple times: https://stackoverflow.com/a/23384253
        params_map = {"id": by_id, "status": by_status}
        params = {key: value for key, value in params_map.items() if value is not None}
        data_map = {
            "status": status,
            "statusDetails": status_details,
            "ignoreDuration": ignore_duration,
            "isPublic": is_public,
            "merge": merge,
            "assignedTo": assigned_to,
            "hasSeen": has_seen,
            "isBookmarked": is_bookmarked,
        }
        data = {key: value for key, value in data_map.items() if value is not None}
        return self.transceiver.put(endpoint, params=params, data=data)


@dataclass
class Issue(BaseModel):
    """Implements an :class:`Issue`"""

    organization_slug: str

    def events(self, full: bool = False) -> Iterator["Event"]:
        """Get an iterator of all :class:`Events <Event>` of this :class:`Issue`

        Args:
            full (bool): If this is set to true then the event payload will include the full event body

        Official API Docs:
            `GET /api/0/organizations/{organization_slug}/issues/{issue_id}/events/ <https://docs.sentry.io/api/events/list-an-issues-events/>`_
        """
        endpoint = f"https://sentry.io/api/0/organizations/{self.organization_slug}/issues/{self.id}/events/"
        params = {"full": full}
        return self.transceiver.paginate_get(endpoint, params=params, model=Event)

    def update(
        self,
        *,
        status: Optional[str] = None,
        assigned_to: Optional[str] = None,
        has_seen: Optional[bool] = None,
        is_bookmarked: Optional[bool] = None,
        is_subscribed: Optional[bool] = None,
        is_public: Optional[bool] = None,
    ) -> "Issue":
        """Update this issue

        Only the attributes submitted are modified.

        Args:
            status (str):
                The new status for the issues. Valid values are ``resolved``,
                ``reprocessing``, ``unresolved``, and ``ignored``.
            assigned_to (str):
                The actor id (or username) of the user or team that should be assigned to this issue.
            has_seen (bool):
                In case this API call is invoked with a user context this allows changing of
                the flag that indicates if the user has seen the event.
            is_bookmarked (bool):
                In case this API call is invoked with a user context this allows changing
                of the bookmark flag.
            is_subscribed (bool):
                In case this API call is invoked with a user context this allows the user
                to subscribe to workflow notifications for this issue.
            is_public (bool):
                Sets the issue to public or private.

        Official API Docs:
            `PUT /api/0/organizations/{self.organization_slug}/issues/{self.id}/ <https://docs.sentry.io/api/events/update-an-issue/>`_
        """
        data_map = {
            "status": status,
            "assignedTo": assigned_to,
            "hasSeen": has_seen,
            "isBookmarked": is_bookmarked,
            "isSubscribed": is_subscribed,
            "isPublic": is_public,
        }
        data = {key: value for key, value in data_map.items() if value is not None}

        endpoint = (
            f"https://sentry.io/api/0/organizations/{self.organization_slug}/issues/{self.id}/"
        )
        return self.transceiver.put(
            endpoint, data=data, model=Issue, organization_slug=self.organization_slug
        )


@dataclass
class Event(BaseModel):
    """Implements an :class:`Event`"""

    @property
    def tags(self):
        return {tag["key"]: tag["value"] for tag in self.json["tags"]}


@dataclass
class EventCount(BaseModel):
    pass
