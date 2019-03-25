class ShellyException(Exception):
    """base shelly exception"""
    def __init__(self, message=None, errors=None):
        # Call the base class constructor with the parameters it needs
        super(ShellyException, self).__init__(message)
        # Now for your custom code...
        self.errors = errors


class ShellyNetworkException(ShellyException):
    """Shelly network exception"""
    def __init__(self, message=None, errors=None):
        # Call the base class constructor with the parameters it needs
        super(ShellyNetworkException, self).__init__(message)
        # Now for your custom code...
        self.errors = errors


class ShellyUnreachableException(ShellyNetworkException):
    """Shelly not available exception"""
    def __init__(self, message=None, errors=None):
        # Call the base class constructor with the parameters it needs
        super(ShellyUnreachableException, self).__init__(message)
        # Now for your custom code...
        self.errors = errors


class ShellyEmptyResponse(ShellyNetworkException):
    """Shelly not available exception"""
    def __init__(self, message=None, errors=None):
        # Call the base class constructor with the parameters it needs
        super(ShellyEmptyResponse, self).__init__(message)
        # Now for your custom code...
        self.errors = errors


class ShellyAccessForbitten(ShellyNetworkException):
    """Shelly login is wrong exception"""
    def __init__(self, message=None, errors=None):
        # Call the base class constructor with the parameters it needs
        super(ShellyAccessForbitten, self).__init__(message)
        # Now for your custom code...
        self.errors = errors
