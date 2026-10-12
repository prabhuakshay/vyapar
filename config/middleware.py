"""Project-wide middleware that does not belong to any one app."""

from typing import TYPE_CHECKING

from django.db import connection
from django.http import HttpResponse

if TYPE_CHECKING:
    from collections.abc import Callable

    from django.http import HttpRequest


class HealthCheckMiddleware:
    """Answer container health probes at /healthz/.

    Runs first in MIDDLEWARE so probes from 127.0.0.1 skip ALLOWED_HOSTS
    validation and the HTTPS redirect, which would otherwise fail them.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Return "ok" once the database is reachable; pass other paths on."""
        if request.path == "/healthz/":
            connection.ensure_connection()
            return HttpResponse("ok", content_type="text/plain")
        return self.get_response(request)
