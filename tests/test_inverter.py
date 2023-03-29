import unittest
from inverter import scale_number


class TestScaleNumber(unittest.TestCase):
    def setUp(self):
        self.field_mapping = {"name": "Current Solar Production (kilowatts)",
                                   "format": "{:.1f}kW",
                                   "divisor": 1000,
                                   "color": "green"}

    def test_value_is_scaled(self):
        """test that 1000 is correctly scaled to 1"""

        self.value = 1000
        self.scaled_number = scale_number(value=self.value,
                                          field_info=self.field_mapping)
        self.assertEqual(1, self.scaled_number)

    def test_zero_value_is_handled(self):
        self.value = 0
        self.scaled_number = scale_number(value=self.value,
                                          field_info=self.field_mapping)
        self.assertEqual(0, self.scaled_number)

    def test_negative_value_is_handled(self):
        self.value = -1000
        self.scaled_number = scale_number(value=self.value,
                                          field_info=self.field_mapping)
        self.assertEqual(-1, self.scaled_number)

if __name__ == '__main__':
    unittest.main()
