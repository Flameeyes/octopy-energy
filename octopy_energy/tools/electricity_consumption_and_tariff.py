# SPDX-FileCopyrightText: 2021 The octopy-energy Authors
#
# SPDX-License-Identifier: Apache-2.0
"""Sample command that fetches the information needed for Home Assistant integration."""
import asyncio

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
    async with graphql.ClientSession(apikey) as session:
        result = await session.query_account_current_electricity_consumption_and_tariff(
            account_number
        )

        for mpan, (consumptions, tariff) in result.items():
            print(f"MPAN {mpan} — Tariff {tariff.display_name} ({tariff.rate} p/kWh)")
            for meter, consumption in consumptions.items():
                print(
                    f"  {meter} reads {consumption.consumption} kWh as of {consumption.interval_end}"
                )


if __name__ == "__main__":
    main()
