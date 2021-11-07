# SPDX-FileCopyrightText: 2021 The octopy-energy Authors
#
# SPDX-License-Identifier: Apache-2.0
"""Simple command line tool to fetch the electricity readings."""
import asyncio

import click

from .. import rest


@click.command()
@click.option(
    "--apikey",
    required=True,
    type=str,
    help="The API key to authenticate to Octopus API.",
)
@click.option(
    "--mpan",
    required=True,
    type=str,
    help="The MPAN number of the electricity meter point to query.",
)
@click.option(
    "--meter", required=True, type=str, help="The meter serial number to query."
)
def main(*args, **kwargs) -> None:
    return asyncio.run(amain(*args, **kwargs))


async def amain(apikey: str, mpan: str, meter: str) -> None:
    async with rest.ClientSession(apikey=apikey) as session:
        async for reading in session.electricity_meter_consumption(mpan, meter):
            print(reading)


if __name__ == "__main__":
    main()
