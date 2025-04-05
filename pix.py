#!/usr/bin/env python3

import argparse
import base64
import hashlib
import json
import pathlib
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
    try:
        return subprocess.run(
            cmd,
            cwd=cwd,
            check=check,
            capture_output=capture_output,
            encoding=encoding,
            **kwargs,
        )
    except subprocess.CalledProcessError as e:
        print(e)
        print(e.stdout)
        print(e.stderr)
        raise


def deriv_add(deriv):
    return run(
        ["nix", "--extra-experimental-features", "nix-command", "derivation", "add"],
        input=json.dumps(deriv),
        check=True,
        capture_output=True,
    )


def to_nix_base32(bytes_data):
    b32_alphabet = b"ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
    b32_nix = b"0123456789abcdfghijklmnpqrsvwxyz"
    trans = bytes.maketrans(b32_alphabet, b32_nix)
    return base64.b32encode(bytes_data[::-1]).translate(trans).decode("utf-8")


def compress_hash(h, newlen):
    result = bytearray(b"\0" * newlen)
    for i in range(len(h)):
        result[i % newlen] ^= h[i]
    return bytes(result[:newlen])


def nix_digest(fingerprint):
    # To make sure we have it right
    with tempfile.NamedTemporaryFile(mode="w+") as f:
        f.write(fingerprint)
        f.flush()
        return run(
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
        ).stdout.rstrip()


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
    fingerprint_digest = to_nix_base32(compress_hash(fingerprint_hash, 20))
    nix_fingerprint_digest = nix_digest(fingerprint)
    assert (
        fingerprint_digest == nix_fingerprint_digest
    ), f"{fingerprint_digest} != {nix_fingerprint_digest}"
    store_path = f"{STORE_DIR}/{fingerprint_digest}-{name}"
    deriv["outputs"][output]["path"] = store_path
    deriv["env"][output] = store_path


def deriv_realize(deriv_path):
    return run(["nix-store", "--realize", deriv_path], capture_output=True)


def source_file(filename):
    return run(
        [
            "nix",
            "--extra-experimental-features",
            "nix-command",
            "store",
            "add-file",
            filename,
        ],
        capture_output=True,
    )


def cc(filename):
    output = "out"
    deriv = {
        "name": "simple",
        "system": "x86_64-linux",
        "builder": "/bin/sh",
        "outputs": {output: {}},
        "inputSrcs": [filename],
        "inputDrvs": {},
        "env": {
            "out": "",
        },
        "args": [
            "-c",
            f"/nix/store/b1wvkjx96i3s7wblz38ya0zr8i93zbc5-coreutils-9.5/bin/mkdir -p $out/bin; /nix/store/m93xabjzcpx17qjj67qxpa68ykxfx75k-tcc-0.9.27-unstable-2025-01-06/bin/tcc {filename} -o $out/bin/hello",
        ],
    }
    discover_output(deriv, output)
    deriv_path = deriv_add(deriv).stdout.rstrip()
    output_path = deriv_realize(deriv_path).stdout.rstrip()
    return output_path


if __name__ == "__main__":
    output_path = source_file("test.c").stdout.rstrip()
    print(output_path)
    compiled = cc(output_path)
    print(compiled)
    # parser = argparse.ArgumentParser()
    # args = parser.parse_args()
    # output = "out"
    # deriv = {
    #     "name": "simple",
    #     "system": "x86_64-linux",
    #     "builder": "/bin/sh",
    #     "outputs": {output: {}},
    #     "inputSrcs": [],
    #     "inputDrvs": {},
    #     "env": {
    #         "out": "",
    #     },
    #     "args": ["-c", "echo 'hello world' > $out"],
    # }

    # discover_output(deriv, output)
    # deriv_path = deriv_add(deriv).stdout.rstrip()
    # output_path = deriv_realize(deriv_path).stdout.rstrip()
    # print(output_path)
