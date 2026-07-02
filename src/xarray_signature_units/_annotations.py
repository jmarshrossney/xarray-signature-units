"""Reading declared units off ``typing.Annotated`` type hints.

Pure ``typing`` introspection with no dependency on the active registry or
configuration: this is the "declaration side" of the package, turning
``Annotated[DataArray, "degC"]`` metadata into plain unit strings that the
checking layer later validates.
"""

import types
from typing import (
    Annotated,
    Any,
    Union,
    get_args,
    get_origin,
    get_type_hints,
    is_typeddict,
)

import xarray as xr


def unwrap_annotated(hint: Any) -> Any:
    """Return the underlying type of an ``Annotated`` hint, else the hint itself.

    ``Annotated[DataArray, "degC"]`` → ``DataArray``; a non-``Annotated`` hint is
    returned unchanged. Lets type comparisons (e.g. ``t is DataArray``) see through
    the unit metadata that signature-native declarations attach to parameters.
    """
    return get_args(hint)[0] if get_origin(hint) is Annotated else hint


def _is_dataarray_type(tp: Any) -> bool:
    """Return whether ``tp`` is ``DataArray`` (possibly wrapped in a Union).

    Accepts a bare ``DataArray`` as well as ``DataArray | None`` /
    ``Optional[DataArray]`` (and any other union that includes ``DataArray``), so
    an optional DataArray parameter can still carry a declared unit. Anything
    else (scalars, ``str``, ``bool``, ``Dataset``, …) is not a unit-bearing type.
    """
    if tp is xr.DataArray:
        return True
    if get_origin(tp) in (Union, types.UnionType):
        return any(_is_dataarray_type(arg) for arg in get_args(tp))
    return False


def annotated_unit(hint: Any) -> str | None:
    """Return the declared unit carried by an ``Annotated`` type hint, or ``None``.

    The unit is the **first ``str``** in the ``Annotated`` metadata, e.g.
    ``Annotated[DataArray, "degC"]`` → ``"degC"``. This makes the metadata
    extensible: a unit may be followed by free-form annotations (a description,
    typed markers, …) that are ignored here, so

        ``Annotated[DataArray, "m s-1", "z component of velocity"]`` → ``"m s-1"``

    The convention is therefore *unit first*: the unit must precede any
    descriptive string. A description placed before the unit would be mis-read as
    the unit — but `assert_valid_unit` rejects it unless the description itself
    parses as a valid unit, so the failure is loud.
    Non-string metadata (ints, markers) is skipped regardless of position.

    The metadata is only interpreted as a unit when the annotated base type is a
    ``DataArray`` (the only type that carries units); a descriptive string on a
    non-``DataArray`` parameter (e.g. ``Annotated[bool, "toggles X"]``) is *not* a
    unit and yields ``None``. Non-``Annotated`` hints, or ``Annotated`` hints
    whose metadata holds no string, also return ``None``.
    """
    if get_origin(hint) is not Annotated:
        return None
    # get_args(Annotated[T, m1, m2, ...]) == (T, m1, m2, ...); skip the base type.
    args = get_args(hint)
    if not _is_dataarray_type(args[0]):
        return None
    for meta in args[1:]:
        if isinstance(meta, str):
            return meta
    return None


def units_from_signature(
    func: object,
) -> tuple[dict[str, str], dict[str, str] | str | None]:
    """Extract declared units from a function's type annotations.

    Reads ``get_type_hints(func, include_extras=True)`` and interprets
    ``Annotated[..., "<unit>"]`` metadata as unit declarations:

    - **inputs**: every parameter whose hint is ``Annotated`` with a string unit
      contributes to the returned ``input_units`` mapping (others are ignored);
    - **output**: if the return hint is a ``TypedDict``, each field name maps to
      its ``Annotated`` unit (a ``dict``); if it is a bare ``Annotated[DataArray,
      unit]`` return, the bare unit ``str``; otherwise ``None``.
    """
    hints = get_type_hints(func, include_extras=True)
    ret = hints.pop("return", None)

    input_units = {
        name: unit
        for name, hint in hints.items()
        if (unit := annotated_unit(hint)) is not None
    }

    output_units: dict[str, str] | str | None
    if is_typeddict(ret):
        ret_hints = get_type_hints(ret, include_extras=True)
        output_units = {
            name: unit
            for name, hint in ret_hints.items()
            if (unit := annotated_unit(hint)) is not None
        }
    else:
        output_units = annotated_unit(ret)

    return input_units, output_units
