# encoding: utf-8

from urllib.parse import urlencode
from html import escape
from datetime import datetime
import csv
import io

from flask import Blueprint, Response


from ckan.common import json
from ckan.plugins.toolkit import get_action, request, h
import re

ogdatatablesdatefilterview = Blueprint(u'ogdatatablesdatefilterview', __name__)


def merge_filters(view_filters, user_filters_str):
    u'''
    view filters are built as part of the view, user filters
    are selected by the user interacting with the view. Any filters
    selected by user may only tighten filters set in the view,
    others are ignored.

    >>> merge_filters({
    ...    u'Department': [u'BTDT'], u'OnTime_Status': [u'ONTIME']},
    ...    u'CASE_STATUS:Open|CASE_STATUS:Closed|Department:INFO')
    {u'Department': [u'BTDT'],
     u'OnTime_Status': [u'ONTIME'],
     u'CASE_STATUS': [u'Open', u'Closed']}
    '''
    filters = dict(view_filters)
    if not user_filters_str:
        return filters
    user_filters = {}
    for k_v in user_filters_str.split(u'|'):
        k, sep, v = k_v.partition(u':')
        if k not in view_filters or v in view_filters[k]:
            user_filters.setdefault(k, []).append(v)
    for k in user_filters:
        filters[k] = user_filters[k]
    return filters


def is_date_range_filter(value):
    u'''
    Check if a filter value contains a date range pattern.
    Supports formats like:
    - "2024-01-01 to 2024-12-31"
    - "2024-01-01,2024-12-31"
    - "2024-01-01 - 2024-12-31"
    
    Returns tuple (is_date_range, start_date, end_date) or (False, None, None)
    '''
    if not value:
        return (False, None, None)
    
    value = value.strip()
    
    # Try "to" separator
    if u' to ' in value.lower():
        parts = re.split(r'\s+to\s+', value, flags=re.IGNORECASE)
        if len(parts) == 2:
            start_date = parts[0].strip()
            end_date = parts[1].strip()
            if _is_valid_date(start_date) and _is_valid_date(end_date):
                return (True, start_date, end_date)
    
    # Try comma separator
    if u',' in value:
        parts = value.split(u',')
        if len(parts) == 2:
            start_date = parts[0].strip()
            end_date = parts[1].strip()
            if _is_valid_date(start_date) and _is_valid_date(end_date):
                return (True, start_date, end_date)
    
    # Try dash separator (with spaces)
    if u' - ' in value:
        parts = value.split(u' - ')
        if len(parts) == 2:
            start_date = parts[0].strip()
            end_date = parts[1].strip()
            if _is_valid_date(start_date) and _is_valid_date(end_date):
                return (True, start_date, end_date)
    
    return (False, None, None)


def _is_valid_date(date_str):
    u'''
    Check if a string is a valid date in YYYY-MM-DD format.
    '''
    try:
        datetime.strptime(date_str, u'%Y-%m-%d')
        return True
    except ValueError:
        return False


def is_date_column(column_name, fields):
    u'''
    Check if a column is a date/timestamp type.
    '''
    for field in fields:
        if field.get(u'id') == column_name:
            field_type = field.get(u'type', u'').lower()
            return field_type in (u'timestamp', u'timestamptz', u'date')
    return False


