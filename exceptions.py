# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 17:11:23 2022

@author: youwu
"""
# This code is part of Qiskit.
#
# (C) Copyright IBM 2018, 2019.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Exceptions related to the IBM Quantum Experience provider."""

from qiskit.exceptions import QiskitError


class KosakaQError(QiskitError):
    """Base class for errors raised by the provider modules."""
    pass


class KosakaQAccountError(KosakaQError):
    """Base class for errors raised by account management."""
    pass


class KosakaQAccountValueError(KosakaQError):
    """Value errors raised by account management."""


class KosakaQAccountCredentialsNotFound(KosakaQAccountError):
    """Errors raised when credentials are not found."""
    pass


class KosakaQAccountCredentialsInvalidFormat(KosakaQAccountError):
    """Errors raised when the credentials format is invalid."""
    pass


class KosakaQAccountCredentialsInvalidToken(KosakaQAccountError):
    """Errors raised when an IBM Quantum Experience token is invalid."""
    pass


class KosakaQAccountCredentialsInvalidUrl(KosakaQAccountError):
    """Errors raised when an IBM Quantum Experience URL is invalid."""
    pass


class KosakaQAccountMultipleCredentialsFound(KosakaQAccountError):
    """Errors raised when multiple credentials are found."""
    pass


class KosakaQProviderError(KosakaQAccountError):
    """Errors related to provider handling."""
    pass


class KosakaQBackendError(KosakaQError):
    """Base class for errors raised by the backend modules."""
    pass


class KosakaQBackendApiError(KosakaQBackendError):
    """Errors that occur unexpectedly when querying the server."""
    pass


class KosakaQBackendApiProtocolError(KosakaQBackendApiError):
    """Errors raised when an unexpected value is received from the server."""
    pass


class KosakaQBackendValueError(KosakaQBackendError, ValueError):
    """Value errors raised by the backend modules."""
    pass


class KosakaQBackendJobLimitError(KosakaQBackendError):
    """Errors raised when job limit is reached."""
    pass


class KosakaQInputValueError(KosakaQError):
    """Error raised due to invalid input value."""
    pass


class KosakaQNotAuthorizedError(KosakaQError):
    """Error raised when a service is invoked from an unauthorized account."""
    pass


class KosakaQApiError(KosakaQError):
    """Error raised when a server error encountered."""
    pass


class KosakaQRedcalibrationError(KosakaQError):
    """Error raised in Red_calibration.py."""
    pass


class RedCalibrationError(KosakaQError):
    """Error raised when red calibration is not done correctly."""

