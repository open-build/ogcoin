#!/usr/bin/env python3
"""
Create an unsigned Stellar XDR that links the OGC issuer to a home domain.

This script never asks for or handles a secret key. Sign the output XDR with the
issuer account in a wallet or Stellar Lab, then submit the signed transaction.
"""

import argparse
import sys

try:
    from stellar_sdk import Network, Server, TransactionBuilder
except ImportError:
    print("stellar-sdk is required. Install with: pip install stellar-sdk", file=sys.stderr)
    raise


NETWORKS = {
    "public": {
        "horizon": "https://horizon.stellar.org",
        "passphrase": Network.PUBLIC_NETWORK_PASSPHRASE,
        "lab": "https://lab.stellar.org/transaction/sign",
    },
    "testnet": {
        "horizon": "https://horizon-testnet.stellar.org",
        "passphrase": Network.TESTNET_NETWORK_PASSPHRASE,
        "lab": "https://lab.stellar.org/transaction/sign",
    },
}


def build_home_domain_xdr(issuer: str, home_domain: str, network: str) -> str:
    network_config = NETWORKS[network]
    server = Server(network_config["horizon"])
    source_account = server.load_account(issuer)

    transaction = (
        TransactionBuilder(
            source_account=source_account,
            network_passphrase=network_config["passphrase"],
            base_fee=100,
        )
        .append_set_options_op(home_domain=home_domain)
        .set_timeout(300)
        .build()
    )
    return transaction.to_xdr()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create an unsigned set_options XDR for the OGC issuer home_domain."
    )
    parser.add_argument(
        "--issuer",
        default="GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57",
        help="Issuer public key",
    )
    parser.add_argument(
        "--home-domain",
        default="www.opengreencoin.com",
        help="Domain that hosts /.well-known/stellar.toml",
    )
    parser.add_argument(
        "--network",
        choices=sorted(NETWORKS),
        default="public",
        help="Stellar network",
    )
    args = parser.parse_args()

    xdr = build_home_domain_xdr(args.issuer, args.home_domain, args.network)
    print("Unsigned XDR:")
    print(xdr)
    print()
    print("Next step:")
    print("Sign this XDR with the issuer account, then submit it to Stellar.")
    print(f"Stellar Lab signer: {NETWORKS[args.network]['lab']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
