# SPDX-FileCopyrightText: 2021 The octopy-energy Authors
#
# SPDX-License-Identifier: Apache-2.0
"""Common data types for Octopus Energy client."""

import dataclasses
import datetime
import enum
from typing import Any

import iso8601


@enum.unique
class ConsumptionGroupings(enum.Enum):
    HALF_HOUR = ""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"

    @property
    def rest(self) -> str:
        return self.value

    @property
    def graphql(self) -> str:
        return self.name


@dataclasses.dataclass
class Consumption:
    consumption: float
    interval_start: datetime.datetime
    interval_end: datetime.datetime

    @classmethod
    def from_rest(cls, json_dict: dict[str, Any]) -> "Consumption":
        return Consumption(
            json_dict["consumption"],
            iso8601.parse_date(json_dict["interval_start"]),
            iso8601.parse_date(json_dict["interval_end"]),
        )

    @classmethod
    def from_graphql(cls, gql_dict: dict[str, Any]) -> "Consumption":
        if "node" in gql_dict:
            return cls.from_graphql(gql_dict["node"])

        return Consumption(
            float(gql_dict["value"]),
            iso8601.parse_date(gql_dict["startAt"]),
            iso8601.parse_date(gql_dict["endAt"]),
        )


@dataclasses.dataclass
class Tariff:
    display_name: str
    rate: float

    @classmethod
    def from_graphql(cls, gql_dict: dict[str, Any]) -> "Tariff":
        if "tariff" in gql_dict:
            return cls.from_graphql(gql_dict["tariff"])

        return Tariff(gql_dict["displayName"], gql_dict["unitRate"])
