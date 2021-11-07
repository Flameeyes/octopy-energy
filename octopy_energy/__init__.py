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
