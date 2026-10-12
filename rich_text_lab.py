"""Small, standalone model inspired by aiogram issue #1925.

This deliberately models the same troublesome shape: a recursive union with
26 model alternatives, each of which has a recursively typed text field.
It is not a copy of aiogram's generated models or the original update payload.
"""

from __future__ import annotations

from typing import Annotated, ForwardRef, Literal, Union

from pydantic import BaseModel, Discriminator, Tag, create_model
from typing_extensions import TypeAliasType


RICH_TEXT_TYPES = (
    "bold",
    "italic",
    "underline",
    "strikethrough",
    "spoiler",
    "date_time",
    "text_mention",
    "subscript",
    "superscript",
    "marked",
    "code",
    "custom_emoji",
    "mathematical_expression",
    "url",
    "email_address",
    "phone_number",
    "bank_card_number",
    "mention",
    "hashtag",
    "cashtag",
    "bot_command",
    "anchor",
    "anchor_link",
    "reference",
    "reference_link",
    "button",
)


def _tag(value: object) -> str | None:
    if isinstance(value, str):
        return "str"
    if isinstance(value, (list, tuple)):
        return "list"
    if isinstance(value, dict):
        tag = value.get("type")
        return tag if isinstance(tag, str) else None
    tag = getattr(value, "type", None)
    return tag if isinstance(tag, str) else None


def build_envelope(*, discriminated: bool) -> type[BaseModel]:
    """Build either the legacy smart union or the tagged comparison model."""
    variant = "Tagged" if discriminated else "Legacy"
    alias_name = f"{variant}RichTextUnion"
    recursive_list = list[ForwardRef(alias_name)]

    models = [
        create_model(
            f"{variant}RichText{''.join(part.title() for part in kind.split('_'))}",
            type=(Literal[kind], kind),
            text=(ForwardRef(alias_name), ...),
        )
        for kind in RICH_TEXT_TYPES
    ]

    if discriminated:
        branches = [
            Annotated[str, Tag("str")],
            Annotated[recursive_list, Tag("list")],
            *(Annotated[model, Tag(kind)] for kind, model in zip(RICH_TEXT_TYPES, models)),
        ]
        union = Annotated[Union[tuple(branches)], Discriminator(_tag)]
    else:
        union = Union[(str, recursive_list, *models)]

    rich_text = TypeAliasType(alias_name, union)
    namespace = {alias_name: rich_text}
    for model in models:
        model.model_rebuild(force=True, _types_namespace=namespace)

    envelope = create_model(f"{variant}Envelope", value=(rich_text, ...))
    envelope.model_rebuild(force=True, _types_namespace=namespace)
    return envelope


def nested_value(depth: int) -> object:
    """Create a nested chain matching Telegram's rich-text wrapper shape."""
    if depth < 1:
        raise ValueError("depth must be at least 1")
    value: object = "sample"
    kinds = ("spoiler", "subscript", "bold", "italic", "underline")
    for index in reversed(range(depth)):
        kind = kinds[index % len(kinds)]
        value = {"type": kind, "text": value}
    return value
