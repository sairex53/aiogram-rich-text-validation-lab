from __future__ import annotations

import argparse
import platform
from time import perf_counter

import pydantic

from rich_text_lab import build_envelope, nested_value


def measure(model: type, depths: list[int], label: str) -> None:
    print(label, flush=True)
    for depth in depths:
        payload = {"value": nested_value(depth)}
        started = perf_counter()
        model.model_validate(payload)
        elapsed_ms = (perf_counter() - started) * 1000
        print(f"  depth {depth:>3}: {elapsed_ms:9.3f} ms", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare recursive smart-union validation with tagged dispatch."
    )
    parser.add_argument(
        "--max-legacy-depth",
        type=int,
        default=4,
        help="highest depth for the intentionally slow legacy model (default: 4)",
    )
    parser.add_argument(
        "--fixed-depths",
        type=int,
        nargs="+",
        default=[1, 2, 3, 4, 5, 10, 50, 100],
        help="depths for the tagged model",
    )
    args = parser.parse_args()
    if args.max_legacy_depth < 1:
        parser.error("--max-legacy-depth must be at least 1")

    legacy = build_envelope(discriminated=False)
    tagged = build_envelope(discriminated=True)
    print(f"Python {platform.python_version()} / Pydantic {pydantic.__version__}")
    measure(legacy, list(range(1, args.max_legacy_depth + 1)), "Untagged union")
    measure(tagged, args.fixed_depths, "Tagged union")


if __name__ == "__main__":
    main()
