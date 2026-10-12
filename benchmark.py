from __future__ import annotations

import argparse
import platform
import statistics
from time import perf_counter

import pydantic

from rich_text_lab import build_envelope, nested_value


def measure(model: type, depths: list[int], label: str, repeats: int) -> None:
    print(label, flush=True)
    for depth in depths:
        payload = {"value": nested_value(depth)}
        model.model_validate(payload)  # Warm up the model before timing.
        samples = []
        for _ in range(repeats):
            started = perf_counter()
            model.model_validate(payload)
            samples.append((perf_counter() - started) * 1000)
        median_ms = statistics.median(samples)
        print(
            f"  depth {depth:>3}: {median_ms:9.3f} ms "
            f"(median of {repeats})",
            flush=True,
        )


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
    parser.add_argument(
        "--repeats",
        type=int,
        default=5,
        help="validation samples per depth (default: 5)",
    )
    args = parser.parse_args()
    if args.max_legacy_depth < 1:
        parser.error("--max-legacy-depth must be at least 1")
    if args.repeats < 1:
        parser.error("--repeats must be at least 1")

    legacy = build_envelope(discriminated=False)
    tagged = build_envelope(discriminated=True)
    print(f"Python {platform.python_version()} / Pydantic {pydantic.__version__}")
    measure(
        legacy,
        list(range(1, args.max_legacy_depth + 1)),
        "Untagged union",
        args.repeats,
    )
    measure(tagged, args.fixed_depths, "Tagged union", args.repeats)


if __name__ == "__main__":
    main()
