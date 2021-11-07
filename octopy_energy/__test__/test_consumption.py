# SPDX-FileCopyrightText: 2021 The octopy-energy Authors
#
# SPDX-License-Identifier: Apache-2.0

import datetime
import json
import unittest

from .. import Consumption


class ConsumptionTest(unittest.TestCase):
    def test_from_rest(self) -> None:
        rest_result_str = """
            {"consumption":0.209,"interval_start":"2021-11-06T23:30:00Z","interval_end":"2021-11-07T00:00:00Z"}
        """

        self.assertEqual(
            Consumption(
                0.209,
                datetime.datetime(2021, 11, 6, 23, 30, 0, tzinfo=datetime.timezone.utc),
                datetime.datetime(2021, 11, 7, 0, 0, 0, tzinfo=datetime.timezone.utc),
            ),
            Consumption.from_rest(json.loads(rest_result_str)),
        )

    def test_from_graphql(self) -> None:
        gql_result_str = """
            {
                "node": {
                    "value": "0.20900000000000000000",
                    "startAt": "2021-11-06T23:30:00+00:00",
                    "endAt": "2021-11-07T00:00:00+00:00"
                }
            }
        """

        self.assertEqual(
            Consumption(
                0.209,
                datetime.datetime(2021, 11, 6, 23, 30, 0, tzinfo=datetime.timezone.utc),
                datetime.datetime(2021, 11, 7, 0, 0, 0, tzinfo=datetime.timezone.utc),
            ),
            Consumption.from_graphql(json.loads(gql_result_str)),
        )
