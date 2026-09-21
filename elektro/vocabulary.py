"""The vocabularies a caller writes against: axis types and transformation kinds.

Kept free of the generated schema on purpose, so `import elektro` does not pull
`elektro.api.schema` in through it.
"""

import re
from collections.abc import Mapping
from typing import Final, Literal, Union

#: The axis types of the elektro schema, as the wire spells them.
AxisTypeName = Literal[
    "SPACE",
    "TIME",
    "CHANNEL",
    "COORDINATE",
    "DISPLACEMENT",
    "FREQUENCY",
    "VALUE",
    "INDEX",
]

#: Every transformation kind an edge can come back as.
ResolvedTransformKind = Literal[
    "IDENTITY",
    "SCALE",
    "TRANSLATION",
    "MAP_AXIS",
    "AFFINE",
    "ROTATION",
    "SEQUENCE",
    "BY_DIMENSION",
    "FIELD",
    "UNMAPPABLE",
]

#: The kinds that state their numbers on the edge itself.
MATRIX_KINDS: Final[frozenset[ResolvedTransformKind]] = frozenset(
    {"IDENTITY", "SCALE", "TRANSLATION", "AFFINE", "ROTATION", "MAP_AXIS"}
)

# The sample axis of a signal is TIME even when sampling is irregular; INDEX is
# for what has no metric at all (a sweep, a trial, a spike number).
_AXIS_TYPE_BY_NAME: Final[Mapping[str, AxisTypeName]] = {
    "t": "TIME",
    "time": "TIME",
    "c": "CHANNEL",
    "channel": "CHANNEL",
    "f": "FREQUENCY",
    "frequency": "FREQUENCY",
    "v": "VALUE",
    "value": "VALUE",
    "sweep": "INDEX",
    "trial": "INDEX",
    "spike": "INDEX",
    "x": "SPACE",
    "y": "SPACE",
    "z": "SPACE",
}


class UnknownAxisName(ValueError):
    """Raised when the bare-name convention has no entry for an axis name."""


def default_axis_type(name: str) -> AxisTypeName:
    """The conventional axis type for a bare axis name.

    ``t`` -> TIME, ``c`` -> CHANNEL, ``f`` -> FREQUENCY, ``v`` -> VALUE,
    ``sweep``/``trial``/``spike`` -> INDEX, ``x``/``y``/``z`` -> SPACE. Anything
    else raises: nothing in an array says whether a second dimension is channels
    or sweeps, and the type decides how it is sampled, windowed and composed.

    Raises:
        UnknownAxisName: if the convention has no entry for ``name``.
    """
    try:
        return _AXIS_TYPE_BY_NAME[name.lower()]
    except KeyError:
        raise UnknownAxisName(
            f"No conventional axis type for {name!r}. The bare-name convention "
            f"covers {sorted(_AXIS_TYPE_BY_NAME)} and nothing else. State the type "
            f"explicitly with AxisInput(name={name!r}, type=...)."
        ) from None


#: What `Trace.lens` takes per axis: one index, a ``slice()``, or a
#: ``(start, stop[, step])`` tuple.
AxisSelection = Union[
    int,
    slice,
    tuple[int | None, int | None],
    tuple[int | None, int | None, int | None],
]

#: The normalized form: ``(start, stop, step)``, any of which may be ``None``.
SliceBounds = tuple[int | None, int | None, int | None]


def normalize_selection(axis: str, selection: AxisSelection) -> SliceBounds:
    """One selection as ``(start, stop, step)``, or a refusal naming the axis.

    The ``bool`` rejection is not redundant with the annotation: ``bool`` is a
    subclass of ``int``, so no type can exclude ``trace.lens(c=True)``, and
    silently reading it as index 1 is worse than refusing it.
    """
    if isinstance(selection, bool):
        raise TypeError(f"Invalid selection for axis {axis!r}: {selection!r}")
    if isinstance(selection, int):
        return (selection, selection + 1, None)
    if isinstance(selection, slice):
        return (selection.start, selection.stop, selection.step)
    if isinstance(selection, (tuple, list)) and 2 <= len(selection) <= 3:
        start, stop = selection[0], selection[1]
        step = selection[2] if len(selection) == 3 else None
        return (start, stop, step)
    raise TypeError(
        f"Invalid selection for axis {axis!r}: {selection!r}. Pass an int, a "
        f"slice(), or a (start, stop[, step]) tuple"
    )


#: What DuckDB calls each Arrow type, for the types that survive a Parquet round
#: trip with the same answer on every DuckDB the stack runs.
#:
#: A table column's declared ``dtype`` is a **DuckDB** type name and the frame it
#: is declared for is a **pandas/Arrow** object, so this mapping is the whole of
#: the gap — and it is not the obvious one: a float64 is a ``DOUBLE``, a float32
#: is a ``FLOAT``, a str column is a ``VARCHAR``. Every entry was measured, by
#: writing a one-column Parquet of that type and running ``DESCRIBE`` over it on
#: **both** the DuckDB the client has and the older one the server runs.
#:
#: The keys are ``str(arrow_type)`` — what ``pyarrow`` prints, and what a caller
#: reading a traceback sees. Deliberately partial; see :func:`duckdb_type`.
_DUCKDB_BY_ARROW: Final[Mapping[str, str]] = {
    "int8": "TINYINT",
    "int16": "SMALLINT",
    "int32": "INTEGER",
    "int64": "BIGINT",
    "uint8": "UTINYINT",
    "uint16": "USMALLINT",
    "uint32": "UINTEGER",
    "uint64": "UBIGINT",
    "float": "FLOAT",
    "double": "DOUBLE",
    "bool": "BOOLEAN",
    "string": "VARCHAR",
    "large_string": "VARCHAR",
    "string_view": "VARCHAR",
    "binary": "BLOB",
    "large_binary": "BLOB",
    "binary_view": "BLOB",
    # date64 beside date32 is not a duplicate: Parquet has one date encoding, so
    # a date64 column comes back off the file *as* a date32. Both are DATE
    # either way, which is why they can share a row without the caller caring.
    "date32[day]": "DATE",
    "date64[ms]": "DATE",
    "time32[s]": "TIME",
    "time32[ms]": "TIME",
    "time64[us]": "TIME",
    "time64[ns]": "TIME",
    "timestamp[s]": "TIMESTAMP",
    "timestamp[ms]": "TIMESTAMP",
    "timestamp[us]": "TIMESTAMP",
    "timestamp[ns]": "TIMESTAMP_NS",
}