def datastore_search_sql_date_range(resource_id, column_name, start_date, end_date,
                                    filters, sort_list, offset, limit, cols):
    u'''
    Perform a datastore_search_sql query for date range filtering.
    Returns the response dictionary similar to datastore_search.
    '''
    datastore_search_sql = get_action(u'datastore_search_sql')
    
    # Build WHERE clause for date range
    # Escape column name to prevent SQL injection
    # Column names in datastore are typically quoted
    safe_column = u'"{}"'.format(column_name.replace(u'"', u'""'))
    
    # Escape date values to prevent SQL injection
    safe_start_date = start_date.replace(u"'", u"''")
    safe_end_date = end_date.replace(u"'", u"''")
    
    # Include full day for end date by adding time component
    where_clauses = [u'{} >= \'{}\'::timestamp'.format(safe_column, safe_start_date),
                     u'{} < (\'{}\'::date + interval \'1 day\')::timestamp'.format(safe_column, safe_end_date)]
    
    # Add filters as additional WHERE conditions
    filter_conditions = []
    for filter_key, filter_values in filters.items():
        if isinstance(filter_values, list):
            if len(filter_values) == 1:
                safe_filter_key = u'"{}"'.format(filter_key.replace(u'"', u'""'))
                safe_filter_value = str(filter_values[0]).replace(u"'", u"''")
                filter_conditions.append(
                    u'{} = \'{}\''.format(safe_filter_key, safe_filter_value)
                )
            else:
                safe_filter_key = u'"{}"'.format(filter_key.replace(u'"', u'""'))
                values = u", ".join([u"'" + str(v).replace(u"'", u"''") + u"'" for v in filter_values])
                filter_conditions.append(u'{} IN ({})'.format(safe_filter_key, values))
        else:
            safe_filter_key = u'"{}"'.format(filter_key.replace(u'"', u'""'))
            safe_filter_value = str(filter_values).replace(u"'", u"''")
            filter_conditions.append(
                u'{} = \'{}\''.format(safe_filter_key, safe_filter_value)
            )
    
    if filter_conditions:
        where_clauses.extend(filter_conditions)
    
    where_clause = u' AND '.join(where_clauses)
    
    # Build ORDER BY clause - quote column names to handle spaces
    if sort_list:
        quoted_sort_list = []
        for sort_item in sort_list:
            # sort_item format: "column_name asc" or "column_name desc"
            # Split from the right (rsplit) to get direction and column name
            # This handles column names with spaces correctly
            parts = sort_item.rsplit(None, 1)  # Split on whitespace from right, max 1 split
            if len(parts) == 2:
                col_name, direction = parts
                # Quote column name to handle spaces and special characters
                safe_col_name = u'"{}"'.format(col_name.replace(u'"', u'""'))
                quoted_sort_list.append(u'{} {}'.format(safe_col_name, direction))
            else:
                # Fallback if format is unexpected - quote the whole thing
                safe_col_name = u'"{}"'.format(sort_item.replace(u'"', u'""'))
                quoted_sort_list.append(safe_col_name)
        order_by = u', '.join(quoted_sort_list)
    else:
        order_by = u'"_id" asc'
    
    # Build SELECT clause - escape column names
    select_fields = u', '.join([u'"{}"'.format(col.replace(u'"', u'""')) for col in cols])
    
    # CKAN datastore uses resource_id as table identifier
    # Escape resource_id for SQL
    safe_resource_id = resource_id.replace(u'"', u'""')
    
    # Build SQL query - CKAN datastore_search_sql uses resource_id directly
    sql = u'SELECT {select_fields} FROM "{safe_resource_id}" WHERE {where_clause} ORDER BY {order_by} LIMIT {limit} OFFSET {offset}'.format(
        select_fields=select_fields,
        safe_resource_id=safe_resource_id,
        where_clause=where_clause,
        order_by=order_by,
        limit=limit,
        offset=offset
    )
    
    # Also get total count for filtered results
    count_sql = u'SELECT COUNT(*) as total FROM "{safe_resource_id}" WHERE {where_clause}'.format(
        safe_resource_id=safe_resource_id,
        where_clause=where_clause
    )
    
    try:
        # Execute main query
        response = datastore_search_sql(
            None, {
                u'sql': sql
            }
        )
        
        # Execute count query
        count_response = datastore_search_sql(
            None, {
                u'sql': count_sql
            }
        )
        
        # datastore_search_sql returns records as list of dicts with column names as keys
        records = response.get(u'records', [])
        
        # Get total from count query
        count_records = count_response.get(u'records', [])
        total = count_records[0].get(u'total', 0) if count_records else 0
        
        return {
            u'records': records,
            u'total': total,
            u'fields': [{'id': col} for col in cols]
        }
    except Exception as e:
        raise Exception(u'SQL query error: {}'.format(str(e)))


