from flask import request, url_for
from pytz import timezone

__all__ = (
    "pagination_headers",
    "is_hidden_field_filter",
    "url_for_related",
    "format_datetime",
    "format_price",
)


def pagination_headers(query, res, bp, per_page=20, **kwargs):
    links = []
    if query.has_next:
        next_url = bp.url_for(res, page=query.next_num, per_page=per_page, **kwargs)
        last_url = bp.url_for(res, page=query.pages, per_page=per_page, **kwargs)

        links.append('<{}>; rel="next"'.format(next_url))
        links.append('<{}>; rel="last"'.format(last_url))

    if query.page > 1:
        prev_url = bp.url_for(res, page=query.prev_num, per_page=per_page, **kwargs)
        first_url = bp.url_for(res, per_page=per_page, **kwargs)

        links.append('<{}>; rel="prev"'.format(prev_url))
        links.append('<{}>; rel="first"'.format(first_url))
    return ", ".join(links)


def is_hidden_field_filter(field):
    return field.type in ["HiddenField", "CSRFTokenField"]


def url_for_related(endpoint, remove_args=[], **kwargs):
    args = request.args.copy()
    for key in remove_args:
        args.pop(key, None)

    new_args = {}
    new_args.update(args)
    new_args.update(request.view_args)
    new_args.update(kwargs)
    return url_for(endpoint, **new_args)


def format_datetime(value, format="%b %d, %Y %-I:%M %p"):
    if not value:
        return ""
    if not hasattr(value, "tzinfo"):
        return value.strftime(format)
    est = timezone("US/Eastern")
    utc = timezone("UTC")
    if not value.tzinfo:
        tz_aware_dt = utc.localize(value)
    else:
        tz_aware_dt = value
    local_dt = tz_aware_dt.astimezone(est)
    return local_dt.strftime(format)


def format_price(value, format="${:,.2f}"):
    return format.format(value / 100)
