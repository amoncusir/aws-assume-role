import typing


def is_optional(field):
    return typing.get_origin(field) is typing.Union and \
           type(None) in typing.get_args(field)
