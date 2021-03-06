import unittest
import timeit
import sys
from copy import deepcopy

import asn1tools

sys.path.append('tests/files')
sys.path.append('tests/files/3gpp')
sys.path.append('tests/files/ietf')

from rrc_8_6_0 import EXPECTED as RRC_8_6_0
from rfc4511 import EXPECTED as RFC4511
from rfc5280 import EXPECTED as RFC5280
from rfc5280_modified import RFC5280_MODIFIED
from zforce import EXPECTED as ZFORCE


class Asn1ToolsBerTest(unittest.TestCase):

    maxDiff = None

    def test_foo(self):
        foo = asn1tools.compile_files(['tests/files/foo.asn'])

        self.assertEqual(len(foo.types), 2)
        self.assertTrue(foo.types['Question'] is not None)
        self.assertTrue(foo.types['Answer'] is not None)
        self.assertEqual(len(foo.modules), 1)
        self.assertTrue(foo.modules['Foo'] is not None)

        # Encode a question.
        encoded = foo.encode('Question',
                             {'id': 1, 'question': 'Is 1+1=3?'})
        self.assertEqual(encoded, b'0\x0e\x02\x01\x01\x16\x09Is 1+1=3?')

        # Decode the encoded question.
        decoded = foo.decode('Question', encoded)
        self.assertEqual(decoded, {'id': 1, 'question': 'Is 1+1=3?'})

        # Encode an answer.
        encoded = foo.encode('Answer', {'id': 1, 'answer': False})
        self.assertEqual(encoded, b'0\x06\x02\x01\x01\x01\x01\x00')

        # Decode the encoded answer.
        decoded = foo.decode('Answer', encoded)
        self.assertEqual(decoded, {'id': 1, 'answer': False})

        # Encode a question with missing field 'id'.
        with self.assertRaises(asn1tools.EncodeError) as cm:
            encoded = foo.encode('Question', {'question': 'Is 1+1=3?'})

        self.assertEqual(
            str(cm.exception),
            "member 'id' not found in {'question': 'Is 1+1=3?'}")

    def test_decode_length(self):
        foo = asn1tools.compile_files('tests/files/foo.asn')

        # The length can be decoded.
        datas = [
            (b'0\x0e\x02\x01\x01\x16\x09Is 1+1=3?', 16),
            (b'0\x10\x02\x02\x01\x16\x09Is 1+10=14?', 18),
            (b'0\x0d', 15),
            (b'0\x84\x00\x00\x00\xb8', 190)
        ]

        for encoded_message, decoded_length in datas:
            length = foo.decode_length(encoded_message)
            self.assertEqual(length, decoded_length)

        # The length cannot be decoded.
        datas = [
            b'0',
            b'',
            b'0\x84\x00\x00\x00'
        ]

        for encoded_message in datas:
            with self.assertRaises(asn1tools.DecodeError) as cm:
                foo.decode_length(encoded_message)

            self.assertEqual(str(cm.exception), ': Not enough data.')

    def test_complex(self):
        cmplx = asn1tools.compile_files('tests/files/complex.asn')

        decoded_message = {
            'boolean': True,
            'integer': -7,
            'bit-string': (b'\x80', 3),
            'octet-string': b'\x31\x32',
            'null': None,
            'object-identifier': '1.3.2',
            'enumerated': 'one',
            'sequence': {},
            'ia5-string': 'foo'
        }

        encoded_message = (
            b'\x30\x1e\x01\x01\xff\x02\x01\xf9\x03\x02\x05\x80\x04\x02\x31\x32'
            b'\x05\x00\x06\x02\x2b\x02\x0a\x01\x01\x30\x00\x16\x03\x66\x6f\x6f'
        )

        encoded = cmplx.encode('AllUniversalTypes', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = cmplx.decode('AllUniversalTypes', encoded_message)
        self.assertEqual(decoded, decoded_message)

        # Ivalid enumeration value.
        decoded_message = {
            'boolean': True,
            'integer': -7,
            'bit-string': (b'\x80', 3),
            'octet-string': b'\x31\x32',
            'null': None,
            'object-identifier': '1.3.2',
            'enumerated': 'three',
            'sequence': {},
            'ia5-string': 'foo'
        }

        with self.assertRaises(asn1tools.EncodeError) as cm:
            cmplx.encode('AllUniversalTypes', decoded_message)

        self.assertEqual(
            str(cm.exception),
            "enumeration value 'three' not found in ['one', 'two']")

    def test_rrc_8_6_0(self):
        rrc = asn1tools.compile_dict(deepcopy(RRC_8_6_0))

        # Message 1.
        decoded_message = {
            'message': {
                'c1' : {
                    'paging': {
                        'systemInfoModification': 'true',
                        'nonCriticalExtension': {
                        }
                    }
                }
            }
        }

        encoded_message = b'0\x0b\xa0\t\xa0\x07\xa0\x05\x81\x01\x00\xa3\x00'

        encoded = rrc.encode('PCCH-Message', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = rrc.decode('PCCH-Message', encoded)
        self.assertEqual(decoded, decoded_message)

        # Message 2.
        decoded_message = {
            'message': {
                'c1' : {
                    'paging': {
                    }
                }
            }
        }

        encoded_message = b'0\x06\xa0\x04\xa0\x02\xa0\x00'

        encoded = rrc.encode('PCCH-Message', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = rrc.decode('PCCH-Message', encoded)
        self.assertEqual(decoded, decoded_message)

        # Message 3.
        decoded_message = {
            'message': {
                'dl-Bandwidth': 'n6',
                'phich-Config': {
                    'phich-Duration': 'normal',
                    'phich-Resource': 'half'
                },
                'systemFrameNumber': (b'\x12', 8),
                'spare': (b'\x34\x56', 10)
            }
        }

        encoded_message = (
            b'0\x16\xa0\x14\x80\x01\x00\xa1\x06\x80\x01\x00\x81\x01\x01\x82'
            b'\x02\x00\x12\x83\x03\x064V'
        )

        encoded = rrc.encode('BCCH-BCH-Message', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = rrc.decode('BCCH-BCH-Message', encoded)
        self.assertEqual(decoded, decoded_message)

        # Message 4.
        decoded_message = {
            'message': {
                'c1': {
                    'systemInformation': {
                        'criticalExtensions': {
                            'systemInformation-r8': {
                                'sib-TypeAndInfo': [
                                    {
                                        'sib2': {
                                            'ac-BarringInfo': {
                                                'ac-BarringForEmergency': True,
                                                'ac-BarringForMO-Data': {
                                                    'ac-BarringFactor': 'p95',
                                                    'ac-BarringTime': 's128',
                                                    'ac-BarringForSpecialAC': (b'\xf0', 5)
                                                }
                                            },
                                            'radioResourceConfigCommon': {
                                                'rach-ConfigCommon': {
                                                    'preambleInfo': {
                                                        'numberOfRA-Preambles': 'n24',
                                                        'preamblesGroupAConfig': {
                                                            'sizeOfRA-PreamblesGroupA': 'n28',
                                                            'messageSizeGroupA': 'b144',
                                                            'messagePowerOffsetGroupB': 'minusinfinity'
                                                        }
                                                    },
                                                    'powerRampingParameters': {
                                                        'powerRampingStep': 'dB0',
                                                        'preambleInitialReceivedTargetPower': 'dBm-102'
                                                    },
                                                    'ra-SupervisionInfo': {
                                                        'preambleTransMax': 'n8',
                                                        'ra-ResponseWindowSize': 'sf6',
                                                        'mac-ContentionResolutionTimer': 'sf48'
                                                    },
                                                    'maxHARQ-Msg3Tx': 8
                                                },
                                                'bcch-Config': {
                                                    'modificationPeriodCoeff': 'n2'
                                                },
                                                'pcch-Config': {
                                                    'defaultPagingCycle': 'rf256',
                                                    'nB': 'twoT'
                                                },
                                                'prach-Config': {
                                                    'rootSequenceIndex': 836,
                                                    'prach-ConfigInfo': {
                                                        'prach-ConfigIndex': 33,
                                                        'highSpeedFlag': False,
                                                        'zeroCorrelationZoneConfig': 10,
                                                        'prach-FreqOffset': 64
                                                    }
                                                },
                                                'pdsch-ConfigCommon': {
                                                    'referenceSignalPower': -60,
                                                    'p-b': 2
                                                },
                                                'pusch-ConfigCommon': {
                                                    'pusch-ConfigBasic': {
                                                        'n-SB': 1,
                                                        'hoppingMode': 'interSubFrame',
                                                        'pusch-HoppingOffset': 10,
                                                        'enable64QAM': False
                                                    },
                                                    'ul-ReferenceSignalsPUSCH': {
                                                        'groupHoppingEnabled': True,
                                                        'groupAssignmentPUSCH': 22,
                                                        'sequenceHoppingEnabled': False,
                                                        'cyclicShift': 5
                                                    }
                                                },
                                                'pucch-ConfigCommon': {
                                                    'deltaPUCCH-Shift': 'ds1',
                                                    'nRB-CQI': 98,
                                                    'nCS-AN': 4,
                                                    'n1PUCCH-AN': 2047
                                                },
                                                'soundingRS-UL-ConfigCommon': {
                                                    'setup': {
                                                        'srs-BandwidthConfig': 'bw0',
                                                        'srs-SubframeConfig': 'sc4',
                                                        'ackNackSRS-SimultaneousTransmission': True
                                                    }
                                                },
                                                'uplinkPowerControlCommon': {
                                                    'p0-NominalPUSCH': -126,
                                                    'alpha': 'al0',
                                                    'p0-NominalPUCCH': -127,
                                                    'deltaFList-PUCCH': {
                                                        'deltaF-PUCCH-Format1': 'deltaF-2',
                                                        'deltaF-PUCCH-Format1b': 'deltaF1',
                                                        'deltaF-PUCCH-Format2': 'deltaF0',
                                                        'deltaF-PUCCH-Format2a': 'deltaF-2',
                                                        'deltaF-PUCCH-Format2b': 'deltaF0'
                                                    },
                                                    'deltaPreambleMsg3': -1
                                                },
                                                'ul-CyclicPrefixLength': 'len1'
                                            },
                                            'ue-TimersAndConstants': {
                                                't300': 'ms100',
                                                't301': 'ms200',
                                                't310': 'ms50',
                                                'n310': 'n2',
                                                't311': 'ms30000',
                                                'n311': 'n2'
                                            },
                                            'freqInfo': {
                                                'additionalSpectrumEmission': 3
                                            },
                                            'timeAlignmentTimerCommon': 'sf500'
                                        }
                                    },
                                    {
                                        'sib3': {
                                            'cellReselectionInfoCommon': {
                                                'q-Hyst': 'dB0',
                                                'speedStateReselectionPars': {
                                                    'mobilityStateParameters': {
                                                        't-Evaluation': 's180',
                                                        't-HystNormal': 's180',
                                                        'n-CellChangeMedium': 1,
                                                        'n-CellChangeHigh': 16
                                                    },
                                                    'q-HystSF': {
                                                        'sf-Medium': 'dB-6',
                                                        'sf-High': 'dB-4'
                                                    }
                                                }
                                            },
                                            'cellReselectionServingFreqInfo': {
                                                'threshServingLow': 7,
                                                'cellReselectionPriority': 3
                                            },
                                            'intraFreqCellReselectionInfo': {
                                                'q-RxLevMin': -33,
                                                's-IntraSearch': 0,
                                                'presenceAntennaPort1': False,
                                                'neighCellConfig': (b'\x80', 2),
                                                't-ReselectionEUTRA': 4
                                            }
                                        }
                                    },
                                    {
                                        'sib4': {
                                        }
                                    },
                                    {
                                        'sib5': {
                                            'interFreqCarrierFreqList': [
                                                {
                                                    'dl-CarrierFreq': 1,
                                                    'q-RxLevMin': -45,
                                                    't-ReselectionEUTRA': 0,
                                                    'threshX-High': 31,
                                                    'threshX-Low': 29 ,
                                                    'allowedMeasBandwidth': 'mbw6',
                                                    'presenceAntennaPort1': True,
                                                    'q-OffsetFreq': 'dB0',
                                                    'neighCellConfig': (b'\x00', 2)
                                                }
                                            ]
                                        }
                                    },
                                    {
                                        'sib6': {
                                            't-ReselectionUTRA': 3
                                        }
                                    },
                                    {
                                        'sib7': {
                                            't-ReselectionGERAN': 3
                                        }
                                    },
                                    {
                                        'sib8': {
                                            'parameters1XRTT': {
                                                'longCodeState1XRTT': (b'\x01\x23\x45\x67\x89\x00', 42)
                                            }
                                        }
                                    },
                                    {
                                        'sib9': {
                                            'hnb-Name': b'\x34'
                                        }
                                    },
                                    {
                                        'sib10': {
                                            'messageIdentifier': (b'\x23\x34', 16),
                                            'serialNumber': (b'\x12\x34', 16),
                                            'warningType': b'\x32\x12'
                                        }
                                    },
                                    {
                                        'sib11': {
                                            'messageIdentifier': (b'\x67\x88', 16),
                                            'serialNumber': (b'\x54\x35', 16),
                                            'warningMessageSegmentType': 'notLastSegment',
                                            'warningMessageSegmentNumber': 19,
                                            'warningMessageSegment': b'\x12'
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }

        encoded_message = (
            b'\x30\x82\x01\x93\xa0\x82\x01\x8f\xa0\x82\x01\x8b\xa0\x82\x01'
            b'\x87\xa0\x82\x01\x83\xa0\x82\x01\x7f\xa0\x82\x01\x7b\xa0\x81'
            b'\xdd\xa0\x0f\x80\x01\xff\xa2\x0a\x80\x01\x0f\x81\x01\x05\x82'
            b'\x02\x03\xf0\xa1\x81\xad\xa0\x26\xa0\x0e\x80\x01\x05\xa1\x09'
            b'\x80\x01\x06\x81\x01\x01\x82\x01\x00\xa1\x06\x80\x01\x00\x81'
            b'\x01\x09\xa2\x09\x80\x01\x05\x81\x01\x04\x82\x01\x05\x83\x01'
            b'\x08\xa1\x03\x80\x01\x00\xa2\x06\x80\x01\x03\x81\x01\x01\xa3'
            b'\x12\x80\x02\x03\x44\xa1\x0c\x80\x01\x21\x81\x01\x00\x82\x01'
            b'\x0a\x83\x01\x40\xa4\x06\x80\x01\xc4\x81\x01\x02\xa5\x1c\xa0'
            b'\x0c\x80\x01\x01\x81\x01\x00\x82\x01\x0a\x83\x01\x00\xa1\x0c'
            b'\x80\x01\xff\x81\x01\x16\x82\x01\x00\x83\x01\x05\xa6\x0d\x80'
            b'\x01\x00\x81\x01\x62\x82\x01\x04\x83\x02\x07\xff\xa7\x0b\xa1'
            b'\x09\x80\x01\x00\x81\x01\x04\x82\x01\xff\xa8\x1d\x80\x01\x82'
            b'\x81\x01\x00\x82\x01\x81\xa3\x0f\x80\x01\x00\x81\x01\x00\x82'
            b'\x01\x01\x83\x01\x00\x84\x01\x01\x84\x01\xff\x89\x01\x00\xa2'
            b'\x12\x80\x01\x00\x81\x01\x01\x82\x01\x01\x83\x01\x01\x84\x01'
            b'\x06\x85\x01\x01\xa3\x03\x82\x01\x03\x85\x01\x00\xa1\x37\xa0'
            b'\x1b\x80\x01\x00\xa1\x16\xa0\x0c\x80\x01\x03\x81\x01\x03\x82'
            b'\x01\x01\x83\x01\x10\xa1\x06\x80\x01\x00\x81\x01\x01\xa1\x06'
            b'\x81\x01\x07\x82\x01\x03\xa2\x10\x80\x01\xdf\x82\x01\x00\x84'
            b'\x01\x00\x85\x02\x06\x80\x86\x01\x04\xa2\x00\xa3\x1d\xa0\x1b'
            b'\x30\x19\x80\x01\x01\x81\x01\xd3\x83\x01\x00\x85\x01\x1f\x86'
            b'\x01\x1d\x87\x01\x00\x88\x01\xff\x8a\x02\x06\x00\xa4\x03\x82'
            b'\x01\x03\xa5\x03\x80\x01\x03\xa6\x0b\xa3\x09\x81\x07\x06\x01'
            b'\x23\x45\x67\x89\x00\xa7\x03\x80\x01\x34\xa8\x0e\x80\x03\x00'
            b'\x23\x34\x81\x03\x00\x12\x34\x82\x02\x32\x12\xa9\x13\x80\x03'
            b'\x00\x67\x88\x81\x03\x00\x54\x35\x82\x01\x00\x83\x01\x13\x84'
            b'\x01\x12'
        )

        encoded = rrc.encode('BCCH-DL-SCH-Message', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = rrc.decode('BCCH-DL-SCH-Message', encoded)
        self.assertEqual(decoded, decoded_message)

    def test_rfc1157(self):
        rfc1157 = asn1tools.compile_files([
            'tests/files/ietf/rfc1155.asn',
            'tests/files/ietf/rfc1157.asn'
        ])

        # First message.
        decoded_message = {
            "version": 0,
            "community": b'public',
            "data": {
                "set-request": {
                    "request-id": 60,
                    "error-status": 0,
                    "error-index": 0,
                    "variable-bindings": [
                        {
                            "name": "1.3.6.1.4.1.253.8.51.10.2.1.7.10.14130101",
                            "value": {
                                "simple": {
                                    "string": (b'\x31\x37\x32\x2e\x33\x31'
                                               b'\x2e\x31\x39\x2e\x37\x33')
                                }
                            }
                        },
                        {
                            "name": "1.3.6.1.4.1.253.8.51.10.2.1.5.10.14130400",
                            "value": {
                                "simple": {
                                    "number": 2
                                }
                            }
                        },
                        {
                            "name": "1.3.6.1.4.1.253.8.51.10.2.1.7.10.14130102",
                            "value": {
                                "simple": {
                                    "string": (b'\x32\x35\x35\x2e\x32\x35'
                                               b'\x35\x2e\x32\x35\x35\x2e'
                                               b'\x30')
                                }
                            }
                        },
                        {
                            "name": "1.3.6.1.4.1.253.8.51.10.2.1.7.10.14130104",
                            "value": {
                                "simple": {
                                    "string": (b'\x31\x37\x32\x2e\x33\x31'
                                               b'\x2e\x31\x39\x2e\x32')
                                }
                            }
                        }
                    ]
                }
            }
        }

        encoded_message = (
            b'0\x81\x9f\x02\x01\x00\x04\x06public\xa3\x81\x91\x02'
            b'\x01<\x02\x01\x00\x02\x01\x000\x81\x850"\x06\x12+\x06'
            b'\x01\x04\x01\x81}\x083\n\x02\x01\x07\n\x86\xde\xb75'
            b'\x04\x0c172.31.19.730\x17\x06\x12+\x06\x01\x04\x01\x81'
            b'}\x083\n\x02\x01\x05\n\x86\xde\xb9`\x02\x01\x020#\x06'
            b'\x12+\x06\x01\x04\x01\x81}\x083\n\x02\x01\x07\n\x86\xde'
            b'\xb76\x04\r255.255.255.00!\x06\x12+\x06\x01\x04\x01\x81'
            b'}\x083\n\x02\x01\x07\n\x86\xde\xb78\x04\x0b172.31.19.2'
        )

        encoded = rfc1157.encode('Message', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = rfc1157.decode('Message', encoded_message)
        self.assertEqual(decoded, decoded_message)

        # Next message.
        decoded_message = {
            'version': 1,
            'community': b'community',
            'data': {
                'set-request': {
                    'request-id': 1687059484,
                    'error-status': 0,
                    'error-index': 0,
                    'variable-bindings': [
                        {
                            'name': '1.3.6.1.999.1.1',
                            'value': {
                                'simple': {
                                    'number': 1
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.2.1',
                            'value': {
                                'simple': {
                                    'string': b'f00'
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.3.1',
                            'value': {
                                'application-wide': {
                                    'address': {
                                        'internet': b'\xc0\xa8\x01\x01'
                                    }
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.4.1',
                            'value': {
                                'simple': {
                                    'object': '1.2.3.444.555'
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.1.2',
                            'value': {
                                'simple': {
                                    'number': 1
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.2.2',
                            'value': {
                                'simple': {
                                'string': b'f00'
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.3.2',
                            'value': {
                                'application-wide': {
                                    'address': {
                                        'internet': b'\xc0\xa8\x01\x01'
                                    }
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.4.2',
                            'value': {
                                'simple': {
                                    'object': '1.2.3.444.555'
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.1.3',
                            'value': {
                                'simple': {
                                    'number': 1
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.2.3',
                            'value': {
                                'simple': {
                                    'string': b'f00'
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.3.3',
                            'value': {
                                'application-wide': {
                                    'address': {
                                        'internet': b'\xc0\xa8\x01\x01'
                                    }
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.4.3',
                            'value': {
                                'simple': {
                                    'object': '1.2.3.444.555'
                                }
                            }
                        }
                    ]
                }
            }
        }

        encoded_message = (
            b'\x30\x81\xe6\x02\x01\x01\x04\x09\x63\x6f\x6d\x6d\x75\x6e\x69\x74'
            b'\x79\xa3\x81\xd5\x02\x04\x64\x8e\x7c\x1c\x02\x01\x00\x02\x01\x00'
            b'\x30\x81\xc6\x30\x0c\x06\x07\x2b\x06\x01\x87\x67\x01\x01\x02\x01'
            b'\x01\x30\x0e\x06\x07\x2b\x06\x01\x87\x67\x02\x01\x04\x03\x66\x30'
            b'\x30\x30\x0f\x06\x07\x2b\x06\x01\x87\x67\x03\x01\x40\x04\xc0\xa8'
            b'\x01\x01\x30\x11\x06\x07\x2b\x06\x01\x87\x67\x04\x01\x06\x06\x2a'
            b'\x03\x83\x3c\x84\x2b\x30\x0c\x06\x07\x2b\x06\x01\x87\x67\x01\x02'
            b'\x02\x01\x01\x30\x0e\x06\x07\x2b\x06\x01\x87\x67\x02\x02\x04\x03'
            b'\x66\x30\x30\x30\x0f\x06\x07\x2b\x06\x01\x87\x67\x03\x02\x40\x04'
            b'\xc0\xa8\x01\x01\x30\x11\x06\x07\x2b\x06\x01\x87\x67\x04\x02\x06'
            b'\x06\x2a\x03\x83\x3c\x84\x2b\x30\x0c\x06\x07\x2b\x06\x01\x87\x67'
            b'\x01\x03\x02\x01\x01\x30\x0e\x06\x07\x2b\x06\x01\x87\x67\x02\x03'
            b'\x04\x03\x66\x30\x30\x30\x0f\x06\x07\x2b\x06\x01\x87\x67\x03\x03'
            b'\x40\x04\xc0\xa8\x01\x01\x30\x11\x06\x07\x2b\x06\x01\x87\x67\x04'
            b'\x03\x06\x06\x2a\x03\x83\x3c\x84\x2b'
        )

        encoded = rfc1157.encode('Message', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = rfc1157.decode('Message', encoded_message)
        self.assertEqual(decoded, decoded_message)

        # Next message.
        decoded_message = {
            'version': 1,
            'community': b'community',
            'data': {
                'set-request': {
                    'request-id': 1687059484,
                    'error-status': 0,
                    'error-index': 0,
                    'variable-bindings': [
                        {
                            'name': '1.3.6.1.999.1.1',
                            'value': {
                                'simple': {
                                    'number': -1
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.2.1',
                            'value': {
                                'simple': {
                                    'string': b'f00'
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.4.1',
                            'value': {
                                'simple': {
                                    'object': '1.2.3.444.555'
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.4.1',
                            'value': {
                                'simple': {
                                    'empty': None
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.3.1',
                            'value': {
                                'application-wide': {
                                    'address': {
                                        'internet': b'\xc0\xa8\x01\x01'
                                    }
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.3.1',
                            'value': {
                                'application-wide': {
                                    'counter': 0
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.3.1',
                            'value': {
                                'application-wide': {
                                    'gauge': 4294967295
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.3.1',
                            'value': {
                                'application-wide': {
                                    'ticks': 88
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.3.1',
                            'value': {
                                'application-wide': {
                                    'arbitrary': b'\x31\x32\x33'
                                }
                            }
                        }
                    ]
                }
            }
        }

        encoded_message = (
            b'\x30\x81\xad\x02\x01\x01\x04\x09\x63\x6f\x6d\x6d\x75\x6e\x69\x74'
            b'\x79\xa3\x81\x9c\x02\x04\x64\x8e\x7c\x1c\x02\x01\x00\x02\x01\x00'
            b'\x30\x81\x8d\x30\x0c\x06\x07\x2b\x06\x01\x87\x67\x01\x01\x02\x01'
            b'\xff\x30\x0e\x06\x07\x2b\x06\x01\x87\x67\x02\x01\x04\x03\x66\x30'
            b'\x30\x30\x11\x06\x07\x2b\x06\x01\x87\x67\x04\x01\x06\x06\x2a\x03'
            b'\x83\x3c\x84\x2b\x30\x0b\x06\x07\x2b\x06\x01\x87\x67\x04\x01\x05'
            b'\x00\x30\x0f\x06\x07\x2b\x06\x01\x87\x67\x03\x01\x40\x04\xc0\xa8'
            b'\x01\x01\x30\x0c\x06\x07\x2b\x06\x01\x87\x67\x03\x01\x41\x01\x00'
            b'\x30\x10\x06\x07\x2b\x06\x01\x87\x67\x03\x01\x42\x05\x00\xff\xff'
            b'\xff\xff\x30\x0c\x06\x07\x2b\x06\x01\x87\x67\x03\x01\x43\x01\x58'
            b'\x30\x0e\x06\x07\x2b\x06\x01\x87\x67\x03\x01\x44\x03\x31\x32\x33'
        )

        encoded = rfc1157.encode('Message', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = rfc1157.decode('Message', encoded_message)
        self.assertEqual(decoded, decoded_message)

        # Next message with missing field 'data' -> 'set-request' ->
        # 'variable-bindings[0]' -> 'value' -> 'simple'.
        decoded_message = {
            'version': 1,
            'community': b'community',
            'data': {
                'set-request': {
                    'request-id': 1687059484,
                    'error-status': 0,
                    'error-index': 0,
                    'variable-bindings': [
                        {
                            'name': '1.3.6.1.999.1.1',
                            'value': {
                            }
                        }
                    ]
                }
            }
        }

        with self.assertRaises(asn1tools.EncodeError) as cm:
            rfc1157.encode('Message', decoded_message)

        self.assertEqual(
            str(cm.exception),
            "expected choices are ['simple', 'application-wide'], "
            "but got ''")

    def test_performance(self):
        cmplx = asn1tools.compile_files('tests/files/complex.asn')

        decoded_message = {
            'boolean': True,
            'integer': -7,
            'bit-string': (b'\x80', 3),
            'octet-string': b'\x31\x32',
            'null': None,
            'object-identifier': '1.3.2',
            'enumerated': 'one',
            'sequence': {},
            'ia5-string': 'foo'
        }

        encoded_message = (
            b'\x30\x1e\x01\x01\xff\x02\x01\xf9\x03\x02\x05\x80\x04\x02\x31\x32'
            b'\x05\x00\x06\x02\x2b\x02\x0a\x01\x01\x30\x00\x16\x03\x66\x6f\x6f'
        )

        def encode():
            cmplx.encode('AllUniversalTypes', decoded_message)

        def decode():
            cmplx.decode('AllUniversalTypes', encoded_message)

        iterations = 1000

        res = timeit.timeit(encode, number=iterations)
        ms_per_call = 1000 * res / iterations
        print('{} ms per encode call.'.format(round(ms_per_call, 3)))

        res = timeit.timeit(decode, number=iterations)
        ms_per_call = 1000 * res / iterations
        print('{} ms per decode call.'.format(round(ms_per_call, 3)))

    def test_rfc4511(self):
        rfc4511 = asn1tools.compile_dict(deepcopy(RFC4511))

        # A search request message.
        decoded_message = {
            'messageID': 2,
            'protocolOp': {
                'searchRequest': {
                    'baseObject': b'',
                    'scope': 'wholeSubtree',
                    'derefAliases': 'neverDerefAliases',
                    'sizeLimit': 0,
                    'timeLimit': 0,
                    'typesOnly': False,
                    'filter': {
                        'and': [
                            {
                                'substrings': {
                                    'type': b'\x63\x6e',
                                    'substrings': {
                                        'any': b'\x66\x72\x65\x64'
                                    }
                                }
                            },
                            {
                                'equalityMatch': {
                                    'attributeDesc': b'\x64\x6e',
                                    'assertionValue': b'\x6a\x6f\x65'
                                }
                            }
                        ]
                    },
                    'attributes': {
                    }
                }
            }
        }

        encoded_message = (
            b'\x30\x33\x02\x01\x02\x63\x2e\x04\x00\x0a\x01\x02\x0a\x01\x00\x02'
            b'\x01\x00\x02\x01\x00\x01\x01\x00\xa0\x19\xa4\x0c\x04\x02\x63\x6e'
            b'\x30\x06\x81\x04\x66\x72\x65\x64\xa3\x09\x04\x02\x64\x6e\x04\x03'
            b'\x6a\x6f\x65\x30\x00'
        )

        with self.assertRaises(NotImplementedError) as cm:
            decoded = rfc4511.decode('LDAPMessage', encoded_message)
            self.assertEqual(decoded, decoded_message)
            encoded = rfc4511.encode('LDAPMessage', decoded_message)
            self.assertEqual(encoded, encoded_message)

        self.assertEqual(str(cm.exception),
                         "Recursive types are not yet implemented (type 'Filter').")

        # A search result done message.
        decoded_message = {
            'messageID': 2,
            'protocolOp': {
                'searchResDone': {
                    'resultCode': 'noSuchObject',
                    'matchedDN': b'',
                    'diagnosticMessage': b''
                }
            }
        }

        encoded_message = (
            b'\x30\x0c\x02\x01\x02\x65\x07\x0a\x01\x20\x04\x00\x04\x00'
        )

        decoded = rfc4511.decode('LDAPMessage', encoded_message)
        self.assertEqual(decoded, decoded_message)
        encoded = rfc4511.encode('LDAPMessage', decoded_message)
        self.assertEqual(encoded, encoded_message)

        # A bind request message.
        decoded_message = {
            'messageID': 1,
            'protocolOp': {
                'bindRequest': {
                    'version': 3,
                    'name': b'uid=tesla,dc=example,dc=com',
                    'authentication': {
                        'simple': b'password'
                    }
                }
            }
        }

        encoded_message = (
            b'\x30\x2f\x02\x01\x01\x60\x2a\x02\x01\x03\x04\x1b\x75\x69\x64\x3d'
            b'\x74\x65\x73\x6c\x61\x2c\x64\x63\x3d\x65\x78\x61\x6d\x70\x6c\x65'
            b'\x2c\x64\x63\x3d\x63\x6f\x6d\x80\x08\x70\x61\x73\x73\x77\x6f\x72'
            b'\x64'
        )

        decoded = rfc4511.decode('LDAPMessage', encoded_message)
        self.assertEqual(decoded, decoded_message)
        encoded = rfc4511.encode('LDAPMessage', decoded_message)
        self.assertEqual(encoded, encoded_message)

        # A bind response message.
        decoded_message = {
            'messageID': 1,
            'protocolOp': {
                'bindResponse': {
                    'resultCode': 'success',
                    'matchedDN': b'',
                    'diagnosticMessage': b''
                }
            }
        }

        encoded_message = (
            b'\x30\x0c\x02\x01\x01\x61\x07\x0a\x01\x00\x04\x00\x04\x00'
        )

        decoded = rfc4511.decode('LDAPMessage', encoded_message)
        self.assertEqual(decoded, decoded_message)
        encoded = rfc4511.encode('LDAPMessage', decoded_message)
        self.assertEqual(encoded, encoded_message)

    def test_rfc5280(self):
        rfc5280 = asn1tools.compile_dict(deepcopy(RFC5280))

        decoded_message = {
            'tbsCertificate': {
                'version': 'v1',
                'serialNumber': 3578,
                'signature': {
                    'algorithm': '1.2.840.113549.1.1.5',
                    'parameters': b'\x05\x00'
                },
                'issuer': {
                    'rdnSequence': [
                        [{'type': '2.5.4.6',
                          'value': b'\x13\x02\x4a\x50'}],
                        [{'type': '2.5.4.8',
                          'value': b'\x13\x05\x54\x6f\x6b\x79\x6f'}],
                        [{'type': '2.5.4.7',
                          'value': b'\x13\x07\x43\x68\x75\x6f\x2d\x6b\x75'}],
                        [{'type': '2.5.4.10',
                          'value': b'\x13\x08\x46\x72\x61\x6e\x6b\x34\x44\x44'}],
                        [{'type': '2.5.4.11',
                          'value': (b'\x13\x0f\x57\x65\x62\x43\x65\x72\x74\x20\x53'
                                    b'\x75\x70\x70\x6f\x72\x74')}],
                        [{'type': '2.5.4.3',
                          'value': (b'\x13\x0f\x46\x72\x61\x6e\x6b\x34\x44\x44\x20'
                                    b'\x57\x65\x62\x20\x43\x41')}],
                        [{'type': '1.2.840.113549.1.9.1',
                          'value': (b'\x16\x14\x73\x75\x70\x70\x6f\x72\x74\x40\x66'
                                    b'\x72\x61\x6e\x6b\x34\x64\x64\x2e\x63\x6f\x6d')}]
                    ]
                },
                'validity': {
                    'notAfter': {'utcTime': '170821052654'},
                    'notBefore': {'utcTime': '120822052654'}
                },
                'subject': {
                    'rdnSequence': [
                        [{'type': '2.5.4.6',
                          'value': b'\x13\x02\x4a\x50'}],
                        [{'type': '2.5.4.8',
                          'value': b'\x0c\x05\x54\x6f\x6b\x79\x6f'}],
                        [{'type': '2.5.4.10',
                          'value': b'\x0c\x08\x46\x72\x61\x6e\x6b\x34\x44\x44'}],
                        [{'type': '2.5.4.3',
                          'value': (b'\x0c\x0f\x77\x77\x77\x2e\x65\x78\x61\x6d\x70'
                                    b'\x6c\x65\x2e\x63\x6f\x6d')}]
                    ]
                },
                'subjectPublicKeyInfo': {
                    'algorithm': {
                        'algorithm': '1.2.840.113549.1.1.1',
                        'parameters': b'\x05\x00'
                    },
                    'subjectPublicKey': (b'0H\x02A\x00\x9b\xfcf\x90y\x84B\xbb'
                                         b'\xab\x13\xfd+{\xf8\xde\x15\x12\xe5'
                                         b'\xf1\x93\xe3\x06\x8a{\xb8\xb1\xe1'
                                         b'\x9e&\xbb\x95\x01\xbf\xe70\xedd\x85'
                                         b'\x02\xdd\x15i\xa84\xb0\x06\xec?5<'
                                         b'\x1e\x1b+\x8f\xfa\x8f\x00\x1b\xdf'
                                         b'\x07\xc6\xacS\x07\x02\x03\x01\x00'
                                         b'\x01',
                                         592)
                }
            },
            'signatureAlgorithm': {
                'algorithm': '1.2.840.113549.1.1.5',
                'parameters': b'\x05\x00'
            },
            'signature': (b'\x14\xb6L\xbb\x81y3\xe6q\xa4\xdaQo\xcb\x08\x1d'
                          b'\x8d`\xec\xbc\x18\xc7sGY\xb1\xf2 H\xbba\xfa'
                          b'\xfcM\xad\x89\x8d\xd1!\xeb\xd5\xd8\xe5\xba'
                          b'\xd6\xa66\xfdtP\x83\xb6\x0f\xc7\x1d\xdf}\xe5.\x81'
                          b'\x7fE\xe0\x9f\xe2>y\xee\xd701\xc7 r\xd9X.*\xfe\x12'
                          b'Z4E\xa1\x19\x08|\x89G_J\x95\xbe#!JSr\xda*\x05/.\xc9'
                          b'p\xf6[\xfa\xfd\xdf\xb41\xb2\xc1J\x9c\x06%C\xa1'
                          b'\xe6\xb4\x1e\x7f\x86\x9b\x16@',
                          1024)
        }

        encoded_message = (
            b'\x30\x82\x02\x12\x30\x82\x01\x7b\x02\x02\x0d\xfa\x30\x0d\x06\x09'
            b'\x2a\x86\x48\x86\xf7\x0d\x01\x01\x05\x05\x00\x30\x81\x9b\x31\x0b'
            b'\x30\x09\x06\x03\x55\x04\x06\x13\x02\x4a\x50\x31\x0e\x30\x0c\x06'
            b'\x03\x55\x04\x08\x13\x05\x54\x6f\x6b\x79\x6f\x31\x10\x30\x0e\x06'
            b'\x03\x55\x04\x07\x13\x07\x43\x68\x75\x6f\x2d\x6b\x75\x31\x11\x30'
            b'\x0f\x06\x03\x55\x04\x0a\x13\x08\x46\x72\x61\x6e\x6b\x34\x44\x44'
            b'\x31\x18\x30\x16\x06\x03\x55\x04\x0b\x13\x0f\x57\x65\x62\x43\x65'
            b'\x72\x74\x20\x53\x75\x70\x70\x6f\x72\x74\x31\x18\x30\x16\x06\x03'
            b'\x55\x04\x03\x13\x0f\x46\x72\x61\x6e\x6b\x34\x44\x44\x20\x57\x65'
            b'\x62\x20\x43\x41\x31\x23\x30\x21\x06\x09\x2a\x86\x48\x86\xf7\x0d'
            b'\x01\x09\x01\x16\x14\x73\x75\x70\x70\x6f\x72\x74\x40\x66\x72\x61'
            b'\x6e\x6b\x34\x64\x64\x2e\x63\x6f\x6d\x30\x1e\x17\x0d\x31\x32\x30'
            b'\x38\x32\x32\x30\x35\x32\x36\x35\x34\x5a\x17\x0d\x31\x37\x30\x38'
            b'\x32\x31\x30\x35\x32\x36\x35\x34\x5a\x30\x4a\x31\x0b\x30\x09\x06'
            b'\x03\x55\x04\x06\x13\x02\x4a\x50\x31\x0e\x30\x0c\x06\x03\x55\x04'
            b'\x08\x0c\x05\x54\x6f\x6b\x79\x6f\x31\x11\x30\x0f\x06\x03\x55\x04'
            b'\x0a\x0c\x08\x46\x72\x61\x6e\x6b\x34\x44\x44\x31\x18\x30\x16\x06'
            b'\x03\x55\x04\x03\x0c\x0f\x77\x77\x77\x2e\x65\x78\x61\x6d\x70\x6c'
            b'\x65\x2e\x63\x6f\x6d\x30\x5c\x30\x0d\x06\x09\x2a\x86\x48\x86\xf7'
            b'\x0d\x01\x01\x01\x05\x00\x03\x4b\x00\x30\x48\x02\x41\x00\x9b\xfc'
            b'\x66\x90\x79\x84\x42\xbb\xab\x13\xfd\x2b\x7b\xf8\xde\x15\x12\xe5'
            b'\xf1\x93\xe3\x06\x8a\x7b\xb8\xb1\xe1\x9e\x26\xbb\x95\x01\xbf\xe7'
            b'\x30\xed\x64\x85\x02\xdd\x15\x69\xa8\x34\xb0\x06\xec\x3f\x35\x3c'
            b'\x1e\x1b\x2b\x8f\xfa\x8f\x00\x1b\xdf\x07\xc6\xac\x53\x07\x02\x03'
            b'\x01\x00\x01\x30\x0d\x06\x09\x2a\x86\x48\x86\xf7\x0d\x01\x01\x05'
            b'\x05\x00\x03\x81\x81\x00\x14\xb6\x4c\xbb\x81\x79\x33\xe6\x71\xa4'
            b'\xda\x51\x6f\xcb\x08\x1d\x8d\x60\xec\xbc\x18\xc7\x73\x47\x59\xb1'
            b'\xf2\x20\x48\xbb\x61\xfa\xfc\x4d\xad\x89\x8d\xd1\x21\xeb\xd5\xd8'
            b'\xe5\xba\xd6\xa6\x36\xfd\x74\x50\x83\xb6\x0f\xc7\x1d\xdf\x7d\xe5'
            b'\x2e\x81\x7f\x45\xe0\x9f\xe2\x3e\x79\xee\xd7\x30\x31\xc7\x20\x72'
            b'\xd9\x58\x2e\x2a\xfe\x12\x5a\x34\x45\xa1\x19\x08\x7c\x89\x47\x5f'
            b'\x4a\x95\xbe\x23\x21\x4a\x53\x72\xda\x2a\x05\x2f\x2e\xc9\x70\xf6'
            b'\x5b\xfa\xfd\xdf\xb4\x31\xb2\xc1\x4a\x9c\x06\x25\x43\xa1\xe6\xb4'
            b'\x1e\x7f\x86\x9b\x16\x40'
        )

        decoded = rfc5280.decode('Certificate', encoded_message)
        self.assertEqual(decoded, decoded_message)
        encoded = rfc5280.encode('Certificate', decoded_message)
        self.assertEqual(encoded, encoded_message)

    def test_rfc5280_modified(self):
        any_defined_by_choices = {
            ('PKIX1Explicit88', 'AlgorithmIdentifier', 'parameters'): {
                '1.2.840.113549.1.1.1': 'NULL',
                '1.2.840.113549.1.1.5': 'NULL'
            },
            ('PKIX1Explicit88', 'AttributeValue'): {
                '2.5.4.3': 'DirectoryString',
                '2.5.4.6': 'PrintableString',
                '2.5.4.7': 'PrintableString',
                '2.5.4.8': 'DirectoryString',
                '2.5.4.10': 'DirectoryString',
                '2.5.4.11': 'PrintableString',
                '1.2.840.113549.1.9.1': 'IA5String'
            }
        }

        rfc5280 = asn1tools.compile_dict(
            deepcopy(RFC5280_MODIFIED),
            any_defined_by_choices=any_defined_by_choices)

        decoded_message = {
            'tbsCertificate': {
                'version': 'v1',
                'serialNumber': 3578,
                'signature': {
                    'algorithm': '1.2.840.113549.1.1.5',
                    'parameters': None
                },
                'issuer': {
                    'rdnSequence': [
                        [{'type': '2.5.4.6', 'value': 'JP'}],
                        [{'type': '2.5.4.8',
                          'value': {'printableString': 'Tokyo'}}],
                        [{'type': '2.5.4.7', 'value': 'Chuo-ku'}],
                        [{'type': '2.5.4.10',
                          'value': {'printableString': 'Frank4DD'}}],
                        [{'type': '2.5.4.11', 'value': 'WebCert Support'}],
                        [{'type': '2.5.4.3',
                          'value': {'printableString': 'Frank4DD Web CA'}}],
                        [{'type': '1.2.840.113549.1.9.1',
                          'value': 'support@frank4dd.com'}]
                    ]
                },
                'validity': {
                    'notAfter': {'utcTime': '170821052654'},
                    'notBefore': {'utcTime': '120822052654'}
                },
                'subject': {
                    'rdnSequence': [
                        [{'type': '2.5.4.6', 'value': 'JP'}],
                        [{'type': '2.5.4.8', 'value': {'utf8String': 'Tokyo'}}],
                        [{'type': '2.5.4.10',
                          'value': {'utf8String': 'Frank4DD'}}],
                        [{'type': '2.5.4.3',
                          'value': {'utf8String': 'www.example.com'}}]
                    ]
                },
                'subjectPublicKeyInfo': {
                    'algorithm': {
                        'algorithm': '1.2.840.113549.1.1.1',
                        'parameters': None
                    },
                    'subjectPublicKey': (b'0H\x02A\x00\x9b\xfcf\x90y\x84B\xbb'
                                         b'\xab\x13\xfd+{\xf8\xde\x15\x12\xe5'
                                         b'\xf1\x93\xe3\x06\x8a{\xb8\xb1\xe1'
                                         b'\x9e&\xbb\x95\x01\xbf\xe70\xedd\x85'
                                         b'\x02\xdd\x15i\xa84\xb0\x06\xec?5<'
                                         b'\x1e\x1b+\x8f\xfa\x8f\x00\x1b\xdf'
                                         b'\x07\xc6\xacS\x07\x02\x03\x01\x00'
                                         b'\x01',
                                         592)
                }
            },
            'signatureAlgorithm': {
                'algorithm': '1.2.840.113549.1.1.5',
                'parameters': None
            },
            'signature': (b'\x14\xb6L\xbb\x81y3\xe6q\xa4\xdaQo\xcb\x08\x1d'
                          b'\x8d`\xec\xbc\x18\xc7sGY\xb1\xf2 H\xbba\xfa'
                          b'\xfcM\xad\x89\x8d\xd1!\xeb\xd5\xd8\xe5\xba'
                          b'\xd6\xa66\xfdtP\x83\xb6\x0f\xc7\x1d\xdf}\xe5.\x81'
                          b'\x7fE\xe0\x9f\xe2>y\xee\xd701\xc7 r\xd9X.*\xfe\x12'
                          b'Z4E\xa1\x19\x08|\x89G_J\x95\xbe#!JSr\xda*\x05/.\xc9'
                          b'p\xf6[\xfa\xfd\xdf\xb41\xb2\xc1J\x9c\x06%C\xa1'
                          b'\xe6\xb4\x1e\x7f\x86\x9b\x16@',
                          1024)
        }

        encoded_message = (
            b'\x30\x82\x02\x12\x30\x82\x01\x7b\x02\x02\x0d\xfa\x30\x0d\x06\x09'
            b'\x2a\x86\x48\x86\xf7\x0d\x01\x01\x05\x05\x00\x30\x81\x9b\x31\x0b'
            b'\x30\x09\x06\x03\x55\x04\x06\x13\x02\x4a\x50\x31\x0e\x30\x0c\x06'
            b'\x03\x55\x04\x08\x13\x05\x54\x6f\x6b\x79\x6f\x31\x10\x30\x0e\x06'
            b'\x03\x55\x04\x07\x13\x07\x43\x68\x75\x6f\x2d\x6b\x75\x31\x11\x30'
            b'\x0f\x06\x03\x55\x04\x0a\x13\x08\x46\x72\x61\x6e\x6b\x34\x44\x44'
            b'\x31\x18\x30\x16\x06\x03\x55\x04\x0b\x13\x0f\x57\x65\x62\x43\x65'
            b'\x72\x74\x20\x53\x75\x70\x70\x6f\x72\x74\x31\x18\x30\x16\x06\x03'
            b'\x55\x04\x03\x13\x0f\x46\x72\x61\x6e\x6b\x34\x44\x44\x20\x57\x65'
            b'\x62\x20\x43\x41\x31\x23\x30\x21\x06\x09\x2a\x86\x48\x86\xf7\x0d'
            b'\x01\x09\x01\x16\x14\x73\x75\x70\x70\x6f\x72\x74\x40\x66\x72\x61'
            b'\x6e\x6b\x34\x64\x64\x2e\x63\x6f\x6d\x30\x1e\x17\x0d\x31\x32\x30'
            b'\x38\x32\x32\x30\x35\x32\x36\x35\x34\x5a\x17\x0d\x31\x37\x30\x38'
            b'\x32\x31\x30\x35\x32\x36\x35\x34\x5a\x30\x4a\x31\x0b\x30\x09\x06'
            b'\x03\x55\x04\x06\x13\x02\x4a\x50\x31\x0e\x30\x0c\x06\x03\x55\x04'
            b'\x08\x0c\x05\x54\x6f\x6b\x79\x6f\x31\x11\x30\x0f\x06\x03\x55\x04'
            b'\x0a\x0c\x08\x46\x72\x61\x6e\x6b\x34\x44\x44\x31\x18\x30\x16\x06'
            b'\x03\x55\x04\x03\x0c\x0f\x77\x77\x77\x2e\x65\x78\x61\x6d\x70\x6c'
            b'\x65\x2e\x63\x6f\x6d\x30\x5c\x30\x0d\x06\x09\x2a\x86\x48\x86\xf7'
            b'\x0d\x01\x01\x01\x05\x00\x03\x4b\x00\x30\x48\x02\x41\x00\x9b\xfc'
            b'\x66\x90\x79\x84\x42\xbb\xab\x13\xfd\x2b\x7b\xf8\xde\x15\x12\xe5'
            b'\xf1\x93\xe3\x06\x8a\x7b\xb8\xb1\xe1\x9e\x26\xbb\x95\x01\xbf\xe7'
            b'\x30\xed\x64\x85\x02\xdd\x15\x69\xa8\x34\xb0\x06\xec\x3f\x35\x3c'
            b'\x1e\x1b\x2b\x8f\xfa\x8f\x00\x1b\xdf\x07\xc6\xac\x53\x07\x02\x03'
            b'\x01\x00\x01\x30\x0d\x06\x09\x2a\x86\x48\x86\xf7\x0d\x01\x01\x05'
            b'\x05\x00\x03\x81\x81\x00\x14\xb6\x4c\xbb\x81\x79\x33\xe6\x71\xa4'
            b'\xda\x51\x6f\xcb\x08\x1d\x8d\x60\xec\xbc\x18\xc7\x73\x47\x59\xb1'
            b'\xf2\x20\x48\xbb\x61\xfa\xfc\x4d\xad\x89\x8d\xd1\x21\xeb\xd5\xd8'
            b'\xe5\xba\xd6\xa6\x36\xfd\x74\x50\x83\xb6\x0f\xc7\x1d\xdf\x7d\xe5'
            b'\x2e\x81\x7f\x45\xe0\x9f\xe2\x3e\x79\xee\xd7\x30\x31\xc7\x20\x72'
            b'\xd9\x58\x2e\x2a\xfe\x12\x5a\x34\x45\xa1\x19\x08\x7c\x89\x47\x5f'
            b'\x4a\x95\xbe\x23\x21\x4a\x53\x72\xda\x2a\x05\x2f\x2e\xc9\x70\xf6'
            b'\x5b\xfa\xfd\xdf\xb4\x31\xb2\xc1\x4a\x9c\x06\x25\x43\xa1\xe6\xb4'
            b'\x1e\x7f\x86\x9b\x16\x40'
        )

        decoded = rfc5280.decode('Certificate', encoded_message)
        self.assertEqual(decoded, decoded_message)
        # Do not include the version member, which have a default
        # value (is this correct?).
        del decoded_message['tbsCertificate']['version']
        encoded = rfc5280.encode('Certificate', decoded_message)
        self.assertEqual(encoded, encoded_message)

        # Explicit tagging.
        decoded_message = {
            'psap-address': {
                'pSelector': b'\x12',
                'nAddresses': [ b'\x34' ]
            }
        }

        encoded_message = b'\xa0\x0c\xa0\x03\x04\x01\x12\xa3\x05\x31\x03\x04\x01\x34'

        encoded = rfc5280.encode('ExtendedNetworkAddress', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = rfc5280.decode('ExtendedNetworkAddress', encoded)
        self.assertEqual(decoded, decoded_message)

    def test_rfc5280_errors(self):
        rfc5280 = asn1tools.compile_dict(deepcopy(RFC5280))

        # Empty data.
        encoded_message = b''

        with self.assertRaises(asn1tools.DecodeError) as cm:
            rfc5280.decode('Certificate', encoded_message)

        self.assertEqual(str(cm.exception),
                         ': expected SEQUENCE with tag 0x30 but got 0x at offset 0')

        # Only tag and length, no contents.
        encoded_message = b'\x30\x81\x9f'

        with self.assertRaises(asn1tools.DecodeError) as cm:
            rfc5280.decode('Certificate', encoded_message)

        self.assertEqual(str(cm.exception),
                         'tbsCertificate: expected SEQUENCE with tag 0x30 but got '
                         '0x at offset 3')

        # Unexpected tag 0xff.
        encoded_message = b'\xff\x01\x00'

        with self.assertRaises(asn1tools.DecodeError) as cm:
            rfc5280.decode('Certificate', encoded_message)

        self.assertEqual(str(cm.exception),
                         ': expected SEQUENCE with tag 0x30 but got 0xff at '
                         'offset 0')

        # Unexpected type 0x31 embedded in the data.
        encoded_message = bytearray(
            b'\x30\x82\x02\x12\x30\x82\x01\x7b\x02\x02\x0d\xfa\x30\x0d\x06\x09'
            b'\x2a\x86\x48\x86\xf7\x0d\x01\x01\x05\x05\x00\x30\x81\x9b\x31\x0b'
            b'\x30\x09\x06\x03\x55\x04\x06\x13\x02\x4a\x50\x31\x0e\x30\x0c\x06'
            b'\x03\x55\x04\x08\x13\x05\x54\x6f\x6b\x79\x6f\x31\x10\x30\x0e\x06'
            b'\x03\x55\x04\x07\x13\x07\x43\x68\x75\x6f\x2d\x6b\x75\x31\x11\x30'
            b'\x0f\x06\x03\x55\x04\x0a\x13\x08\x46\x72\x61\x6e\x6b\x34\x44\x44'
            b'\x31\x18\x30\x16\x06\x03\x55\x04\x0b\x13\x0f\x57\x65\x62\x43\x65'
            b'\x72\x74\x20\x53\x75\x70\x70\x6f\x72\x74\x31\x18\x30\x16\x06\x03'
            b'\x55\x04\x03\x13\x0f\x46\x72\x61\x6e\x6b\x34\x44\x44\x20\x57\x65'
            b'\x62\x20\x43\x41\x31\x23'
            b'\x31'
            b'\x21\x06\x09\x2a\x86\x48\x86\xf7\x0d'
            b'\x01\x09\x01\x16\x14\x73\x75\x70\x70\x6f\x72\x74\x40\x66\x72\x61'
            b'\x6e\x6b\x34\x64\x64\x2e\x63\x6f\x6d\x30\x1e\x17\x0d\x31\x32\x30'
            b'\x38\x32\x32\x30\x35\x32\x36\x35\x34\x5a\x17\x0d\x31\x37\x30\x38'
            b'\x32\x31\x30\x35\x32\x36\x35\x34\x5a\x30\x4a\x31\x0b\x30\x09\x06'
            b'\x03\x55\x04\x06\x13\x02\x4a\x50\x31\x0e\x30\x0c\x06\x03\x55\x04'
            b'\x08\x0c\x05\x54\x6f\x6b\x79\x6f\x31\x11\x30\x0f\x06\x03\x55\x04'
            b'\x0a\x0c\x08\x46\x72\x61\x6e\x6b\x34\x44\x44\x31\x18\x30\x16\x06'
            b'\x03\x55\x04\x03\x0c\x0f\x77\x77\x77\x2e\x65\x78\x61\x6d\x70\x6c'
            b'\x65\x2e\x63\x6f\x6d\x30\x5c\x30\x0d\x06\x09\x2a\x86\x48\x86\xf7'
            b'\x0d\x01\x01\x01\x05\x00\x03\x4b\x00\x30\x48\x02\x41\x00\x9b\xfc'
            b'\x66\x90\x79\x84\x42\xbb\xab\x13\xfd\x2b\x7b\xf8\xde\x15\x12\xe5'
            b'\xf1\x93\xe3\x06\x8a\x7b\xb8\xb1\xe1\x9e\x26\xbb\x95\x01\xbf\xe7'
            b'\x30\xed\x64\x85\x02\xdd\x15\x69\xa8\x34\xb0\x06\xec\x3f\x35\x3c'
            b'\x1e\x1b\x2b\x8f\xfa\x8f\x00\x1b\xdf\x07\xc6\xac\x53\x07\x02\x03'
            b'\x01\x00\x01\x30\x0d\x06\x09\x2a\x86\x48\x86\xf7\x0d\x01\x01\x05'
            b'\x05\x00\x03\x81\x81\x00\x14\xb6\x4c\xbb\x81\x79\x33\xe6\x71\xa4'
            b'\xda\x51\x6f\xcb\x08\x1d\x8d\x60\xec\xbc\x18\xc7\x73\x47\x59\xb1'
            b'\xf2\x20\x48\xbb\x61\xfa\xfc\x4d\xad\x89\x8d\xd1\x21\xeb\xd5\xd8'
            b'\xe5\xba\xd6\xa6\x36\xfd\x74\x50\x83\xb6\x0f\xc7\x1d\xdf\x7d\xe5'
            b'\x2e\x81\x7f\x45\xe0\x9f\xe2\x3e\x79\xee\xd7\x30\x31\xc7\x20\x72'
            b'\xd9\x58\x2e\x2a\xfe\x12\x5a\x34\x45\xa1\x19\x08\x7c\x89\x47\x5f'
            b'\x4a\x95\xbe\x23\x21\x4a\x53\x72\xda\x2a\x05\x2f\x2e\xc9\x70\xf6'
            b'\x5b\xfa\xfd\xdf\xb4\x31\xb2\xc1\x4a\x9c\x06\x25\x43\xa1\xe6\xb4'
            b'\x1e\x7f\x86\x9b\x16\x40'
        )

        self.assertEqual(encoded_message[150], 49)

        with self.assertRaises(asn1tools.DecodeError) as cm:
            rfc5280.decode('Certificate', encoded_message)

        self.assertEqual(str(cm.exception),
                         'tbsCertificate: issuer: expected SEQUENCE with tag '
                         '0x30 but got 0x31 at offset 150')

    def test_all_types(self):
        all_types = asn1tools.compile_files('tests/files/all_types.asn')

        datas = [
            ('Boolean',                 True, b'\x01\x01\xff'),
            ('Boolean',                False, b'\x01\x01\x00'),
            ('Integer',                32768, b'\x02\x03\x00\x80\x00'),
            ('Integer',                32767, b'\x02\x02\x7f\xff'),
            ('Integer',                  256, b'\x02\x02\x01\x00'),
            ('Integer',                  255, b'\x02\x02\x00\xff'),
            ('Integer',                  128, b'\x02\x02\x00\x80'),
            ('Integer',                  127, b'\x02\x01\x7f'),
            ('Integer',                    1, b'\x02\x01\x01'),
            ('Integer',                    0, b'\x02\x01\x00'),
            ('Integer',                   -1, b'\x02\x01\xff'),
            ('Integer',                 -128, b'\x02\x01\x80'),
            ('Integer',                 -129, b'\x02\x02\xff\x7f'),
            ('Integer',                 -256, b'\x02\x02\xff\x00'),
            ('Integer',               -32768, b'\x02\x02\x80\x00'),
            ('Integer',               -32769, b'\x02\x03\xff\x7f\xff'),
            ('Bitstring',       (b'\x80', 1), b'\x03\x02\x07\x80'),
            ('Octetstring',          b'\x00', b'\x04\x01\x00'),
            ('Octetstring',    127 * b'\x55', b'\x04\x7f' + 127 * b'\x55'),
            ('Octetstring',    128 * b'\xaa', b'\x04\x81\x80' + 128 * b'\xaa'),
            ('Null',                    None, b'\x05\x00'),
            ('Objectidentifier',       '1.2', b'\x06\x01\x2a'),
            ('Enumerated',             'one', b'\x0a\x01\x01'),
            ('Utf8string',             'foo', b'\x0c\x03foo'),
            ('Sequence',                  {}, b'\x30\x00'),
            ('Sequence2',           {'a': 0}, b'\x30\x00'),
            ('Sequence2',           {'a': 1}, b'\x30\x03\x02\x01\x01'),
            ('Set',                       {}, b'\x31\x00'),
            ('Set2',                {'a': 1}, b'\x31\x00'),
            ('Set2',                {'a': 2}, b'\x31\x03\x02\x01\x02'),
            ('Numericstring',          '123', b'\x12\x03123'),
            ('Printablestring',        'foo', b'\x13\x03foo'),
            ('Ia5string',              'bar', b'\x16\x03bar'),
            ('Universalstring',        'bar', b'\x1c\x03bar'),
            ('Visiblestring',          'bar', b'\x1a\x03bar'),
            ('Bmpstring',             b'bar', b'\x1e\x03bar'),
            ('Teletexstring',         b'fum', b'\x14\x03fum'),
            ('Utctime',       '010203040506', b'\x17\x0d010203040506Z'),
            ('GeneralizedTime1',
             '20001231235959.999',
             b'\x18\x12\x32\x30\x30\x30\x31\x32\x33\x31\x32\x33\x35\x39'
             b'\x35\x39\x2e\x39\x39\x39'),
            ('SequenceOf',                [], b'0\x00'),
            ('SetOf',                     [], b'1\x00')
        ]

        for type_name, decoded, encoded in datas:
            self.assertEqual(all_types.encode(type_name, decoded), encoded)
            self.assertEqual(all_types.decode(type_name, encoded), decoded)

        with self.assertRaises(NotImplementedError):
            all_types.encode('Sequence12', {'a': [{'a': []}]})

        with self.assertRaises(NotImplementedError):
            all_types.decode('Sequence12', b'\x30\x04\xa0\x02\x30\x00')

    def test_all_types_automatic_tags(self):
        all_types = asn1tools.compile_files(
            'tests/files/all_types_automatic_tags.asn')

        datas = [
            ('Sequence14',
             {'a': 1, 'c': 2,'d': True},
             b'\x30\x09\x80\x01\x01\x82\x01\x02\x83\x01\xff')
        ]

        for type_name, decoded, encoded in datas:
            self.assertEqual(all_types.encode(type_name, decoded), encoded)
            self.assertEqual(all_types.decode(type_name, encoded), decoded)

    def test_decode_all_types_errors(self):
        all_types = asn1tools.compile_files('tests/files/all_types.asn')

        # BOOLEAN.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Boolean', b'\xff')

        self.assertEqual(str(cm.exception),
                         ': expected BOOLEAN with tag 0x01 but got 0xff at offset 0')

        # INTEGER.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Integer', b'\xfe')

        self.assertEqual(str(cm.exception),
                         ': expected INTEGER with tag 0x02 but got 0xfe at offset 0')

        # BIT STRING.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Bitstring', b'\xfd')

        self.assertEqual(str(cm.exception),
                         ': expected BIT STRING with tag 0x03 but got 0xfd at offset 0')

        # OCTET STRING.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Octetstring', b'\xfc')

        self.assertEqual(str(cm.exception),
                         ': expected OCTET STRING with tag 0x04 but got 0xfc at offset 0')

        # NULL.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Null', b'\xfb')

        self.assertEqual(str(cm.exception),
                         ': expected NULL with tag 0x05 but got 0xfb at offset 0')

        # OBJECT IDENTIFIER.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Objectidentifier', b'\xfa')

        self.assertEqual(str(cm.exception),
                         ': expected OBJECT IDENTIFIER with tag 0x06 but got '
                         '0xfa at offset 0')

        # ENUMERATED.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Enumerated', b'\xf9')

        self.assertEqual(str(cm.exception),
                         ': expected ENUMERATED with tag 0x0a but got 0xf9 at offset 0')

        # UTF8String.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Utf8string', b'\xf8')

        self.assertEqual(str(cm.exception),
                         ': expected UTF8String with tag 0x0c but got 0xf8 at offset 0')

        # SEQUENCE.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Sequence', b'\xf7')

        self.assertEqual(str(cm.exception),
                         ': expected SEQUENCE with tag 0x30 but got 0xf7 at offset 0')

        # SET.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Set', b'\xf6')

        self.assertEqual(str(cm.exception),
                         ': expected SET with tag 0x31 but got 0xf6 at offset 0')

        # NumericString.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Numericstring', b'\xf5')

        self.assertEqual(str(cm.exception),
                         ': expected NumericString with tag 0x12 but got '
                         '0xf5 at offset 0')

        # PrintableString.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Printablestring', b'\xf4')

        self.assertEqual(str(cm.exception),
                         ': expected PrintableString with tag 0x13 but got '
                         '0xf4 at offset 0')

        # IA5String.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Ia5string', b'\xf3')

        self.assertEqual(str(cm.exception),
                         ': expected IA5String with tag 0x16 but got '
                         '0xf3 at offset 0')

        # UniversalString.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Universalstring', b'\xf2')

        self.assertEqual(str(cm.exception),
                         ': expected UniversalString with tag 0x1c but got '
                         '0xf2 at offset 0')

        # VisibleString.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Visiblestring', b'\xf1')

        self.assertEqual(str(cm.exception),
                         ': expected VisibleString with tag 0x1a but got '
                         '0xf1 at offset 0')

        # BMPString.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Bmpstring', b'\xf0')

        self.assertEqual(str(cm.exception),
                         ': expected BMPString with tag 0x1e but got '
                         '0xf0 at offset 0')

        # TeletexString.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Teletexstring', b'\xef')

        self.assertEqual(str(cm.exception),
                         ': expected TeletexString with tag 0x14 but got '
                         '0xef at offset 0')

        # UTCTime.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Utctime', b'\xee')

        self.assertEqual(str(cm.exception),
                         ': expected UTCTime with tag 0x17 but got '
                         '0xee at offset 0')

        # SequenceOf.
        # ToDo: Should raise a decode error.
        with self.assertRaises(IndexError) as cm:
            all_types.decode('SequenceOf', b'\xed')

        self.assertEqual(str(cm.exception),
                         'bytearray index out of range')

        # SetOf.
        # ToDo: Should raise a decode error.
        with self.assertRaises(IndexError) as cm:
            all_types.decode('SetOf', b'\xec')

        self.assertEqual(str(cm.exception),
                         'bytearray index out of range')

    def test_repr_all_types(self):
        all_types = asn1tools.compile_files('tests/files/all_types.asn')

        self.assertEqual(repr(all_types.types['Boolean']), 'Boolean(Boolean)')
        self.assertEqual(repr(all_types.types['Integer']), 'Integer(Integer)')
        self.assertEqual(repr(all_types.types['Bitstring']), 'BitString(Bitstring)')
        self.assertEqual(repr(all_types.types['Octetstring']), 'OctetString(Octetstring)')
        self.assertEqual(repr(all_types.types['Null']), 'Null(Null)')
        self.assertEqual(repr(all_types.types['Objectidentifier']),
                         'ObjectIdentifier(Objectidentifier)')
        self.assertEqual(repr(all_types.types['Enumerated']), 'Enumerated(Enumerated)')
        self.assertEqual(repr(all_types.types['Utf8string']), 'UTF8String(Utf8string)')
        self.assertEqual(repr(all_types.types['Sequence']), 'Sequence(Sequence, [])')
        self.assertEqual(repr(all_types.types['Set']), 'Set(Set, [])')
        self.assertEqual(repr(all_types.types['Sequence2']),
                         'Sequence(Sequence2, [Integer(a)])')
        self.assertEqual(repr(all_types.types['Set2']), 'Set(Set2, [Integer(a)])')
        self.assertEqual(repr(all_types.types['Numericstring']),
                         'NumericString(Numericstring)')
        self.assertEqual(repr(all_types.types['Printablestring']),
                         'PrintableString(Printablestring)')
        self.assertEqual(repr(all_types.types['Ia5string']), 'IA5String(Ia5string)')
        self.assertEqual(repr(all_types.types['Universalstring']),
                         'UniversalString(Universalstring)')
        self.assertEqual(repr(all_types.types['Visiblestring']),
                         'VisibleString(Visiblestring)')
        self.assertEqual(repr(all_types.types['Bmpstring']),
                         'BMPString(Bmpstring)')
        self.assertEqual(repr(all_types.types['Teletexstring']),
                         'TeletexString(Teletexstring)')
        self.assertEqual(repr(all_types.types['Utctime']), 'UTCTime(Utctime)')
        self.assertEqual(repr(all_types.types['SequenceOf']),
                         'SequenceOf(SequenceOf, Integer())')
        self.assertEqual(repr(all_types.types['SetOf']), 'SetOf(SetOf, Integer())')

    def test_integer_explicit_tags(self):
        """Test explicit tags on integers.

        """

        spec = 'Foo DEFINITIONS ::= BEGIN Foo ::= [2] INTEGER END'
        foo = asn1tools.compile_string(spec)
        encoded = foo.encode('Foo', 1)
        self.assertEqual(encoded, b'\xa2\x03\x02\x01\x01')
        decoded = foo.decode('Foo', encoded)
        self.assertEqual(decoded, 1)

        spec = 'Foo DEFINITIONS ::= BEGIN Foo ::= [2] EXPLICIT INTEGER END'
        foo = asn1tools.compile_string(spec)
        encoded = foo.encode('Foo', 1)
        self.assertEqual(encoded, b'\xa2\x03\x02\x01\x01')
        decoded = foo.decode('Foo', encoded)
        self.assertEqual(decoded, 1)

        spec = 'Foo DEFINITIONS EXPLICIT TAGS ::= BEGIN Foo ::= INTEGER END'
        foo = asn1tools.compile_string(spec)
        encoded = foo.encode('Foo', 1)
        self.assertEqual(encoded, b'\x02\x01\x01')
        decoded = foo.decode('Foo', encoded)
        self.assertEqual(decoded, 1)

        spec = 'Foo DEFINITIONS ::= BEGIN Foo ::= [2] BOOLEAN END'
        foo = asn1tools.compile_string(spec)
        encoded = foo.encode('Foo', True)
        self.assertEqual(encoded, b'\xa2\x03\x01\x01\xff')
        decoded = foo.decode('Foo', encoded)
        self.assertEqual(decoded, True)

    def test_integer_implicit_tags(self):
        """Test implicit tags on integers.

        """

        spec = 'Foo DEFINITIONS ::= BEGIN Foo ::= [2] IMPLICIT INTEGER END'
        foo = asn1tools.compile_string(spec)
        encoded = foo.encode('Foo', 1)
        self.assertEqual(encoded, b'\x82\x01\x01')
        decoded = foo.decode('Foo', encoded)
        self.assertEqual(decoded, 1)

        spec = 'Foo DEFINITIONS IMPLICIT TAGS ::= BEGIN Foo ::= INTEGER END'
        foo = asn1tools.compile_string(spec)
        encoded = foo.encode('Foo', 1)
        self.assertEqual(encoded, b'\x02\x01\x01')
        decoded = foo.decode('Foo', encoded)
        self.assertEqual(decoded, 1)

        spec = ('Foo DEFINITIONS EXPLICIT TAGS ::= BEGIN '
                'Foo ::= [2] IMPLICIT INTEGER END')
        foo = asn1tools.compile_string(spec)
        encoded = foo.encode('Foo', 1)
        self.assertEqual(encoded, b'\x82\x01\x01')
        decoded = foo.decode('Foo', encoded)
        self.assertEqual(decoded, 1)

    def test_boolean_explicit_tags(self):
        """Test explicit tags on booleans.

        """

        spec = 'Foo DEFINITIONS ::= BEGIN Foo ::= [2] BOOLEAN END'
        foo = asn1tools.compile_string(spec)
        encoded = foo.encode('Foo', True)
        self.assertEqual(encoded, b'\xa2\x03\x01\x01\xff')
        decoded = foo.decode('Foo', encoded)
        self.assertEqual(decoded, True)

        # Bad explicit tag.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('Foo', b'\xa3\x03\x01\x01\x01')

        self.assertEqual(str(cm.exception),
                         ': expected Tag with tag 0xa2 but got 0xa3 at offset 0')

        # Bad tag.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('Foo', b'\xa2\x03\x02\x01\x01')

        self.assertEqual(str(cm.exception),
                         ': expected BOOLEAN with tag 0x01 but got 0x02 at offset 2')

    def test_boolean_implicit_tags(self):
        """Test implicit tags on booleans.

        """

        spec = 'Foo DEFINITIONS ::= BEGIN Foo ::= [2] IMPLICIT BOOLEAN END'
        foo = asn1tools.compile_string(spec)
        encoded = foo.encode('Foo', True)
        self.assertEqual(encoded, b'\x82\x01\xff')
        decoded = foo.decode('Foo', encoded)
        self.assertEqual(decoded, True)

    def test_octet_string_explicit_tags(self):
        """Test explicit tags on octet strings.

        """

        spec = 'Foo DEFINITIONS ::= BEGIN Foo ::= [2] OCTET STRING END'
        foo = asn1tools.compile_string(spec)
        encoded = foo.encode('Foo', b'\x56')
        self.assertEqual(encoded, b'\xa2\x03\x04\x01\x56')
        decoded = foo.decode('Foo', encoded)
        self.assertEqual(decoded, b'\x56')

    def test_bit_string_explicit_tags(self):
        """Test explicit tags on bit strings.

        """

        spec = 'Foo DEFINITIONS ::= BEGIN Foo ::= [2] BIT STRING END'
        foo = asn1tools.compile_string(spec)
        encoded = foo.encode('Foo', (b'\x56', 7))
        self.assertEqual(encoded, b'\xa2\x04\x03\x02\x01\x56')
        decoded = foo.decode('Foo', encoded)
        self.assertEqual(decoded, (b'\x56', 7))

    def test_utc_time_explicit_tags(self):
        """Test explicit tags on UTC time.

        """

        spec = 'Foo DEFINITIONS ::= BEGIN Foo ::= [2] UTCTime END'
        foo = asn1tools.compile_string(spec)
        encoded = foo.encode('Foo', '121001230001')
        self.assertEqual(encoded, b'\xa2\x0f\x17\x0d121001230001Z')
        decoded = foo.decode('Foo', encoded)
        self.assertEqual(decoded, '121001230001')

    def test_utf8_string_explicit_tags(self):
        """Test explicit tags on UTC time.

        """

        spec = 'Foo DEFINITIONS ::= BEGIN Foo ::= [2] UTF8String END'
        foo = asn1tools.compile_string(spec)
        encoded = foo.encode('Foo', 'foo')
        self.assertEqual(encoded, b'\xa2\x05\x0c\x03foo')
        decoded = foo.decode('Foo', encoded)
        self.assertEqual(decoded, 'foo')

    def test_nested_explicit_tags(self):
        """Test nested explicit tags.

        Based on https://github.com/wbond/asn1crypto/issues/63 by tiran.

        """

        spec = """
        TESTCASE DEFINITIONS EXPLICIT TAGS ::=
        BEGIN
        INNERSEQ ::= SEQUENCE {
        innernumber       [21] INTEGER
        }

        INNER ::= [APPLICATION 20] INNERSEQ

        OUTERSEQ ::= SEQUENCE {
        outernumber  [11] INTEGER,
        inner        [12] INNER
        }

        OUTER ::= [APPLICATION 10] OUTERSEQ
        END
        """

        decoded_message = {
            'outernumber': 23,
            'inner': {
                'innernumber': 42
            }
        }

        encoded_message = (
            b'\x6a\x12\x30\x10\xab\x03\x02\x01\x17\xac\x09\x74\x07\x30'
            b'\x05\xb5\x03\x02\x01\x2a'
        )

        testcase = asn1tools.compile_string(spec)
        encoded = testcase.encode('OUTER', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = testcase.decode('OUTER', encoded)
        self.assertEqual(decoded, decoded_message)

    def test_duplicated_type(self):
        """Duplicated types makes the types dictionary None.

        """

        spec = """
        Foo DEFINITIONS ::= BEGIN Fum ::= INTEGER END
        Bar DEFINITIONS ::= BEGIN Fum ::= BOOLEAN END
        """

        foo_bar = asn1tools.compile_string(spec)
        self.assertEqual(foo_bar.types, None)

    def test_zforce(self):
        """

        """

        zforce = asn1tools.compile_dict(deepcopy(ZFORCE))

        # PDU 1.
        decoded_message = {
            'request': {
                'deviceAddress': b'\x00\x01'
            }
        }
        encoded_message = b'\xee\x04\x40\x02\x00\x01'

        encoded = zforce.encode('ProtocolMessage', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = zforce.decode('ProtocolMessage', encoded)
        self.assertEqual(decoded, decoded_message)

        # PDU 2.
        decoded_message = {
            'request': {
                'enable': {
                    'enable': 1
                }
            }
        }
        encoded_message = b'\xee\x05\x65\x03\x81\x01\x01'

        encoded = zforce.encode('ProtocolMessage', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = zforce.decode('ProtocolMessage', encoded)
        self.assertEqual(decoded, decoded_message)

        # PDU 3.
        decoded_message = {
            'response': {
                'enable': {
                    'reset': None
                },
                'openShort': {
                    'openShortInfo': [],
                    'errorCount': 34
                }
            }
        }
        encoded_message = (
            b'\xef\x0b\x65\x02\x82\x00\x6a\x05\xa0\x00\x81\x01\x22'
        )

        encoded = zforce.encode('ProtocolMessage', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = zforce.decode('ProtocolMessage', encoded)
        self.assertEqual(decoded, decoded_message)

        # PDU 4.
        decoded_message = {
            'notification': {
                'notificationMessage': {
                    'ledLevels': [
                        {'uint8': b'\x55\x44\x33\x22'},
                        {'uint16': b'\x01\x02'}
                    ]
                },
                'notificationTimestamp': 1,
                'notificationLatency': 21
            }
        }
        encoded_message = (
            b'\xf0\x13\x6b\x0a\x80\x04\x55\x44\x33\x22\x82\x02\x01\x02\x58'
            b'\x01\x01\x5f\x23\x01\x15'
        )

        encoded = zforce.encode('ProtocolMessage', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = zforce.decode('ProtocolMessage', encoded)
        self.assertEqual(decoded, decoded_message)

        # PDU 5.
        decoded_message = {
            'request': {
                'errorLog': -2,
                'errorThresholds': {
                    'asicsThresholds': [
                        {
                            'asicIdentifier': -256,
                            'irLedOpenThresholds': {
                                'low': -4500,
                                'high': 100000
                            }
                        }
                    ]
                }
            }
        }
        encoded_message = (
            b'\xee\x1a\x5f\x21\x01\xfe\x7f\x22\x13\xa0\x11\xa0\x0f\x80\x02'
            b'\xff\x00\xa1\x09\x80\x02\xee\x6c\x81\x03\x01\x86\xa0'
        )

        encoded = zforce.encode('ProtocolMessage', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = zforce.decode('ProtocolMessage', encoded)
        self.assertEqual(decoded, decoded_message)

    def test_bar(self):
        """A simple example.

        """

        bar = asn1tools.compile_files('tests/files/bar.asn')

        # Message 1.
        decoded_message = {
            'headerOnly': True,
            'lock': False,
            'acceptTypes': {
                'standardTypes': [(b'\x40', 4), (b'\x80', 4)]
            },
            'url': b'/ses/magic/moxen.html'
        }

        encoded_message = (
            b'\x60\x29\x01\x01\xff\x01\x01\x00\x61\x0a\xa0\x08\x03\x02\x04'
            b'\x40\x03\x02\x04\x80\x04\x15\x2f\x73\x65\x73\x2f\x6d\x61\x67'
            b'\x69\x63\x2f\x6d\x6f\x78\x65\x6e\x2e\x68\x74\x6d\x6c'
        )

        encoded = bar.encode('GetRequest', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = bar.decode('GetRequest', encoded)
        self.assertEqual(decoded, decoded_message)

        # Message 2.
        decoded_message = {
            'headerOnly': False,
            'lock': False,
            'url': b'0'
        }

        encoded_message = b'\x60\x09\x01\x01\x00\x01\x01\x00\x04\x01\x30'

        encoded = bar.encode('GetRequest', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = bar.decode('GetRequest', encoded)
        self.assertEqual(decoded, decoded_message)

    def test_any_defined_by_integer(self):
        spec = """
        Foo DEFINITIONS ::= BEGIN

        Fie ::= SEQUENCE {
            bar INTEGER,
            fum ANY DEFINED BY bar
        }

        END
        """

        any_defined_by_choices = {
            ('Foo', 'Fie', 'fum'): {
                0: 'NULL',
                1: 'INTEGER'
            }
        }

        foo = asn1tools.compile_string(
            spec,
            any_defined_by_choices=any_defined_by_choices)

        # Message 1.
        decoded_message = {
            'bar': 0,
            'fum': None
        }

        encoded_message = b'\x30\x05\x02\x01\x00\x05\x00'

        encoded = foo.encode('Fie', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = foo.decode('Fie', encoded)
        self.assertEqual(decoded, decoded_message)

        # Message 2.
        decoded_message = {
            'bar': 1,
            'fum': 5
        }

        encoded_message = b'\x30\x06\x02\x01\x01\x02\x01\x05'

        encoded = foo.encode('Fie', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = foo.decode('Fie', encoded)
        self.assertEqual(decoded, decoded_message)

        # Message 3, key not found.
        decoded_message = {
            'bar': 2,
            'fum': 5
        }

        encoded_message = b'\x30\x06\x02\x01\x02\x02\x01\x05'

        with self.assertRaises(KeyError) as cm:
            foo.encode('Fie', decoded_message)

        self.assertEqual(str(cm.exception), "2")

        with self.assertRaises(KeyError) as cm:
            decoded = foo.decode('Fie', encoded_message)

        self.assertEqual(str(cm.exception), "2")

    def test_any_defined_by_object_identifier(self):
        spec = """
        Foo DEFINITIONS ::= BEGIN

        Fie ::= SEQUENCE {
            bar OBJECT IDENTIFIER,
            fum ANY DEFINED BY bar
        }

        END
        """

        any_defined_by_choices = {
            ('Foo', 'Fie', 'fum'): {
                '1.3.6.2':    'IA5String',
                '1.3.1000.7': 'BOOLEAN'
            }
        }

        foo = asn1tools.compile_string(
            spec,
            any_defined_by_choices=any_defined_by_choices)

        # Message 1.
        decoded_message = {
            'bar': '1.3.6.2',
            'fum': 'Hello!'
        }

        encoded_message = b'0\r\x06\x03+\x06\x02\x16\x06Hello!'

        encoded = foo.encode('Fie', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = foo.decode('Fie', encoded)
        self.assertEqual(decoded, decoded_message)

        # Message 2.
        decoded_message = {
            'bar': '1.3.1000.7',
            'fum': True
        }

        encoded_message = b'0\t\x06\x04+\x87h\x07\x01\x01\xff'

        encoded = foo.encode('Fie', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = foo.decode('Fie', encoded)
        self.assertEqual(decoded, decoded_message)

        # Message 3, key not found.
        decoded_message = {
            'bar': '1.3.1000.8',
            'fum': True
        }

        encoded_message = b'0\t\x06\x04+\x87h\x08\x01\x01\x01'

        with self.assertRaises(KeyError) as cm:
            foo.encode('Fie', decoded_message)

        self.assertEqual(str(cm.exception), "'1.3.1000.8'")

        with self.assertRaises(KeyError) as cm:
            decoded = foo.decode('Fie', encoded_message)

        self.assertEqual(str(cm.exception), "'1.3.1000.8'")


if __name__ == '__main__':
    unittest.main()
