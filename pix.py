#!/usr/bin/env python3

import argparse
import base64
import json
import hashlib
import re
import shlex
import subprocess
import sys
import tempfile
import textwrap


def run(
    cmd,
    verbose=True,
    cwd=None,
    check=True,
    capture_output=False,
    encoding="utf-8",
    **kwargs,
):
    if verbose:
        info = "$ "
        if cwd is not None:
            info += f"cd {cwd}; "
        info += " ".join(shlex.quote(c) for c in cmd)
        if capture_output:
            info += " >& ..."
        lines = textwrap.wrap(
            info,
            break_on_hyphens=False,
            break_long_words=False,
            replace_whitespace=False,
            subsequent_indent="  ",
        )
        print(" \\\n".join(lines))
    return subprocess.run(
        cmd,
        cwd=cwd,
        check=check,
        capture_output=capture_output,
        encoding=encoding,
        **kwargs,
    )


def deriv_add(deriv, check=True):
    return run(
        ["nix", "--extra-experimental-features", "nix-command", "derivation", "add"],
        input=json.dumps(deriv),
        check=check,
        capture_output=True,
    )


STORE_DIR = "/nix/store"


def discover_output(deriv, output):
    # Convert to ATerm
    initial_deriv = deriv_add(deriv).stdout.rstrip()
    with open(initial_deriv, "rb") as f:
        initial_deriv_hash = hashlib.file_digest(f, "sha256").digest()
    initial_deriv_hash_base16 = (
        base64.b16encode(initial_deriv_hash).decode("utf-8").lower()
    )
    name = deriv["name"]
    fingerprint = (
        f"output:{output}:sha256:{initial_deriv_hash_base16}:{STORE_DIR}:{name}"
    )
    fingerprint_hash = hashlib.sha256(fingerprint.encode("utf-8")).digest()
    fingerprint_hash_base32 = base64.b32encode(fingerprint_hash[:20]).decode("utf-8").lower()
    with tempfile.NamedTemporaryFile(mode="w+") as f:
        f.write(fingerprint)
        f.flush()
        result = run(
            [
                "nix-hash",
                "--type",
                "sha256",
                "--truncate",
                "--base32",
                "--flat",
                f.name,
            ],
            capture_output=True,
        )
    fingerprint_digest = result.stdout.rstrip()
    # TODO(max): Figure out why hashlib gives a different answer from nix-hash
    # assert fingerprint_digest == fingerprint_hash_base32, f"{fingerprint_digest} != {fingerprint_hash_base32}"
    store_path = f"{STORE_DIR}/{fingerprint_digest}-{name}"
    deriv["outputs"][output]["path"] = store_path
    deriv["env"][output] = store_path


def deriv_realize(deriv_path):
    return run(["nix-store", "--realize", deriv_path], capture_output=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    output = "out"
    deriv = {
        "name": "simple",
        "system": "x86_64-linux",
        "builder": "/bin/sh",
        "outputs": {output: {}},
        "inputSrcs": [],
        "inputDrvs": {},
        "env": {
            "out": "",
        },
        "args": ["-c", "echo 'hello world' > $out"],
    }

    discover_output(deriv, output)
    deriv_path = deriv_add(deriv).stdout.rstrip()
    output = deriv_realize(deriv_path).stdout.rstrip()
    print(f"Contents of output {output}:")
    with open(output, "r") as f:
        print(f.read())
