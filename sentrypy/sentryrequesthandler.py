import requests
from enum import Enum
from dataclasses import dataclass
from typing import Any, Dict, Iterator, List, Optional

ResponseAttribute = Enum("ResponseContent", ["ALL", "JSON", "HEADERS"])


@dataclass
class SentryRequestHandler:
    sentry: "Sentry"
    token: str

    @property
    def auth_headers(self) -> Dict:
        return {"Authorization": f"Bearer {self.token}"}

    def get(
        self,
        endpoint: str,
        *,
        params: Optional[Dict] = None,
        response_attribute: Optional[ResponseAttribute] = ResponseAttribute.JSON,
        model: Optional[type] = None,
        **kwargs,
    ):
        """Perform authenticated get request and return selected attribute of HTTP response

        Args:
            endpoint: Where to send the get request
            params: Parameters to add to endpoint
            response_attribute: Which part of the HTTP response to return
            model: If response_attribute is JSON, which class to instantiate
            **kwargs: Additional arguments for model class constructor
        """
        if params is None:
            params = dict()
        response = requests.get(url=endpoint, headers=self.auth_headers, params=params)
        response.raise_for_status()

        # Return only parts of response that have been selected by response_attribute
        attr_mapper = {
            ResponseAttribute.ALL: lambda x: x,
            ResponseAttribute.JSON: lambda x: x.json(),
            ResponseAttribute.HEADERS: lambda x: x.headers,
        }
        result = attr_mapper[response_attribute](response)
        if response_attribute == ResponseAttribute.JSON and model is not None:
            return model(sentry=self.sentry, json=result, **kwargs)
        else:
            return result

    def paginate_get(
        self,
        endpoint,
        *,
        params: Optional[Dict] = None,
        model: Optional[type] = None,
        max_results: int = None,
        **kwargs,
    ) -> Iterator:
        """Paginate endpoint and generate model instances

        Args:
            endpoint: The URL to send a get request to
            params: Parameters to add to endpoint
            model: Instantiates objects from this class
            max_results: Return no more objects, unlimited by default
            **kwargs: Additional arguments for model class constructor
        """
        # Implementation inspired from: https://www.pretzellogix.net/2021/12/19/step-13-paging-the-endpoints/
        if params is None:
            params = dict()
        counter = 0
        plink = PaginationLink(url=endpoint, results=True)
        while plink.results:
            response = self.get(
                endpoint=plink.url, response_attribute=ResponseAttribute.ALL, params=params
            )
            plink = PaginationLink.from_header(response.headers, direction="next")
            for item in response.json():
                if model is None:
                    yield item
                else:
                    yield model(sentry=self.sentry, json=item, **kwargs)
                counter += 1
                if max_results is not None and counter >= max_results:
                    return


@dataclass
class PaginationLink:
    url: str
    results: bool
    rel: Optional[str] = None
    cursor: Optional[str] = None

    @classmethod
    def from_header(cls, header: Dict, direction: str) -> "PaginationLink":
        """Parses the response header and returns previous or next pagination link"""
        index_map = {
            "previous": 0,
            "next": 1,
        }
        tokens = header["link"].split(", ")[index_map[direction]].split("; ")
        raw = dict()
        raw["url"] = tokens[0][1:-1]
        for key in ["rel", "results", "cursor"]:
            for t in tokens[1:]:
                if key in t:
                    raw[key] = t.split("=")[1][1:-1]
        raw["results"] = True if raw["results"] == "true" else False
        return cls(**raw)
