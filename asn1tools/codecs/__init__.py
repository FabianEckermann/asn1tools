import binascii


class EncodeError(Exception):
    """General ASN.1 encode error.

    """

    pass


class DecodeError(Exception):
    """General ASN.1 decode error.

    """

    def __init__(self, message):
        super(DecodeError, self).__init__()
        self.message = message
        self.location = []

    def __str__(self):
        return "{}: {}".format(': '.join(self.location[::-1]),
                               self.message)


class DecodeTagError(DecodeError):
    """ASN.1 tag decode error.

    """

    def __init__(self, type_name, expected_tag, actual_tag, offset):
        message = 'expected {} with tag 0x{} but got 0x{} at offset {}'.format(
            type_name,
            binascii.hexlify(expected_tag).decode('ascii'),
            binascii.hexlify(actual_tag).decode('ascii'),
            offset)
        super(DecodeTagError, self).__init__(message)