#: The Arrow types this vocabulary refuses by name, and what to do instead. Each
#: is a case where guessing yields a plausible, wrong, silent answer.
_REFUSED_ARROW_TYPES: Final[Mapping[str, str]] = {
    "halffloat": (
        "a float16 column reads back as FLOAT on DuckDB 1.5 and as BLOB on "
        "DuckDB 1.2, so no single answer is right on both. Cast it: "
        "frame.astype({name: 'float32'})"
    ),
    "null": (
        "an all-null column gives Parquet no type to record and DuckDB reads it "
        "back as INTEGER, so declaring it would claim a type the data does not "
        "have. Give the column a dtype, or drop it"
    ),
}

#: The same, matched by prefix because the types are parameterised.
_REFUSED_ARROW_PREFIXES: Final[Mapping[str, str]] = {
    "duration": (
        "a duration column is stored as a bare integer count of its unit, so "
        "DuckDB reads it back as BIGINT and the unit is gone. Convert it to the "
        "number meant -- frame[name].dt.total_seconds() -- and declare the unit "
        "on the column instead"
    ),
    "decimal256": (
        "a decimal256 reads back as DECIMAL while its precision fits DuckDB's 38 "
        "digits and as DOUBLE beyond that, so its type turns on a number this "
        "cannot see. Use decimal128, or float64"
    ),
    "list": "a nested column is not a table column. Explode or flatten it first",
    "large_list": "a nested column is not a table column. Explode or flatten it first",
    "fixed_size_list": "a nested column is not a table column. Explode or flatten it first",
    "struct": "a nested column is not a table column. Flatten it into one column per field",
    "map": "a nested column is not a table column. Flatten it into one column per key",
}

_DECIMAL128 = re.compile(r"^decimal128\((\d+), (\d+)\)$")
_DICTIONARY_VALUES = re.compile(r"^dictionary<values=(.+), indices=[^,]+, ordered=\d+>$")


class UnknownArrowType(ValueError):
    """Raised when the Arrow -> DuckDB vocabulary has no entry for a type."""


def duckdb_type(arrow_type: object) -> str:
    """What DuckDB will call this Arrow type once it is a Parquet file.

    Takes a ``pyarrow.DataType`` — or anything whose ``str()`` is one, which is
    what a schema field prints as — and returns the DuckDB type name a column of
    that type is declared with::

        duckdb_type(pa.float64())   # 'DOUBLE'

    Deliberately partial, in the same way and for the same reason as
    :func:`default_axis_type`: the listed types are the ones measured to give
    the same answer on every DuckDB in the stack, and there is no catch-all.
    Anything else raises, saying what to do about it — because the alternative
    is a column confidently declared as the wrong thing (a float16 named FLOAT,
    an empty column named INTEGER), which nothing downstream would object to.

    Raises:
        UnknownArrowType: if the type is not in the measured vocabulary.
    """
    name = str(arrow_type)

    known = _DUCKDB_BY_ARROW.get(name)
    if known is not None:
        return known

    # A tz-aware timestamp is TIMESTAMP WITH TIME ZONE whatever its unit --
    # measured for s/us/ns and for a named zone as well as UTC, which is why
    # this is a rule where the naive ones above are a table.
    if name.startswith("timestamp[") and ", tz=" in name:
        return "TIMESTAMP WITH TIME ZONE"

    decimal = _DECIMAL128.match(name)
    if decimal is not None:
        return f"DECIMAL({decimal.group(1)},{decimal.group(2)})"

    # A dictionary column becomes its values type on write: Parquet stores the
    # dictionary as an encoding rather than a type, so only a string dictionary
    # survives as one and the rest come back decoded. Recursing is right for
    # both -- measured for values=string (VARCHAR) and values=int64 (BIGINT).
    dictionary = _DICTIONARY_VALUES.match(name)
    if dictionary is not None:
        return duckdb_type(dictionary.group(1))

    advice = _REFUSED_ARROW_TYPES.get(name)
    if advice is None:
        for prefix, reason in _REFUSED_ARROW_PREFIXES.items():
            if name.startswith(prefix):
                advice = reason
                break

    raise UnknownArrowType(
        f"No DuckDB type is recorded for the Arrow type {name!r}: "
        + (advice or "it is not in the measured vocabulary")
        + ". elektro.vocabulary._DUCKDB_BY_ARROW lists what is."
    )



#: The colormaps that assign a colour per distinct value rather than a ramp over a range.
#: Values rather than ``ColorMap`` members, so this module need not import the schema.
QUALITATIVE_COLORMAP_VALUES: Final[frozenset[str]] = frozenset({"HUES", "DISTINCT", "PASTEL", "VIVID"})
