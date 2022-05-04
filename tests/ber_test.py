"""ber_test.py
"""
# Standard library imports
import unittest as _unittest

# Third party imports

# Local application imports
from common.ber import _decode_tag, _decode_length, _decode_value, parse, find, encode_length

class _TestMethods(_unittest.TestCase):
    def test__decode_tag(self):
        self.assertEqual(_decode_tag('5A080123456789ABCDEF'), ('5A', '080123456789ABCDEF'))
        self.assertEqual(_decode_tag('9F36021234'), ('9F36', '021234'))
        self.assertEqual(_decode_tag('5'), ('', '5'))
        self.assertEqual(_decode_tag(''), ('', ''))

    def test__decode_length(self):
        self.assertEqual(_decode_length('080123456789ABCDEF'), ('08', '0123456789ABCDEF'))
        self.assertEqual(_decode_length('8000'), ('80', '00'))
        self.assertEqual(_decode_length('FF00'), ('FF', '00'))
        self.assertEqual(_decode_length('818000'), ('8180', '00'))
        self.assertEqual(_decode_length(''), ('', ''))
        self.assertEqual(_decode_length('F'), ('', 'F'))
        self.assertEqual(_decode_length('FFF'), ('', 'FFF'))

    def test__decode_value(self):
        self.assertEqual(_decode_value('10', '8408A000000003000000A5049F6501FF'), ('8408A000000003000000A5049F6501FF', ''))
        self.assertEqual(_decode_value('8180', '0123456789ABCDEF' * 16), ('0123456789ABCDEF' * 16, ''))
        self.assertEqual(_decode_value('10', '8408A0'), ('', '8408A0'))
        self.assertEqual(_decode_value('80', '0123456789ABCDEF0000'), ('0123456789ABCDEF', ''))

    def test_parse(self):
        self.assertEqual(parse('6F108408A000000003000000A5049F6501FF', recursive=False), ([('6F', '10', '8408A000000003000000A5049F6501FF')], ''))
        self.assertEqual(parse('6F108408A000000003000000A5049F6501FF', recursive=True),
                         ([('6F', '10',
                             [('84', '08', 'A000000003000000'),
                              ('A5', '04',
                               [('9F65', '01', 'FF')]
                               )
                              ]
                            )
                           ],
                          ''))
        self.assertEqual(parse('8408A000000003000000A5049F6501FF', recursive=True),
                         ([('84', '08', 'A000000003000000'), ('A5', '04', [('9F65', '01', 'FF')])],
                          ''))
        self.assertEqual(parse('006F108408A000000003000000A5049F6501FF', recursive=False),
                         ([('6F', '10', '8408A000000003000000A5049F6501FF')], ''))
        self.assertEqual(parse('6F108408A000000003000000A5049F6501FF00', recursive=False),
                         ([('6F', '10', '8408A000000003000000A5049F6501FF')], ''))
        self.assertEqual(parse('6F108408A000000003000000A5049F6501FF006F108408A000000003000000A5049F6501FF', recursive=False),
                         ([('6F', '10', '8408A000000003000000A5049F6501FF'), ('6F', '10', '8408A000000003000000A5049F6501FF')], ''))

    def test_parse(self):
        self.assertEqual(find('6F', [('6F', '10', [('84', '08', 'A000000003000000'), ('A5', '04', [('9F65', '01', 'FF')])])]),
                             ('6F', '10', [('84', '08', 'A000000003000000'), ('A5', '04', [('9F65', '01', 'FF')])]))
        self.assertEqual(find('84', [('6F', '10', [('84', '08', 'A000000003000000'), ('A5', '04', [('9F65', '01', 'FF')])])]),
                             ('84', '08', 'A000000003000000'))
        self.assertEqual(find('A5', [('6F', '10', [('84', '08', 'A000000003000000'), ('A5', '04', [('9F65', '01', 'FF')])])]),
                             ('A5', '04', [('9F65', '01', 'FF')]))
        self.assertEqual(find('9F65', [('6F', '10', [('84', '08', 'A000000003000000'), ('A5', '04', [('9F65', '01', 'FF')])])]),
                             ('9F65', '01', 'FF'))

    def test_encode_length(self):
        self.assertEqual(encode_length('A0000000041010'), '07')
        self.assertEqual(encode_length('0123456789ABCDEF' * 16), '8180')


if __name__ == '__main__':
    _unittest.main()
