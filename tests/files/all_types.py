EXPECTED = {'AllTypes': {'extensibility-implied': False,
              'imports': {},
              'object-classes': {},
              'object-sets': {},
              'types': {'Bitstring': {'type': 'BIT STRING'},
                        'Bitstring2': {'size': [9], 'type': 'BIT STRING'},
                        'Bitstring3': {'size': [(5, 7)], 'type': 'BIT STRING'},
                        'Bmpstring': {'type': 'BMPString'},
                        'Boolean': {'type': 'BOOLEAN'},
                        'Boolean2': {'type': 'BOOLEAN'},
                        'Boolean3': {'type': 'BOOLEAN'},
                        'Enumerated': {'type': 'ENUMERATED',
                                       'values': {1: 'one'}},
                        'Enumerated2': {'type': 'ENUMERATED',
                                        'values': {1: 'one',
                                                   2: 'two',
                                                   3: 'three'}},
                        'GeneralizedTime1': {'type': 'GeneralizedTime'},
                        'Ia5string': {'type': 'IA5String'},
                        'Ia5string2': {'type': 'IA5String'},
                        'Ia5string3': {'restricted-to': ['foo', 'bar', 'fie'],
                                       'type': 'IA5String'},
                        'Ia5string4': {'type': 'IA5String'},
                        'Integer': {'type': 'INTEGER'},
                        'Integer2': {'restricted-to': [(1, 99)],
                                     'type': 'INTEGER'},
                        'Integer3': {'restricted-to': [(1, 2), (9, 10)],
                                     'type': 'INTEGER'},
                        'Integer4': {'type': 'INTEGER'},
                        'Integer5': {'type': 'INTEGER'},
                        'Null': {'type': 'NULL'},
                        'Numericstring': {'type': 'NumericString'},
                        'Objectidentifier': {'type': 'OBJECT IDENTIFIER'},
                        'Octetstring': {'type': 'OCTET STRING'},
                        'Octetstring2': {'size': [2], 'type': 'OCTET STRING'},
                        'Octetstring3': {'size': [3], 'type': 'OCTET STRING'},
                        'Octetstring4': {'size': [(3, 7)],
                                         'type': 'OCTET STRING'},
                        'Octetstring5': {'size': [4, 9],
                                         'type': 'OCTET STRING'},
                        'Printablestring': {'type': 'PrintableString'},
                        'Real': {'type': 'REAL'},
                        'Real2': {'restricted-to': [('1.0', '2.0')],
                                  'type': 'REAL'},
                        'Real3': {'restricted-to': [(1, 2)], 'type': 'REAL'},
                        'Real4': {'restricted-to': [('1.', 2)], 'type': 'REAL'},
                        'Real5': {'restricted-to': [('1.', 2)], 'type': 'REAL'},
                        'Real6': {'restricted-to': [('-20.0', '-10.0')],
                                  'type': 'REAL'},
                        'Real7': {'tag': {'class': 'UNIVERSAL', 'number': 0},
                                  'type': 'REAL'},
                        'Real8': {'tag': {'class': 'APPLICATION', 'number': 0},
                                  'type': 'REAL'},
                        'Real9': {'tag': {'class': 'PRIVATE', 'number': 0},
                                  'type': 'REAL'},
                        'Sequence': {'members': [], 'type': 'SEQUENCE'},
                        'Sequence10': {'members': [{'name': 'c',
                                                    'type': 'Sequence9'},
                                                   {'name': 'd',
                                                    'type': 'Sequence9'},
                                                   '...'],
                                       'type': 'SEQUENCE'},
                        'Sequence11': {'type': 'Sequence10'},
                        'Sequence12': {'members': [{'element': {'type': 'Sequence12'},
                                                    'name': 'a',
                                                    'optional': True,
                                                    'type': 'SEQUENCE OF'}],
                                       'type': 'SEQUENCE'},
                        'Sequence2': {'members': [{'default': 0,
                                                   'name': 'a',
                                                   'type': 'INTEGER'}],
                                      'type': 'SEQUENCE'},
                        'Sequence3': {'members': [{'name': 'a',
                                                   'type': 'BOOLEAN'},
                                                  '...'],
                                      'type': 'SEQUENCE'},
                        'Sequence4': {'members': [{'name': 'a',
                                                   'type': 'BOOLEAN'},
                                                  '...',
                                                  {'name': 'b',
                                                   'type': 'BOOLEAN'}],
                                      'type': 'SEQUENCE'},
                        'Sequence5': {'members': [{'name': 'a',
                                                   'type': 'BOOLEAN'},
                                                  '...',
                                                  {'name': 'b',
                                                   'type': 'BOOLEAN'},
                                                  '...'],
                                      'type': 'SEQUENCE'},
                        'Sequence6': {'members': [{'name': 'a',
                                                   'type': 'BOOLEAN'},
                                                  '...',
                                                  {'name': 'b',
                                                   'type': 'BOOLEAN'},
                                                  '...',
                                                  {'name': 'c',
                                                   'type': 'BOOLEAN'}],
                                      'type': 'SEQUENCE'},
                        'Sequence7': {'members': [{'name': 'a',
                                                   'type': 'BOOLEAN'},
                                                  '...',
                                                  {'name': 'b',
                                                   'type': 'BOOLEAN'},
                                                  {'name': 'c',
                                                   'type': 'BOOLEAN'},
                                                  '...',
                                                  {'name': 'd',
                                                   'type': 'BOOLEAN'}],
                                      'type': 'SEQUENCE'},
                        'Sequence8': {'members': [{'name': 'a',
                                                   'type': 'BOOLEAN'},
                                                  '...',
                                                  '...'],
                                      'type': 'SEQUENCE'},
                        'Sequence9': {'members': [{'name': 'a',
                                                   'type': 'INTEGER'},
                                                  {'name': 'b',
                                                   'optional': True,
                                                   'type': 'BOOLEAN'}],
                                       'type': 'SEQUENCE'},
                        'SequenceOf': {'element': {'type': 'INTEGER'},
                                       'type': 'SEQUENCE OF'},
                        'Set': {'members': [], 'type': 'SET'},
                        'Set2': {'members': [{'default': 1,
                                              'name': 'a',
                                              'type': 'INTEGER'}],
                                 'type': 'SET'},
                        'SetOf': {'element': {'type': 'INTEGER'},
                                  'type': 'SET OF'},
                        'Teletexstring': {'type': 'TeletexString'},
                        'Universalstring': {'type': 'UniversalString'},
                        'Utctime': {'type': 'UTCTime'},
                        'Utf8string': {'type': 'UTF8String'},
                        'Visiblestring': {'type': 'VisibleString'}},
              'values': {'bitstring': {'type': 'BIT STRING',
                                       'value': '0b100010001001'},
                         'bitstring2': {'type': 'BIT STRING',
                                        'value': '0x0123456789ABCDEF'},
                         'boolean': {'type': 'BOOLEAN', 'value': 'TRUE'},
                         'boolean2': {'type': 'BOOLEAN', 'value': 'FALSE'},
                         'choice': {'type': 'CHOICE', 'value': 'foo'},
                         'ia5string': {'type': 'IA5String', 'value': '{'},
                         'ia5string2': {'type': 'IA5String', 'value': '{'}}}}
