"""Public API for the xarray_signature_units package.

Run-time validation of pint/CF units declared in signature annotations on xarray DataArrays.
"""

from ._annotations import units_from_signature
from ._check import (
    UnitsWarning,
    assert_valid_unit,
    check_units,
)
from ._config import (
    Policy,
    get_policy,
    policy,
    set_policy,
)
from ._decorator import declare_units
from ._registry import (
    set_registry,
    use_cf_units,
)

__all__ = [
    "Policy",
    "UnitsWarning",
    "assert_valid_unit",
    "check_units",
    "declare_units",
    "get_policy",
    "policy",
    "set_policy",
    "set_registry",
    "units_from_signature",
    "use_cf_units",
]
