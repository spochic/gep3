"""test_common_ber.py
"""
# Standard library imports
import unittest

# Third party imports

# Local application imports
from common.ber import HexString, TagClass, TagConstruction, Tag, create_tag, Length, create_length, T_fieldP, L_fieldP, parserc, TagLengthValueP


#
# Test values
#


#
# Unit tests
#
class TestMethods(unittest.TestCase):
    def test_Tag(self):
        self.assertEqual(Tag('01').class_, TagClass.Universal)
        self.assertEqual(Tag('01').construction, TagConstruction.Primitive)
        self.assertEqual(Tag('01').number, 1)
        self.assertEqual(Tag('ED').class_, TagClass.Private)
        self.assertEqual(Tag('ED').construction, TagConstruction.Constructed)
        self.assertEqual(Tag('ED').number, 13)
        self.assertEqual(Tag('5F28').class_, TagClass.Application)
        self.assertEqual(Tag('5F28').construction, TagConstruction.Primitive)
        self.assertEqual(Tag('5F28').number, 40)

        with self.assertRaises(ValueError):
            Tag('5A080123456789ABCDEF')

    def test_create_tag(self):
        self.assertEqual(create_tag(TagClass.Universal, TagConstruction.Primitive, 1),
                         Tag('01'))
        self.assertEqual(create_tag(TagClass.Private, TagConstruction.Constructed, 13),
                         Tag('ED'))
        self.assertEqual(create_tag(TagClass.Application, TagConstruction.Primitive, 40),
                         Tag('5F28'))

    def test_Length(self):
        self.assertEqual(Length('05').value, 5)
        self.assertEqual(Length('8203FC').value, 1020)

        with self.assertRaises(ValueError):
            Length('5A080123456789ABCDEF')

    def test_create_length(self):
        self.assertEqual(create_length(HexString('FF'*5)), Length('05'))
        self.assertEqual(create_length(HexString('FF'*1020)), Length('8203FC'))

    def test_T_fieldP(self):
        self.assertEqual(T_fieldP.parse_partial('6F108408A000000003000000A5049F6501FF'),
                         ('6F', '108408A000000003000000A5049F6501FF'))
        self.assertEqual(T_fieldP.parse_partial('9F272D' + 'FF'*0x2d),
                         ('9F27', '2D' + 'FF'*0x2d))

    def test_L_fieldP(self):
        self.assertEqual(L_fieldP.parse_partial('108408A000000003000000A5049F6501FF'),
                         ('10', '8408A000000003000000A5049F6501FF'))
        self.assertEqual(L_fieldP.parse_partial('8180FF'),
                         ('8180', 'FF'))

    def test_TagLengthValueP(self):
        self.assertEqual(TagLengthValueP.parse_partial('8408A000000003000000A5049F6501FF'),
                         (('84', '08', 'A000000003000000'), 'A5049F6501FF'))
        self.assertEqual(parserc.many(TagLengthValueP).parse('8408A000000003000000A5049F6501FF'),
                         [('84', '08', 'A000000003000000'), ('A5', '04', '9F6501FF')])

    # def test_parse(self):
    #     self.assertEqual(find('6F', [('6F', '10', [('84', '08', 'A000000003000000'), ('A5', '04', [('9F65', '01', 'FF')])])]),
    #                      ('6F', '10', [('84', '08', 'A000000003000000'), ('A5', '04', [('9F65', '01', 'FF')])]))
    #     self.assertEqual(find('84', [('6F', '10', [('84', '08', 'A000000003000000'), ('A5', '04', [('9F65', '01', 'FF')])])]),
    #                      ('84', '08', 'A000000003000000'))
    #     self.assertEqual(find('A5', [('6F', '10', [('84', '08', 'A000000003000000'), ('A5', '04', [('9F65', '01', 'FF')])])]),
    #                      ('A5', '04', [('9F65', '01', 'FF')]))
    #     self.assertEqual(find('9F65', [('6F', '10', [('84', '08', 'A000000003000000'), ('A5', '04', [('9F65', '01', 'FF')])])]),
    #                      ('9F65', '01', 'FF'))

    # def test_parse_dol(self):
    #     self.assertEqual(parse_dol('9F1A02'), ([('9F1A', '02')], ''))


if __name__ == '__main__':
    unittest.main()
