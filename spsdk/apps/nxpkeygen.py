#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2020-2021 NXP
#
# SPDX-License-Identifier: BSD-3-Clause

"""Module is used to generate public/private key and generating debug credential file."""
import logging
import os
import sys
from typing import List

import click

from spsdk import __version__ as version
from spsdk.apps.utils import catch_spsdk_error, check_destination_dir, check_file_exists
from spsdk.crypto import (
    ec,
    generate_ecc_private_key,
    generate_ecc_public_key,
    generate_rsa_private_key,
    generate_rsa_public_key,
    save_ecc_private_key,
    save_ecc_public_key,
    save_rsa_private_key,
    save_rsa_public_key,
)

logger = logging.getLogger(__name__)
LOG_LEVEL_NAMES = [name.lower() for name in logging._nameToLevel]


def get_list_of_supported_keys() -> List[str]:
    """Generate list with list of supported key types.

    :return: List of supported key types.
    """
    ret = ["rsa2048", "rsa3072", "rsa4096"]
    # pylint: disable=protected-access
    ret.extend(ec._CURVE_TYPES.keys())  # type: ignore

    return ret


@click.command(no_args_is_help=True)
@click.option(
    "-d",
    "--debug",
    "log_level",
    metavar="LEVEL",
    default="warning",
    help=f"Set the level of system logging output. "
    f'Available options are: {", ".join(LOG_LEVEL_NAMES)}',
    type=click.Choice(LOG_LEVEL_NAMES),
)
@click.option(
    "-k",
    "--key-type",
    type=click.Choice(get_list_of_supported_keys(), case_sensitive=False),
    metavar="KEY-TYPE",
    default="RSA2048",
    help=f"""\b
        Set of the supported key types. Default is RSA2048.

        Note: NXP DAT protocol is using encryption keys by this table:

        NXP Protocol Version                Encryption Type
            1.0                                 RSA 2048
            1.1                                 RSA 4096
            2.0                                 SECP256R1
            2.1                                 SECP384R1
            2.2                                 SECP521R1

        All possible options:
        {", ".join(get_list_of_supported_keys())}.
        """,
)
@click.option(
    "--password",
    "password",
    metavar="PASSWORD",
    help="Password with which the output file will be encrypted. "
    "If not provided, the output will be unencrypted.",
)
@click.argument("path", type=click.Path(file_okay=True))
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Force overwriting of an existing file.",
)
@click.version_option(version, "--version")
def main(log_level: str, key_type: str, path: str, password: str, force: bool) -> int:
    """NXP Key Generator Tool.

    \b
    PATH    - output file path, where the key pairs (private and public key) will be stored.
              Each key will be stored in separate file (.pub and .pem).
    """
    logging.basicConfig(level=log_level.upper())

    key_param = key_type.lower().strip()
    is_rsa = "rsa" in key_param

    check_destination_dir(path, force)
    check_file_exists(path, force)
    pub_key_path = os.path.splitext(path)[0] + ".pub"
    check_file_exists(pub_key_path, force)

    if is_rsa:
        logger.info("Generating RSA private key...")
        priv_key_rsa = generate_rsa_private_key(key_size=int(key_param.replace("rsa", "")))
        logger.info("Generating RSA corresponding public key...")
        pub_key_rsa = generate_rsa_public_key(priv_key_rsa)
        logger.info("Saving RSA key pair...")
        save_rsa_private_key(priv_key_rsa, path, password if password else None)
        save_rsa_public_key(pub_key_rsa, pub_key_path)
    else:
        logger.info("Generating ECC private key...")
        priv_key_ec = generate_ecc_private_key(curve_name=key_param)
        logger.info("Generating ECC public key...")
        pub_key_ec = generate_ecc_public_key(priv_key_ec)
        logger.info("Saving ECC key pair...")
        save_ecc_private_key(priv_key_ec, path, password if password else None)
        save_ecc_public_key(pub_key_ec, pub_key_path)
    return 0


@catch_spsdk_error
def safe_main() -> None:
    """Call the main function."""
    sys.exit(main())  # pragma: no cover  # pylint: disable=no-value-for-parameter


if __name__ == "__main__":
    safe_main()  # pragma: no cover
