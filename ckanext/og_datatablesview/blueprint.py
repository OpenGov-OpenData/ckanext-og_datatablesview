# encoding: utf-8

from urllib.parse import urlencode
from html import escape
from itertools import chain
import csv
import io

from flask import Blueprint, Response


from ckan.common import json
from ckan.plugins.toolkit import get_action, request, h, abort
from ckanext.datastore.writer import xml_writer
import re

ogdatatablesview = Blueprint(u'ogdatatablesview', __name__)

# Page size used when streaming a null-filter export, matching CKAN's
# datastore dump (ckanext.datastore.blueprint.PAGINATE_BY).
EXPORT_PAGINATE_BY = 32000


def format_fts_query(search_value):
    u'''
    Format search value for FTS query with prefix matching.
    Handles compound words (with slashes/apostrophes) by using OR for parts.
    '''
    if not search_value:
        return u''
    space_separated = search_value.split()
    processed_terms = []
    for word in space_separated:
        if word:
            is_date = re.match(r'^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}$', word)
            if is_date:
                processed_terms.append(word + u':*')
                continue
            # replace non-alphanumeric characters with FTS wildcard (_)
            processed = re.sub(r'[^0-9a-zA-Z\-]+', '_', word)
            if processed:
                if '_' in processed:
                    # Compound word: use OR for parts
                    parts = [p for p in processed.split('_') if p]
                    if len(parts) > 1:
                        processed_terms.append(u'(' + u' | '.join([p + u':*' for p in parts]) + u')')
                    else:
                        processed_terms.append(parts[0] + u':*')
                else:
                    # append ':*' so we can do partial FTS searches
                    processed_terms.append(processed + u':*')
    if not processed_terms:
        return u''
    if len(processed_terms) > 1:
        return u' & '.join(processed_terms)
    return processed_terms[0]


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


def _quote_identifier(name):
    u'''Quote an identifier (column/table name) for SQL, escaping any
    embedded double quotes and stripping NUL bytes (mirrors CKAN's
    ckanext.datastore.backend.postgres.identifier).'''
    return u'"{}"'.format(str(name).replace(u'"', u'""').replace(u'\0', u''))


def _quote_literal(value):
    u'''Quote a string literal for SQL, escaping any embedded single
    quotes and stripping NUL bytes (mirrors CKAN's
    ckanext.datastore.backend.postgres.literal_string).'''
    return u"'{}'".format(str(value).replace(u"'", u"''").replace(u'\0', u''))


def build_filter_where_fragments(filters):
    u'''
    Split merged filters into SQL WHERE fragments.

    A filter whose value list contains an empty string is treated as a
    "null" filter (the Add Filter dropdown encodes the null option as an
    empty value). Those are turned into ``IS NULL OR = ''`` clauses so they
    match SQL NULLs, which the standard datastore_search filters never do.

    Returns a tuple ``(null_clauses, regular_clauses)`` of SQL fragment
    strings (no leading ``AND``). Null clauses are parenthesised because
    they contain ``OR``.

    >>> build_filter_where_fragments({u'Status': [u'']})
    ([u'("Status" IS NULL OR "Status" = \'\')'], [])
    '''
    null_clauses = []
    regular_clauses = []
    for col, values in filters.items():
        if not isinstance(values, list):
            values = [values]
        empties = [v for v in values if v == u'']
        reals = [v for v in values if v != u'']
        safe_col = _quote_identifier(col)
        if empties:
            parts = [
                u'{} IS NULL'.format(safe_col),
                u"{} = ''".format(safe_col),
            ]
            if reals:
                values_sql = u', '.join(_quote_literal(v) for v in reals)
                parts.append(u'{} IN ({})'.format(safe_col, values_sql))
            null_clauses.append(u'({})'.format(u' OR '.join(parts)))
        elif reals:
            if len(reals) == 1:
                regular_clauses.append(
                    u'{} = {}'.format(safe_col, _quote_literal(reals[0]))
                )
            else:
                values_sql = u', '.join(_quote_literal(v) for v in reals)
                regular_clauses.append(
                    u'{} IN ({})'.format(safe_col, values_sql)
                )
    return null_clauses, regular_clauses


def build_fts_where_fragment(colsearch_dict, plain_tsquery):
    u'''
    Build the SQL WHERE fragment that reproduces datastore_search's
    full-text ``q`` behaviour so search keeps working under the SQL path.

    Per-column searches (``colsearch_dict``) take precedence over the
    global search (``plain_tsquery``), matching the existing ajax logic.
    Returns a fragment string or ``None`` when there is no search.
    '''
    if colsearch_dict:
        clauses = []
        for col, tsquery in colsearch_dict.items():
            clauses.append(
                u"to_tsvector('simple', cast({} as text)) "
                u"@@ to_tsquery('simple', {})".format(
                    _quote_identifier(col), _quote_literal(tsquery)
                )
            )
        return u' AND '.join(clauses) if clauses else None
    if plain_tsquery:
        return u"_full_text @@ to_tsquery('simple', {})".format(
            _quote_literal(plain_tsquery)
        )
    return None