def ajax(resource_view_id):
    resource_view = get_action(u'resource_view_show'
                               )(None, {
                                   u'id': resource_view_id
                               })

    draw = int(request.form[u'draw'])
    search_text = str(request.form[u'search[value]'])
    offset = int(request.form[u'start'])
    limit = int(request.form[u'length'])
    view_filters = resource_view.get(u'filters', {})
    user_filters = str(request.form[u'filters'])
    filters = merge_filters(view_filters, user_filters)

    datastore_search = get_action(u'datastore_search')
    unfiltered_response = datastore_search(
        None, {
            u"resource_id": resource_view[u'resource_id'],
            u"limit": 0,
            u"filters": view_filters,
        }
    )

    cols = [f[u'id'] for f in unfiltered_response[u'fields']]
    if u'show_fields' in resource_view:
        if '_id' not in resource_view[u'show_fields']:
            resource_view[u'show_fields'].insert(0, '_id')
        cols = [c for c in cols if c in resource_view[u'show_fields']]

    sort_list = []
    i = 0
    while True:
        if u'order[%d][column]' % i not in request.form:
            break
        sort_by_num = int(request.form[u'order[%d][column]' % i])
        sort_order = (
            u'desc' if request.form[u'order[%d][dir]' %
                                    i] == u'desc' else u'asc'
        )
        sort_list.append(cols[sort_by_num] + u' ' + sort_order)
        i += 1

    # Add default sorting
    if u'_id asc' not in sort_list and u'_id desc' not in sort_list:
        sort_list.append(u'_id asc')

    colsearch_dict = {}
    date_range_filter = None
    date_range_column = None
    
    # Check merged filters for date range values (from URL parameters)
    for filter_key, filter_values in filters.items():
        if filter_values:
            # Handle both single value and list of values
            values_to_check = filter_values if isinstance(filter_values, list) else [filter_values]
            for filter_value in values_to_check:
                if filter_value:
                    # Check if this is a date range filter
                    is_date_range, start_date, end_date = is_date_range_filter(str(filter_value))
                    if is_date_range and is_date_column(filter_key, unfiltered_response[u'fields']):
                        # Store date range filter info
                        date_range_filter = (start_date, end_date)
                        date_range_column = filter_key
                        # Remove date range from regular filters (it will be handled by SQL query)
                        if isinstance(filters[filter_key], list):
                            filters[filter_key] = [v for v in filters[filter_key] if v != filter_value]
                            if not filters[filter_key]:
                                del filters[filter_key]
                        else:
                            del filters[filter_key]
                        break
            if date_range_filter:
                break
    
    i = 0
    while True:
        if u'columns[%d][search][value]' % i not in request.form:
            break
        v = str(request.form[u'columns[%d][search][value]' % i])
        if v:
            k = str(request.form[u'columns[%d][name]' % i])
            # Check if this is a date range filter (only if not already found in filters)
            if not date_range_filter:
                is_date_range, start_date, end_date = is_date_range_filter(v)
                if is_date_range and is_date_column(k, unfiltered_response[u'fields']):
                    # Store date range filter info
                    date_range_filter = (start_date, end_date)
                    date_range_column = k
                else:
                    # replace non-alphanumeric characters with FTS wildcard (_)
                    v = re.sub(r'[^0-9a-zA-Z\-]+', '_', v)
                    # append ':*' so we can do partial FTS searches
                    colsearch_dict[k] = v + u':*'
            else:
                # If date range already found, skip column search processing for date columns
                if not (is_date_column(k, unfiltered_response[u'fields']) and is_date_range_filter(v)[0]):
                    # replace non-alphanumeric characters with FTS wildcard (_)
                    v = re.sub(r'[^0-9a-zA-Z\-]+', '_', v)
                    # append ':*' so we can do partial FTS searches
                    colsearch_dict[k] = v + u':*'
        i += 1

    # If date range filter is found, use SQL query instead
    if date_range_filter:
        try:
            start_date, end_date = date_range_filter
            response = datastore_search_sql_date_range(
                resource_view[u'resource_id'],
                date_range_column,
                start_date,
                end_date,
                filters,
                sort_list,
                offset,
                limit,
                cols
            )
        except Exception as e:
            query_error = u'Invalid date range query... ' + str(e)
            dtdata = {u'error': query_error}
        else:
            data = []
            null_label = h.og_datatablesview_null_label()
            for row in response[u'records']:
                record = {colname.replace('.', ''): escape(str(null_label if row.get(colname, u'')
                                                               is None else row.get(colname, u'')))
                          for colname in cols}
                # the DT_RowId is used in DT to set an element id for each record
                record['DT_RowId'] = 'row' + str(row.get(u'_id', u''))
                data.append(record)

            dtdata = {
                u'draw': draw,
                u'recordsTotal': unfiltered_response.get(u'total', 0),
                u'recordsFiltered': response.get(u'total', 0),
                u'data': data
            }
    else:
        # Original logic for non-date-range filters
        if colsearch_dict:
            search_text = json.dumps(colsearch_dict)
        else:
            search_text = re.sub(r'[^0-9a-zA-Z\-]+', '_',
                                 search_text) + u':*' if search_text else u''

        try:
            response = datastore_search(
                None, {
                    u"q": search_text,
                    u"resource_id": resource_view[u'resource_id'],
                    u'plain': False,
                    u'language': u'simple',
                    u"offset": offset,
                    u"limit": limit,
                    u"sort": u', '.join(sort_list),
                    u"filters": filters,
                }
            )
        except Exception:
            query_error = u'Invalid search query... ' + search_text
            dtdata = {u'error': query_error}
        else:
            data = []
            null_label = h.og_datatablesview_null_label()
            for row in response[u'records']:
                record = {colname.replace('.', ''): escape(str(null_label if row.get(colname, u'')
                                                               is None else row.get(colname, u'')))
                          for colname in cols}
                # the DT_RowId is used in DT to set an element id for each record
                record['DT_RowId'] = 'row' + str(row.get(u'_id', u''))
                data.append(record)

            dtdata = {
                u'draw': draw,
                u'recordsTotal': unfiltered_response.get(u'total', 0),
                u'recordsFiltered': response.get(u'total', 0),
                u'data': data
            }

    return json.dumps(dtdata)


