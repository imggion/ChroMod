#!/usr/bin/env python3
"""Reproduce the local ARM64 patch for chromatic-cli 1.2.1."""

import argparse
import hashlib
from pathlib import Path
import platform
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parent
SOURCE_SHA256 = "37257304b250634c586b0061e6f75dc1bec6ebaa57da1b9937106fa1fd370c70"
PATCH_OFFSET = 0x2B780
ORIGINAL_INSTRUCTION = bytes.fromhex("c0050054")  # b.eq 0x10002b838
REPLACEMENT_INSTRUCTION = bytes.fromhex("1f2003d5")  # nop


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source", type=Path,
        default=ROOT / "vendor/chromatic-cli-1.2.1-macos-arm64",
    )
    parser.add_argument("--output", type=Path, default=ROOT / "build/chromatic-cli")
    args = parser.parse_args()

    if platform.system() != "Darwin" or platform.machine() != "arm64":
        parser.error("This project targets macOS on Apple Silicon only.")
    if args.output.resolve() == args.source.resolve():
        parser.error("Source and output must differ; the original is preserved.")

    original = args.source.read_bytes()
    actual_hash = hashlib.sha256(original).hexdigest()
    if actual_hash != SOURCE_SHA256:
        parser.error(f"Unexpected source SHA-256: {actual_hash}; no patch applied.")
    if original[PATCH_OFFSET:PATCH_OFFSET + 4] != ORIGINAL_INSTRUCTION:
        parser.error("Unexpected instruction at the patch location.")

    # The SHA-1 lookup and comparisons still run. Only the conditional jump
    # into the known-title rejection is removed; execution falls through.
    patched = bytearray(original)
    patched[PATCH_OFFSET:PATCH_OFFSET + 4] = REPLACEMENT_INSTRUCTION

    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Sign a fresh inode so replacing a previously run executable does not
    # reuse macOS's cached code-signature state for that executable.
    with tempfile.NamedTemporaryFile(dir=args.output.parent, delete=False) as file:
        temporary = Path(file.name)
        file.write(patched)
    try:
        temporary.chmod(0o755)
        subprocess.run(["codesign", "--force", "--sign", "-", str(temporary)], check=True)
        subprocess.run(["codesign", "--verify", "--strict", str(temporary)], check=True)
        temporary.replace(args.output)
    finally:
        temporary.unlink(missing_ok=True)

    print(f"Patched executable: {args.output.resolve()}")
    print(f"SHA-256: {hashlib.sha256(args.output.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()
