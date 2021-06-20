""" Custom Exceptions for IGLib library.

Authored By Ryan Maugin (@ryanmaugv1)
"""


class IGClientException(Exception):
    """Exceptions thrown for validation/logical errors in client."""
    pass


class IGServerException(Exception):
    """Exception thrown for IG server request error response."""
    pass