def filtered_download(resource_view_id):
    params = json.loads(request.form[u'params'])
    resource_view = get_action(u'resource_view_show'
                               )(None, {
                                   u'id': resource_view_id
                               })

    search_text = str(params[u'search'][u'value'])
    view_filters = resource_view.get(u'filters', {})
    user_filters = str(params[u'filters'])
    filters = merge_filters(view_filters, user_filters)

    datastore_search = get_action(u'datastore_search')
    unfiltered_response = datastore_search(
        None, {
            u"resource_id": resource_view[u'resource_id'],
            u"limit": 0,
            u"filters": view_filters,
        }
    )

    cols = [f[u'id'] for f in unfiltered_response[u'fields']]
    if u'show_fields' in resource_view:
        if '_id' not in resource_view[u'show_fields']:
            resource_view[u'show_fields'].insert(0, '_id')
        cols = [c for c in cols if c in resource_view[u'show_fields']]

    sort_list = []
    for order in params[u'order']:
        sort_by_num = int(order[u'column'])
        sort_order = (u'desc' if order[u'dir'] == u'desc' else u'asc')
        sort_list.append(cols[sort_by_num] + u' ' + sort_order)

    cols = [c for (c, v) in zip(cols, params[u'visible']) if v]

    colsearch_dict = {}
    columns = params[u'columns']
    for column in columns:
        if column[u'search'][u'value']:
            v = column[u'search'][u'value']
            if v:
                k = column[u'name']
                # replace non-alphanumeric characters with FTS wildcard (_)
                v = re.sub(r'[^0-9a-zA-Z\-]+', '_', v)
                # append ':*' so we can do partial FTS searches
                colsearch_dict[k] = v + u':*'

    # Check for date range filters
    date_range_filter = None
    date_range_column = None
    filters_for_query = {}
    
    for filter_key, filter_values in filters.items():
        if filter_values:
            # Handle both single value and list of values
            values_to_check = filter_values if isinstance(filter_values, list) else [filter_values]
            has_date_range = False
            for filter_value in values_to_check:
                if filter_value:
                    # Check if this is a date range filter
                    is_date_range, start_date, end_date = is_date_range_filter(str(filter_value))
                    if is_date_range and is_date_column(filter_key, unfiltered_response[u'fields']):
                        # Store date range filter info
                        date_range_filter = (start_date, end_date)
                        date_range_column = filter_key
                        has_date_range = True
                        break
            
            # Add to filters_for_query if not a date range
            if not has_date_range:
                filters_for_query[filter_key] = filter_values
    
    # If we have a date range filter, use SQL query for export
    if date_range_filter:
        start_date, end_date = date_range_filter
        try:
            # Get all records using SQL query with date range
            # Use a large limit to get all records for export
            response = datastore_search_sql_date_range(
                resource_view[u'resource_id'],
                date_range_column,
                start_date,
                end_date,
                filters_for_query,
                sort_list,
                0,  # offset
                1000000,  # large limit to get all records
                cols
            )
            records = response.get(u'records', [])
        except Exception as e:
            # Fall back to regular search if SQL query fails
            data = {
                u"resource_id": resource_view[u'resource_id'],
                u"filters": filters_for_query,
                u"limit": 1000000,
                u"sort": u','.join(sort_list) if sort_list else None,
            }
            response = datastore_search(None, data)
            records = response.get(u'records', [])
    else:
        # No date range, use regular datastore_search
        # Build query string for FTS search
        if colsearch_dict:
            search_text = json.dumps(colsearch_dict)
        else:
            search_text = re.sub(r'[^0-9a-zA-Z\-]+', '_',
                                 search_text) + u':*' if search_text else ''
        
        # Use redirect to datastore.dump for non-date-range exports
        return h.redirect_to(
            h.url_for(
                u'datastore.dump',
                resource_id=resource_view[u'resource_id']) + u'?' + urlencode(
                {
                    u'q': search_text,
                    u'plain': False,
                    u'language': u'simple',
                    u'sort': u','.join(sort_list),
                    u'filters': json.dumps(filters_for_query),
                    u'format': request.form[u'format'],
                    u'fields': u','.join(cols),
                }))
    
    # Format the export based on requested format
    export_format = request.form.get(u'format', u'csv').lower()
    
    if export_format == u'csv':
        output = io.StringIO()
        if records:
            writer = csv.DictWriter(output, fieldnames=cols, extrasaction='ignore')
            writer.writeheader()
            for record in records:
                writer.writerow(record)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=export.csv'}
        )
    elif export_format == u'tsv':
        output = io.StringIO()
        if records:
            writer = csv.DictWriter(output, fieldnames=cols, delimiter='\t', extrasaction='ignore')
            writer.writeheader()
            for record in records:
                writer.writerow(record)
        return Response(
            output.getvalue(),
            mimetype='text/tab-separated-values',
            headers={'Content-Disposition': 'attachment; filename=export.tsv'}
        )
    elif export_format == u'json':
        return Response(
            json.dumps(records, indent=2),
            mimetype='application/json',
            headers={'Content-Disposition': 'attachment; filename=export.json'}
        )
    else:
        # Default to CSV
        output = io.StringIO()
        if records:
            writer = csv.DictWriter(output, fieldnames=cols, extrasaction='ignore')
            writer.writeheader()
            for record in records:
                writer.writerow(record)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=export.csv'}
        )


ogdatatablesdatefilterview.add_url_rule(
    u'/og_datatables_datefilter/ajax/<resource_view_id>',
    view_func=ajax, methods=[u'POST']
)

ogdatatablesdatefilterview.add_url_rule(
    u'/og_datatables_datefilter/filtered-download/<resource_view_id>',
    view_func=filtered_download, methods=[u'POST']
)
