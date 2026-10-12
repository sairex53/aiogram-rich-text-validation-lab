# Recursive rich-text validation lab

[![tests](https://github.com/sairex53/aiogram-rich-text-validation-lab/actions/workflows/tests.yml/badge.svg)](https://github.com/sairex53/aiogram-rich-text-validation-lab/actions/workflows/tests.yml)

This is a small, reproducible experiment inspired by [aiogram issue #1925](https://github.com/aiogram/aiogram/issues/1925) and its merged fix, [PR #1934](https://github.com/aiogram/aiogram/pull/1934).

The report described a Telegram update that made aiogram 3.31.0 spend seconds validating a nested `rich_message`. The maintainer's fix changed the recursive rich-text union to tagged dispatch. This project isolates the relevant shape: 26 model alternatives, each with a recursively typed `text` field, compared as an untagged Pydantic union and as a callable-discriminated union.

It is an educational microbenchmark, not the original aiogram payload, not an exploit, and not a substitute for the upstream regression test. The timings depend on Python, Pydantic, and hardware. The benchmark intentionally caps the slow model's default depth at 4 because validation cost grows rapidly; raise it only if you are prepared to wait.

## Run

Python 3.10+ and Pydantic 2.5+ are required.

```sh
python -m pip install -r requirements.txt
python -m unittest -v
python benchmark.py
```

The test exercises a depth-100 chain and checks that the tagged union selects concrete models. The benchmark warms up each model and reports the median of five validation samples per depth; use `--repeats` to change the sample count. It makes no fixed performance claim across machines.

One local run on Python 3.14.8 and Pydantic 2.12.5 measured a depth-4 nested value at 195.061 ms for the untagged union and 0.004 ms for tagged dispatch. The tagged depth-100 case measured 0.073 ms. These are measurements of this synthetic model, not aiogram's original payload.

## What the comparison shows

With a recursive untagged union, a failed model alternative can validate the same nested `text` subtree before Pydantic tries the next alternative. A discriminator reads the `type` tag once and dispatches directly to the matching model. The production fix is in aiogram; this repository only demonstrates the type-shape and verifies the behavior locally.
