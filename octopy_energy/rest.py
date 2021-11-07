# SPDX-FileCopyrightText: 2021 The octopy-energy Authors
#
# SPDX-License-Identifier: Apache-2.0
"""REST client for Octopus Energy APIs."""

import datetime
from collections.abc import Iterator
from typing import AsyncIterator, Optional, Union, cast

import aiohttp
import yarl

from . import Consumption, ConsumptionGroupings

_OCTOPUS_ENERGY_BASE_URL = "https://api.octopus.energy/"


class ClientSession(aiohttp.ClientSession):
    """Façade for aiohttp.ClientSession supporting Octopus Energy API."""

    _base_api_url: yarl.URL

    def __init__(self, apikey: str, *args, **kwargs) -> None:
        if "auth" in kwargs:
            raise ValueError("Invalid argument 'auth', please only provide 'apikey'.")
        if not kwargs.pop("raise_for_status", True):
            raise ValueError("Invalid argument 'raise_for_status', please remove.")

        # We save this separately because some of the APIs use fully qualified URLs, so
        # we cannot let aiohttp know about the base_url!
        self._base_api_url = yarl.URL(kwargs.pop("base_url", _OCTOPUS_ENERGY_BASE_URL))

        super().__init__(
            *args, auth=aiohttp.BasicAuth(apikey), raise_for_status=True, **kwargs
        )

    # This is because mypy complains about the additional methods otherwise.
    async def __aenter__(self):
        return cast("ClientSession", await super().__aenter__())

    def api_url(self, api_url: Union[str, yarl.URL]) -> yarl.URL:
        api_url = yarl.URL(api_url)

        if not api_url.is_absolute():
            return self._base_api_url.join(api_url)

        return api_url

    def electricity_meter_consumption(
        self, *args, **kwargs
    ) -> AsyncIterator[Consumption]:
        return ElectricityMeterConsumption(self, *args, **kwargs)


class ElectricityMeterConsumption:

    _results: Iterator[Consumption] = iter(())
    _next_url: Optional[yarl.URL] = None

    def __init__(
        self,
        session: ClientSession,
        mpan: str,
        serial_number: str,
        period_range: Union[None, tuple[datetime.datetime, datetime.datetime]] = None,
        grouping: ConsumptionGroupings = ConsumptionGroupings.HALF_HOUR,
    ) -> None:
        self._session = session

        self._next_url = session.api_url(
            f"/v1/electricity-meter-points/{mpan}/meters/{serial_number}/consumption"
        )

        params = {}
        if period_range:
            period_from, period_to = period_range
            params["period_from"] = period_from.isoformat()
            params["period_to"] = period_to.isoformat()

        # Half-hour grouping requires *not* passing a parameter at all.
        if grouping.rest:
            params["group_by"] = grouping.rest

        if params:
            self._next_url = self._next_url.with_query(**params)

    def __aiter__(self) -> AsyncIterator[Consumption]:
        return self

    async def __anext__(self) -> Consumption:
        try:
            return next(self._results)
        except StopIteration:
            if self._next_url is None:
                raise StopAsyncIteration()

            async with self._session.get(self._next_url) as response:
                response_dict = await response.json()

            self._next_url = response_dict["next"]
            self._results = (
                Consumption.from_rest(result) for result in response_dict["results"]
            )

            return await self.__anext__()
