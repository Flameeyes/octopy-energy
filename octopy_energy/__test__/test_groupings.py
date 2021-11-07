# SPDX-FileCopyrightText: 2021 The octopy-energy Authors
#
# SPDX-License-Identifier: Apache-2.0

import unittest

from .. import ConsumptionGroupings


class GroupingsRestTest(unittest.TestCase):
    """Test the conversion of groupings to REST parameters."""

    def test_conversion_halfhour(self) -> None:
        """The half-hour grouping is the default, and does not have a matching value in REST."""
        self.assertEqual("", ConsumptionGroupings.HALF_HOUR.rest)

    def test_conversion_hour(self) -> None:
        self.assertEqual("hour", ConsumptionGroupings.HOUR.rest)


class GroupingsGraphQLTest(unittest.TestCase):
    """Test the conversion of groupings to GraphQL parameters."""

    def test_conversion_halfhour(self) -> None:
        self.assertEqual("HALF_HOUR", ConsumptionGroupings.HALF_HOUR.graphql)

    def test_conversion_hour(self) -> None:
        self.assertEqual("HOUR", ConsumptionGroupings.HOUR.graphql)
