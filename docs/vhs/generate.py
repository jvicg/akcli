#!/usr/bin/env python3

"""
Script to run a dummy HTTPS server that will be use to answer the requests made on the `vhs` scripts.
This allow us to manipulate the answer to obtain the gifs without leaking any sensible data from the real Akamai API.
"""

import contextlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, ".")

from tests.fixtures import ACCESS_TOKEN, CLIENT_TOKEN, EDGERC_TEMPLATE, run_https_server


def _gen_edgerc(https_server: str) -> Path:
    """
    Helper function to generate `edgerc` file content using a template.
    It adds in the ip and port of the dummy server in to the host properties of the edgerc.
    """
    edgerc_content = (
        EDGERC_TEMPLATE.read_text()
        .format(
            https_server=https_server,
            access_token=ACCESS_TOKEN,
            client_token=CLIENT_TOKEN,
        )
        .strip()
    )
    edgerc = Path(tempfile.mkdtemp()) / ".edgerc"
    edgerc.write_text(edgerc_content)
    return edgerc


def main():
    """
    Run the server and execute all the vhs scripts passing them a dummy `.edgerc` file that
    points to the dummy server by environmental variable.
    """
    with run_https_server() as server:
        script_dir = Path(__file__).parent

        # Get server socket
        host, port = server.socket.getsockname()
        https_server = f"{host}:{port}"

        edgerc = _gen_edgerc(https_server)

        try:
            # Add edgerc path to env var
            env = os.environ.copy()
            env["AKCLI_TEST_EDGERC"] = str(edgerc)

            with contextlib.suppress(KeyboardInterrupt):
                for file in script_dir.glob("*.tape"):
                    if file.name == "config.tape":
                        continue

                    cmd = ["vhs", file]
                    subprocess.run(cmd, env=env)

        finally:
            edgerc.unlink()
            edgerc.parent.rmdir()


if __name__ == "__main__":
    main()
