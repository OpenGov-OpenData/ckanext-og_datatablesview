# encoding: utf-8
import json

import ckan.plugins.toolkit as toolkit
from typing import (
    Any, Optional
)


# Datastore/postgres numeric type names the prefix option applies to. The data
# dictionary reports postgres type names (e.g. numeric, int4, float8), so we
# match against those as well as the friendlier aliases.
NUMERIC_COLUMN_TYPES = frozenset({
    'numeric', 'number', 'decimal', 'money',
    'int', 'integer', 'smallint', 'bigint',
    'int2', 'int4', 'int8',
    'float', 'float4', 'float8', 'real', 'double precision',
})


def og_datatablesview_is_numeric_column(field_type: Any) -> bool:
    """
    Return True if the given data dictionary column type is a numeric type.

    Used by the config form to only offer the display-prefix option on numeric
    columns.
    """
    return str(field_type or '').lower() in NUMERIC_COLUMN_TYPES


def og_datatablesview_has_numeric_column(fields: Any) -> bool:
    """
    Return True if any field in the given data dictionary list is numeric.

    Used by the config form to hide the Prefix/Suffix columns entirely when a
    resource has no numeric columns (so they are not shown as empty columns).
    """
    if not fields:
        return False
    return any(
        og_datatablesview_is_numeric_column(f.get('type'))
        for f in fields
    )


def _og_datatablesview_column_affixes(value: Any) -> dict[str, str]:
    """
    Normalise a per-column affix map (prefixes or suffixes) into a
    ``{column_id: affix}`` dict.

    The value can arrive as a dict (the validated config, e.g. on the initial
    edit form or in the view) or as a JSON string (the raw value POSTed by the
    config form when it is re-rendered after a validation error). Blank affixes
    are dropped so we only keep columns that actually have one.
    """
    if not value:
        return {}

    if isinstance(value, str):
        try:
            value = json.loads(value)
        except ValueError:
            return {}

    if not isinstance(value, dict):
        return {}

    return {
        str(k): str(v)
        for k, v in value.items()
        if v is not None and str(v) != ''
    }


def og_datatablesview_column_prefixes(value: Any) -> dict[str, str]:
    """
    Normalise the per-column display prefixes into a ``{column_id: prefix}``
    dict. See :func:`_og_datatablesview_column_affixes`.
    """
    return _og_datatablesview_column_affixes(value)


def og_datatablesview_column_suffixes(value: Any) -> dict[str, str]:
    """
    Normalise the per-column display suffixes into a ``{column_id: suffix}``
    dict. See :func:`_og_datatablesview_column_affixes`.
    """
    return _og_datatablesview_column_affixes(value)


def og_datatables_datefilterview_null_label() -> str:
    """
    Get the label used to display NoneType values for the front-end

    :returns: The label.
    :rtype: str
    """
    label = toolkit.config.get("ckan.datatables.null_label")
    return toolkit._(label) if label else ""


def og_datastore_dictionary(
        resource_id: str, include_columns: Optional[list[str]] = None
) -> list[dict[str, Any]]:
    """
    Return the data dictionary info for a resource, optionally filtering
    columns returned.

    include_columns is a list of column ids to include in the output
    """
    try:
        return [
            f for f in toolkit.get_action('datastore_search')({}, {
                'id': resource_id,
                'limit': 0
            })['fields']
            if not f['id'].startswith(u'_') and (
                include_columns is None or f['id'] in include_columns)
            ]
    except (toolkit.ObjectNotFound, toolkit.NotAuthorized):
        return []