def _build_order_by(sort_list):
    u'''Build a quoted ORDER BY clause from a list of "col asc"/"col desc"
    strings, handling column names containing spaces.'''
    if not sort_list:
        return u'"_id" asc'
    quoted = []
    for sort_item in sort_list:
        parts = sort_item.rsplit(None, 1)
        if len(parts) == 2:
            col_name, direction = parts
            quoted.append(
                u'{} {}'.format(_quote_identifier(col_name), direction)
            )
        else:
            quoted.append(_quote_identifier(sort_item))
    return u', '.join(quoted)


def _build_where_clause(null_clauses, regular_clauses, fts_fragment):
    u'''Join the null/regular filter clauses and the FTS fragment into a
    single SQL WHERE expression (no leading ``WHERE``).'''
    where_clauses = list(null_clauses) + list(regular_clauses)
    if fts_fragment:
        where_clauses.append(fts_fragment)
    return u' AND '.join(where_clauses) if where_clauses else u'1=1'


def _build_select_fields(cols):
    u'''Build the quoted SELECT field list, or ``*`` when no cols given.'''
    if cols:
        return u', '.join(_quote_identifier(c) for c in cols)
    return u'*'


def datastore_search_sql_null_filter(resource_id, null_clauses,
                                     regular_clauses, fts_fragment,
                                     sort_list, offset, limit, cols):
    u'''
    Run a datastore_search_sql query combining null filter clauses,
    regular filter clauses and the full-text search fragment. Returns a
    dict with the same shape as datastore_search ({records, total, fields})
    so callers can render it unchanged.
    '''
    datastore_search_sql = get_action(u'datastore_search_sql')

    where_clause = _build_where_clause(
        null_clauses, regular_clauses, fts_fragment
    )
    select_fields = _build_select_fields(cols)
    order_by = _build_order_by(sort_list)
    safe_resource_id = _quote_identifier(resource_id)

    sql = (
        u'SELECT {select_fields} FROM {resource_id} WHERE {where_clause} '
        u'ORDER BY {order_by} LIMIT {limit} OFFSET {offset}'
    ).format(
        select_fields=select_fields,
        resource_id=safe_resource_id,
        where_clause=where_clause,
        order_by=order_by,
        limit=int(limit),
        offset=int(offset),
    )

    count_sql = (
        u'SELECT COUNT(*) as total FROM {resource_id} WHERE {where_clause}'
    ).format(
        resource_id=safe_resource_id,
        where_clause=where_clause,
    )

    response = datastore_search_sql(None, {u'sql': sql})
    count_response = datastore_search_sql(None, {u'sql': count_sql})

    records = response.get(u'records', [])
    count_records = count_response.get(u'records', [])
    total = int(count_records[0].get(u'total', 0)) if count_records else 0

    return {
        u'records': records,
        u'total': total,
        u'fields': [{u'id': c} for c in cols],
    }


