# encoding: utf-8
import ckan.plugins.toolkit as toolkit
from typing import (
    Any, Optional
)


def og_datatablesview_null_label() -> str:
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
