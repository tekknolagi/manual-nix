#!/usr/bin/env python3

import argparse
import json
import re
import shlex
import subprocess
import sys
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


def discover_output(deriv):
    # TODO(max): Figure out a better way to do this programmatically
    result = deriv_add(deriv, check=False)
    match = re.search(r"should be '(.+)'", result.stderr)
    assert match
    expected_out_path = match.group(1)
    deriv["outputs"]["out"]["path"] = expected_out_path
    deriv["env"]["out"] = expected_out_path
    return result.stderr


def deriv_realize(deriv_path):
    return run(["nix-store", "--realize", deriv_path], capture_output=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    deriv = {
        "name": "simple",
        "system": "x86_64-linux",
        "builder": "/bin/sh",
        "outputs": {
            "out": {"path": "/nix/store/00000000000000000000000000000000-simple"}
        },
        "inputSrcs": [],
        "inputDrvs": {},
        "env": {
            "out": "/nix/store/00000000000000000000000000000000-simple",
        },
        "args": ["-c", "echo 'hello world' > $out"],
    }
    discover_output(deriv)
    deriv_path = deriv_add(deriv).stdout.rstrip()
    output = deriv_realize(deriv_path).stdout.rstrip()
    print(f"{output}:")
    with open(output, "r") as f:
        print(f.read())
