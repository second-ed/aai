
import os
import re
from itertools import chain
from typing import Optional

import attr
import nbformat
from attr.validators import deep_iterable, instance_of, optional
from pathlib import Path

import black


def get_dir_path(src: str, idx: int, dst: str) -> str:
    curr_dir = Path(src).parents[idx]
    return str(curr_dir.joinpath(dst)).replace("\\", "/")


def _clean_column(col: str) -> str:
    if not all([isinstance(col, str)]):
        raise TypeError(
            "_clean_column expects arg types: [str], "
            f"received: [{type(col).__name__}]"
        )
    return re.sub(
        r"_+",
        "_",
        re.sub(r"[^a-zA-Z0-9_]", "", col.lower().strip().replace(" ", "_")),
    )


def _clean_columns(cols: list[str]) -> list[str]:
    if not all([isinstance(cols, list)]):
        raise TypeError(
            "_clean_columns expects arg types: [List], "
            f"received: [{type(cols).__name__}]"
        )
    return list(map(_clean_column, cols))


def format_code_string(code_snippet: str) -> str:
    return black.format_str(code_snippet, mode=black.FileMode())


def convert_unit(unit: str) -> list[int]:
    unit = str(unit)
    unit_code = list(map(int, unit.split(".")))
    if len(unit_code) == 2:
        unit_code.append(0)
    return unit_code


def get_ref_number(refs: dict, point) -> int:
    if not refs:
        refs[point.source] = 1
        return refs[point.source]
    if point.source in refs:
        return refs[point.source]
    refs[point.source] = max(refs.values()) + 1
    return refs[point.source]