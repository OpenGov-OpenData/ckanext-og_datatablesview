# encoding: utf-8

from six.moves.urllib.parse import urlencode
from six import text_type

from ckan.common import json
from ckan.plugins.toolkit import get_action, request, h, requires_ckan_version
from ckan.exceptions import CkanVersionException


def get_compatible_request_parameters():
    u'''
    Get Flask or Pylons request objects depending on CKAN version
    '''
    try:
        requires_ckan_version("2.9")
    except CkanVersionException:
        return request.params
    else:
        return request.form


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


def ajax(resource_view_id):
    resource_view = get_action(u'resource_view_show')(
        None, {u'id': resource_view_id})

    request_params = get_compatible_request_parameters()
    draw = int(request_params['draw'])
    search_text = text_type(request_params['search[value]'])
    offset = int(request_params['start'])
    limit = int(request_params['length'])
    view_filters = resource_view.get(u'filters', {})
    user_filters = text_type(request_params['filters'])
    filters = merge_filters(view_filters, user_filters)

    datastore_search = get_action(u'datastore_search')
    unfiltered_response = datastore_search(None, {
        u"resource_id": resource_view[u'resource_id'],
        u"limit": 0,
        u"filters": view_filters,
    })

    cols = [f['id'] for f in unfiltered_response['fields']]
    if u'show_fields' in resource_view:
        cols = [c for c in cols if c in resource_view['show_fields']]

    sort_list = []
    i = 0
    while True:
        if u'order[%d][column]' % i not in request_params:
            break
        sort_by_num = int(request_params[u'order[%d][column]' % i])
        sort_order = (
            u'desc' if request_params[u'order[%d][dir]' % i] == u'desc'
            else u'asc'
        )
        sort_list.append(cols[sort_by_num] + u' ' + sort_order)
        i += 1

    # Add default sorting
    if u'_id asc' not in sort_list and u'_id desc' not in sort_list:
        sort_list.append(u'_id asc')

    response = datastore_search(None, {
        u"q": search_text,
        u"resource_id": resource_view[u'resource_id'],
        u"offset": offset,
        u"limit": limit,
        u"sort": u', '.join(sort_list),
        u"filters": filters,
    })

    records_data = []
    for row in response[u'records']:
        record = [
            text_type(row.get(colname, u'')) if row.get(colname) is not None
            else u'' for colname in cols
        ]
        records_data.append(record)

    dtdata = {
        u'draw': draw,
        u'iTotalRecords': unfiltered_response.get(u'total', 0),
        u'iTotalDisplayRecords': response.get(u'total', 0),
        u'aaData': records_data
    }

    return json.dumps(dtdata)


def filtered_download(resource_view_id):
    request_params = get_compatible_request_parameters()
    params = json.loads(request_params['params'])
    resource_view = get_action(u'resource_view_show')(
        None, {u'id': resource_view_id})

    search_text = text_type(params['search']['value'])
    view_filters = resource_view.get(u'filters', {})
    user_filters = text_type(params['filters'])
    filters = merge_filters(view_filters, user_filters)

    datastore_search = get_action(u'datastore_search')
    unfiltered_response = datastore_search(None, {
        u"resource_id": resource_view[u'resource_id'],
        u"limit": 0,
        u"filters": view_filters,
    })

    cols = [f['id'] for f in unfiltered_response['fields']]
    if u'show_fields' in resource_view:
        cols = [c for c in cols if c in resource_view['show_fields']]

    sort_list = []
    for order in params['order']:
        sort_by_num = int(order['column'])
        sort_order = (
            u'desc' if order['dir'] == u'desc'
            else u'asc'
        )
        sort_list.append(cols[sort_by_num] + u' ' + sort_order)

    cols = [c for (c, v) in zip(cols, params['visible']) if v and c != '_id']

    datastore_dump_url = ''
    try:
        requires_ckan_version("2.9")
    except CkanVersionException:
        datastore_dump_url = h.url_for(
            controller=u'ckanext.datastore.controller:DatastoreController',
            action=u'dump',
            resource_id=resource_view[u'resource_id']
        )
    else:
        datastore_dump_url = h.url_for(
            u'datastore.dump',
            resource_id=resource_view[u'resource_id']
        )

    return h.redirect_to(
        datastore_dump_url +
        u'?' + urlencode({
            u'q': search_text,
            u'sort': u','.join(sort_list),
            u'filters': json.dumps(filters),
            u'format': request_params['format'],
            u'fields': u','.join(cols),
        })
    )
