# SPDX-FileCopyrightText: 2021 The octopy-energy Authors
#
# SPDX-License-Identifier: Apache-2.0
"""Simple command line tool to fetch the current electricity tariff on account."""
import asyncio
import csv
import sys

import click

from .. import graphql


@click.command()
@click.option(
    "--apikey",
    required=True,
    type=str,
    help="The API key to authenticate to Octopus API.",
)
@click.option(
    "--account-number",
    required=True,
    type=str,
    help="The account number to fetch the tariff for.",
)
def main(*args, **kwargs) -> None:
    return asyncio.run(amain(*args, **kwargs))


async def amain(apikey: str, account_number: str) -> None:
    writer = csv.writer(sys.stdout)
    writer.writerow(["MPAN", "Tariff Name", "Unit Rate"])
    async with graphql.ClientSession(apikey) as session:
        result = await session.query_account_active_electricity_tariffs(account_number)
        for mpan, tariff in result.items():
            writer.writerow([mpan, tariff.display_name, tariff.rate])


if __name__ == "__main__":
    main()