def _iter_sql_null_filter_records(resource_id, null_clauses, regular_clauses,
                                  fts_fragment, sort_list, cols,
                                  paginate_by=EXPORT_PAGINATE_BY):
    u'''
    Yield records for a null-filter query page by page via
    datastore_search_sql, so an export never loads the whole result set
    into memory at once and is not silently capped at a fixed limit.
    '''
    datastore_search_sql = get_action(u'datastore_search_sql')

    where_clause = _build_where_clause(
        null_clauses, regular_clauses, fts_fragment
    )
    select_fields = _build_select_fields(cols)
    order_by = _build_order_by(sort_list)
    safe_resource_id = _quote_identifier(resource_id)

    offset = 0
    while True:
        sql = (
            u'SELECT {select_fields} FROM {resource_id} '
            u'WHERE {where_clause} ORDER BY {order_by} '
            u'LIMIT {limit} OFFSET {offset}'
        ).format(
            select_fields=select_fields,
            resource_id=safe_resource_id,
            where_clause=where_clause,
            order_by=order_by,
            limit=int(paginate_by),
            offset=int(offset),
        )
        response = datastore_search_sql(None, {u'sql': sql})
        records = response.get(u'records', [])
        for record in records:
            yield record
        if len(records) < paginate_by:
            break
        offset += paginate_by


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
    i = 0
    while True:
        if u'columns[%d][search][value]' % i not in request.form:
            break
        v = str(request.form[u'columns[%d][search][value]' % i])
        if v:
            k = str(request.form[u'columns[%d][name]' % i])
            colsearch_dict[k] = format_fts_query(v)
        i += 1

    # A filter whose value is an empty string is the "null" option from the
    # Add Filter dropdown. datastore_search filters can't match SQL NULLs, so
    # those queries are routed through datastore_search_sql instead. When no
    # null filters are present, keep using datastore_search unchanged.
    null_clauses, regular_clauses = build_filter_where_fragments(filters)
    dtdata = None

    if null_clauses:
        plain_tsquery = (
            format_fts_query(search_text)
            if (not colsearch_dict and search_text) else None
        )
        fts_fragment = build_fts_where_fragment(colsearch_dict, plain_tsquery)
        try:
            response = datastore_search_sql_null_filter(
                resource_view[u'resource_id'],
                null_clauses,
                regular_clauses,
                fts_fragment,
                sort_list,
                offset,
                limit,
                cols,
            )
        except Exception:
            dtdata = {u'error': u'Invalid search query...'}
    else:
        if colsearch_dict:
            search_text = json.dumps(colsearch_dict)
        else:
            search_text = format_fts_query(search_text) if search_text else u''

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
            dtdata = {u'error': u'Invalid search query... ' + search_text}

    if dtdata is None:
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
                colsearch_dict[k] = format_fts_query(v)

    # When a null filter is present, datastore.dump can't express IS NULL, so
    # build the export response here via datastore_search_sql. Otherwise keep
    # the existing redirect to datastore.dump unchanged.
    null_clauses, regular_clauses = build_filter_where_fragments(filters)

    if not null_clauses:
        if colsearch_dict:
            search_text = json.dumps(colsearch_dict)
        else:
            search_text = format_fts_query(search_text) if search_text else ''

        return h.redirect_to(
            h.url_for(
                u'datastore.dump',
                resource_id=resource_view[u'resource_id']) + u'?' + urlencode(
                {
                    u'q': search_text,
                    u'plain': False,
                    u'language': u'simple',
                    u'sort': u','.join(sort_list),
                    u'filters': json.dumps(filters),
                    u'format': request.form[u'format'],
                    u'fields': u','.join(cols),
                }))

    plain_tsquery = (
        format_fts_query(search_text)
        if (not colsearch_dict and search_text) else None
    )
    fts_fragment = build_fts_where_fragment(colsearch_dict, plain_tsquery)

    export_format = request.form.get(u'format', u'csv').lower()

    # datastore.dump streams every row and supports csv/tsv/json/xml; mirror
    # that here by streaming the null-filter result page by page instead of
    # buffering the whole (potentially capped) result set in memory.
    record_iter = _iter_sql_null_filter_records(
        resource_view[u'resource_id'],
        null_clauses,
        regular_clauses,
        fts_fragment,
        sort_list,
        cols,
    )

    # Pull the first page eagerly so a query failure (e.g. datastore SQL
    # search disabled) surfaces as a clean error here, before any response
    # body has been streamed, rather than silently exporting wrong data.
    try:
        first_record = next(record_iter)
        records = chain([first_record], record_iter)
    except StopIteration:
        records = iter(())
    except Exception:
        return abort(400, u'Invalid search query...')

    def stream_records():
        return records

    if export_format == u'xml':
        def generate_xml():
            with xml_writer([{u'id': c} for c in cols]) as writer:
                for record in stream_records():
                    yield writer.write_records(
                        [{c: record.get(c) for c in cols}]
                    )
                yield writer.end_file()
        return Response(
            generate_xml(),
            mimetype=u'text/xml; charset=utf-8',
            headers={u'Content-Disposition':
                     u'attachment; filename=export.xml'}
        )

    if export_format == u'json':
        def generate_json():
            yield u'[\n'
            first = True
            for record in stream_records():
                row = {c: record.get(c) for c in cols}
                yield (u'' if first else u',\n') + json.dumps(row)
                first = False
            yield u'\n]'
        return Response(
            generate_json(),
            mimetype=u'application/json; charset=utf-8',
            headers={u'Content-Disposition':
                     u'attachment; filename=export.json'}
        )

    delimiter = u'\t' if export_format == u'tsv' else u','
    mimetype = (u'text/tab-separated-values; charset=utf-8'
                if export_format == u'tsv' else u'text/csv; charset=utf-8')
    filename = u'export.tsv' if export_format == u'tsv' else u'export.csv'

    def generate_delimited():
        buf = io.StringIO()
        writer = csv.DictWriter(
            buf, fieldnames=cols, delimiter=delimiter, extrasaction=u'ignore'
        )
        # Always emit the header row, even for an empty result set, so the
        # download matches datastore.dump rather than being a 0-byte file.
        writer.writeheader()
        yield buf.getvalue()
        buf.seek(0)
        buf.truncate(0)
        for record in stream_records():
            writer.writerow(record)
            yield buf.getvalue()
            buf.seek(0)
            buf.truncate(0)

    return Response(
        generate_delimited(),
        mimetype=mimetype,
        headers={u'Content-Disposition':
                 u'attachment; filename={}'.format(filename)}
    )


ogdatatablesview.add_url_rule(
    u'/og_datatables/ajax/<resource_view_id>',
    view_func=ajax, methods=[u'POST']
)

ogdatatablesview.add_url_rule(
    u'/og_datatables/filtered-download/<resource_view_id>',
    view_func=filtered_download, methods=[u'POST']
)
