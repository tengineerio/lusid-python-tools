import pandas as pd
import numpy as np
from lusidtools.cocoon import checkargs
from lusid.exceptions import ApiException


@checkargs
def check_dict_for_required_keys(
    target_dict: dict, target_name: str, required_keys: list
):
    """
    This function checks that a named dictionary contains a list of required keys
    :param dict target_dict: Dictionary to check for keys in
    :param str target_name: Variable name of dictionary
    :param list required_keys: List of required keys
    :return:
    """
    for key in required_keys:
        if key not in target_dict.keys():
            raise ValueError(
                f"'{key}' missing from {target_name}. {target_name} must include {required_keys}"
                f"as keys"
            )


def get_errors_from_response(list_of_API_exceptions: list):
    """
    This function gets the status code and reason from API exception
    :param list list_of_API_exceptions:
    :return pd.DataFrame: a Pandas DataFrame containing the reasons and status codes for ApiExceptions from a request
    """
    # check all items are ApiExceptions
    for i in list_of_API_exceptions:
        if not isinstance(i, ApiException):
            raise TypeError(
                f" Unexpected Error in response. Expected instance of ApiException, but got: {repr(i)}"
            )

    # get status and reason for each batch
    status = [item.status for item in list_of_API_exceptions]
    reason = [item.reason for item in list_of_API_exceptions]

    # transpose list of lists for insertion to dataframe
    items_error = np.array([reason, status]).T.tolist()

    return pd.DataFrame(items_error, columns=["error_items", "status"])


def get_portfolio_from_href(href: list, file_type: str):
    """
    This function finds the protfolio code contained within a href for a given file_type
    :param list href: Full href from LUSID response
    :param str file_type:
    :return list: portfolio codes taken from hrefs
    """

    # get portfolio codes from each href
    codes = [j[-2] for j in [i.split("/") for i in href]]

    return codes


@checkargs
def get_non_href_response(response: dict, file_type: str):
    items_success = [
        key for batch in response[file_type]["success"] for key in batch.values.keys()
    ]

    items_failed = [
        key for batch in response[file_type]["success"] for key in batch.failed.keys()
    ]
    return items_success, items_failed


def format_instruments_response(
    response: dict,
) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame):
    """
    This function unpacks a response from instrument requests and returns successful, failed and errored statuses for
    request constituents.

    :param dict response: response from Lusid-python-tools
    :return: pd.DataFrame: Successful calls from request
    :return: pd.DataFrame: Error responses from request that fail (APIExceptions: 400 errors)
    :return: pd.DataFrame: Failed responses that LUSID rejected
    """

    file_type = "instruments"
    check_dict_for_required_keys(
        response[file_type], f"Response from {file_type} request", ["errors", "success"]
    )

    # get success and failures
    items_success, items_failed = get_non_href_response(response, file_type)

    return (
        pd.DataFrame(items_success, columns=["successful items"]),
        get_errors_from_response(response[file_type]["errors"]),
        pd.DataFrame(items_failed, columns=["failed_items"]),
    )


def format_portfolios_response(response: dict) -> (pd.DataFrame, pd.DataFrame):
    """
    This function unpacks a response from portfolio requests and returns successful and errored statuses for
    request constituents.
    :param dict response: response from Lusid-python-tools
    :return: pd.DataFrame: Successful calls from request
    :return: pd.DataFrame: Error responses from request that fail (APIExceptions: 400 errors)
    """
    file_type = "portfolios"
    check_dict_for_required_keys(
        response[file_type], f"Response from {file_type} request", ["errors", "success"]
    )

    # get success
    items_success = [batch.id.code for batch in response[file_type]["success"]]

    errors = get_errors_from_response(response[file_type]["errors"])

    return (pd.DataFrame(items_success, columns=["successful items"]), errors)


def format_transactions_response(response: dict) -> (pd.DataFrame, pd.DataFrame):
    """
    This function unpacks a response from transaction requests and returns successful and errored statuses for
    request constituents.
    :param dict response: response from Lusid-python-tools
    :param str file_type: file_type of Lusid-python-tools
    :return: pd.DataFrame: Successful calls from request
    :return: pd.DataFrame: Error responses from request that fail (APIExceptions: 400 errors)
    """
    file_type = "transactions"

    check_dict_for_required_keys(
        response[file_type], f"Response from {file_type} request", ["errors", "success"]
    )

    # get success
    items_success = [batch.href for batch in response[file_type]["success"]]

    errors = get_errors_from_response(response[file_type]["errors"])

    return (
        pd.DataFrame(
            get_portfolio_from_href(items_success, file_type),
            columns=["successful items"],
        ),
        errors,
    )


def format_holdings_response(response: dict) -> (pd.DataFrame, pd.DataFrame):
    """
    This function unpacks a response from holding requests and returns successful and errored statuses for
    request constituents.
    :param dict response: response from Lusid-python-tools
    :return: pd.DataFrame: Successful calls from request
    :return: pd.DataFrame: Error responses from request that fail (APIExceptions: 400 errors)
    """
    file_type = "holdings"
    check_dict_for_required_keys(
        response[file_type], f"Response from {file_type} request", ["errors", "success"]
    )

    # get success
    items_success = [batch.href for batch in response[file_type]["success"]]

    errors = get_errors_from_response(response[file_type]["errors"])

    return (
        pd.DataFrame(
            get_portfolio_from_href(items_success, file_type),
            columns=["successful items"],
        ),
        errors,
    )


def format_quotes_response(
    response: dict,
) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame):
    """
    This function unpacks a response from quotes requests and returns successful, failed and errored statuses for
    request constituents.
    :param dict response: response from Lusid-python-tools
    :return: pd.DataFrame: Successful calls from request
    :return: pd.DataFrame: Error responses from request that fail (APIExceptions: 400 errors)
    :return: pd.DataFrame: Failed responses that LUSID rejected
    """
    file_type = "quotes"

    check_dict_for_required_keys(
        response[file_type], f"Response from {file_type} request", ["errors", "success"]
    )
    items_success, items_failed = get_non_href_response(response, file_type)

    return (
        pd.DataFrame(items_success, columns=["successful items"]),
        get_errors_from_response(response[file_type]["errors"]),
        pd.DataFrame(items_failed, columns=["failed_items"]),
    )
