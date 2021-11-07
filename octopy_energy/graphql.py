# SPDX-FileCopyrightText: 2021 The octopy-energy Authors
#
# SPDX-License-Identifier: Apache-2.0
"""GraphQL client for Octopus Energy APIs."""

import datetime
from typing import Mapping, Optional, Tuple

import gql
import gql.transport.aiohttp

from . import Consumption, Tariff

_OCTOPUS_ENERGY_API_URL = "https://api.octopus.energy/v1/graphql/"


class ClientSession:

    _apikey: str
    _api_url: str

    _headers: Optional[Mapping[str, str]] = {}
    _authenticated_client: Optional[gql.Client] = None

    def __init__(self, apikey: str, api_url: str = _OCTOPUS_ENERGY_API_URL) -> None:
        self._apikey = apikey
        self._api_url = api_url

    def _get_transport(self) -> gql.transport.aiohttp.AIOHTTPTransport:
        return gql.transport.aiohttp.AIOHTTPTransport(
            self._api_url, headers=self._headers
        )

    def _get_client(self) -> gql.Client:
        return gql.Client(
            transport=self._get_transport(), fetch_schema_from_transport=False
        )

    async def __aenter__(self) -> "ClientSession":
        self._headers = {"Authorization": await self.obtain_kraken_token()}
        self._authenticated_client = self._get_client()
        await self._authenticated_client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._authenticated_client is not None:
            await self._authenticated_client.__aexit__(exc_type, exc, tb)
        self._authenticated_client = None

    async def obtain_kraken_token(self) -> str:
        # obtain_kraken_token is always called with a new session, since it does not
        # require authentication.
        async with self._get_client() as session:
            result = await session.execute(
                _MUTATION_OBTAIN_KRAKEN_TOKEN, variable_values={"apikey": self._apikey}
            )
            return result["obtainKrakenToken"]["token"]

    async def query_account_active_electricity_tariffs(
        self, account_number: str
    ) -> Mapping[str, Tariff]:
        assert self._authenticated_client is not None
        result = await self._authenticated_client.session.execute(
            _QUERY_ACCOUNT_ACTIVE_TARIFFS,
            variable_values={"accountNumber": account_number},
        )
        return {
            agreement["meterPoint"]["mpan"]: Tariff.from_graphql(agreement["tariff"])
            for agreement in result["account"]["electricityAgreements"]
        }

    async def query_account_current_electricity_consumption_and_tariff(
        self, account_number: str
    ) -> Mapping[str, Tuple[Mapping[str, Consumption], Tariff]]:
        assert self._authenticated_client is not None
        # We need to define a date to start looking up the current consumption.
        # Since we're looking for a gauge rather than a measurement, we aggregate by quarter
        # and that means we can just start from four months ago, asking for the last.
        start_date = datetime.datetime.utcnow().astimezone(
            datetime.timezone.utc
        ) - datetime.timedelta(weeks=16)

        raw_result = await self._authenticated_client.session.execute(
            _QUERY_ACCOUNT_CURRENT_CONSUMPTION_AND_TARIFF,
            variable_values={
                "accountNumber": account_number,
                "startAt": start_date.isoformat(),
            },
        )

        result = {}
        for property in raw_result["properties"]:
            for meter_point in property["electricityMeterPoints"]:
                # There should only be a single active tariff.
                assert len(meter_point["agreements"]) == 1

                tariff = Tariff.from_graphql(meter_point["agreements"][0])
                consumptions = {}
                for meter in meter_point["meters"]:
                    # There should only be one consumption value.
                    assert len(meter["consumption"]["edges"]) == 1
                    consumptions[meter["serialNumber"]] = Consumption.from_graphql(
                        meter["consumption"]["edges"][0]
                    )
                result[meter_point["mpan"]] = (consumptions, tariff)

        return result


_MUTATION_OBTAIN_KRAKEN_TOKEN = gql.gql(
    """
        mutation krakenTokenAuthentication($apikey: String!) {
            obtainKrakenToken(input:{APIKey:$apikey}) {
                token
            }
        }
    """
)

_QUERY_ACCOUNT_ACTIVE_TARIFFS = gql.gql(
    """
    query accountActiveTariff($accountNumber: String!) {
        account(accountNumber: $accountNumber) {
            electricityAgreements(active:true) {
                meterPoint{
                    mpan
                }
                tariff {
                    ... on StandardTariff {
                        displayName
                        unitRate
                    }
                }
            }
        }
    }
    """
)

_QUERY_ACCOUNT_CURRENT_CONSUMPTION_AND_TARIFF = gql.gql(
    """
        query consumptionAndRate($accountNumber:String!, $startAt:DateTime!) {
            properties(accountNumber: $accountNumber) {
                electricityMeterPoints {
                    mpan
                    meters {
                        serialNumber
                        consumption(last: 1, grouping:QUARTER, timezone:"UTC", startAt:$startAt) {
                            edges {
                                node {
                                    value
                                    startAt
                                    endAt
                                }
                            }
                        }
                    }
                    agreements {
                        tariff {
                            ... on StandardTariff {
                                displayName
                                unitRate
                            }
                        }
                    }
                }
            }
        }
    """
)
