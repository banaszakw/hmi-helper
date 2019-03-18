#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Created on Tue Feb 20 09:07:45 2018

@author: banaszakw
"""

import unittest
import HMI_Helper as hmi
from unittest import mock


class TestModel(unittest.TestCase):

    INP = ['pies Dingo', 'Tom siódmy', 'CO2', 'A_A', 'rak', 'Pluton', 'a_a',
           'wyŻ I Niż', 'ul pszczół', 'pies dingo', 'Ala', 'rak', 'ul pszczół',
           'Wąsy i żaba', 'rżą', 'ja', 'igła', 'H2O', 'Kot', 'co2', 'wyż i niż',
           'rąk', 'żÓŁw', 'pluton', 'rżą', 'rąk', 'KOT', 'żółw', 'Ala',
           'Wąsy i żaba', 'H2O', 'tom siódmy', 'kot']

    OUT = ["Ala", "Ala", "a_a", "A_A", "co2", "CO2", "H2O", "H2O", "igła", "ja",
           "kot", "Kot", "KOT", "pies dingo", "pies Dingo", "pluton", "Pluton",
           "rak", "rak", "rąk", "rąk", "rżą", "rżą", "tom siódmy", "Tom siódmy",
           "ul pszczół", "ul pszczół", "wyż i niż", "wyŻ I Niż", "Wąsy i żaba",
           "Wąsy i żaba", "żółw", "żÓŁw"]

    def setUp(self):
        self.model = hmi.AppCore()

    def test_teststr(self):
        wrongstr = ["Test, test", "test-Test", "Test_test1("]
        rightstr = ["Test_test1", "Test test 0", "00__00"]
        for w, r in zip(wrongstr, rightstr):
            self.assertFalse(self.model.teststr(w))
            self.assertTrue(self.model.teststr(r))

    def test_sort_ascend(self):
        self.assertListEqual(self.model.sort_ascend(self.INP), self.OUT)

    def test_sort_input(self):
        inp = "|pies dingo |pies|ala | alź | alą |sierotka Marysia | pluton|  " \
              "pies dingo | pies Dingo | PLUTON ||Pluton | | ala\n"
        out = ["ala", "ala", "alą", "alź", "pies", "pies dingo",
               "pies dingo", "pies Dingo", "pluton", "Pluton", "PLUTON",
               "sierotka Marysia"]
        self.assertListEqual(self.model.sort_input(inp), out)

    def test_sortedinput(self):
        """Testuje getter i setter"""
        sortedinput_calls = [mock.call("Ala | dom | ala | dom "),
                             mock.call()]
        with mock.patch('HMI_Helper.AppCore.sortedinput',
                        new_callable=mock.PropertyMock) as mock_sortedinput:
            self.model.sortedinput = "Ala | dom | ala | dom "
            self.model.sortedinput
            mock_sortedinput.assert_has_calls(sortedinput_calls)
            self.assertTrue(mock_sortedinput.call_count == 2)

    def test_search_strict_dupl(self):
        out = ["Ala", "H2O", "rak", "rąk", "rżą", "ul pszczół", "Wąsy i żaba"]
        self.assertListEqual(self.model.search_strict_dupl(self.INP), out)

    def test_strict_dupl(self):
        """Testuje getter i setter"""
        strict_dupl_calls = [mock.call("Ala | dom | ala | dom "),
                             mock.call()]
        with mock.patch('HMI_Helper.AppCore.strict_dupl',
                        new_callable=mock.PropertyMock) as mock_strict_dupl:
            self.model.strict_dupl = "Ala | dom | ala | dom "
            self.model.strict_dupl
            mock_strict_dupl.assert_has_calls(strict_dupl_calls)
            self.assertTrue(mock_strict_dupl.call_count == 2)

    def test_search_soft_dupl(self):
        out = ["a_a", "A_A", "co2", "CO2", "kot", "Kot", "KOT", "pies dingo",
               "pies Dingo", "pluton", "Pluton", "tom siódmy", "Tom siódmy",
               "wyż i niż", "wyŻ I Niż", "żółw", "żÓŁw"]
        self.assertListEqual(self.model.search_soft_dupl(self.INP), out)

    def test_soft_dupl(self):
        """Testuje getter i setter"""
        soft_dupl_calls = [mock.call("Ala | dom | ala | dom "),
                             mock.call()]
        with mock.patch('HMI_Helper.AppCore.soft_dupl',
                        new_callable=mock.PropertyMock) as mock_soft_dupl:
            self.model.soft_dupl = "Ala | dom | ala | dom "
            self.model.soft_dupl
            mock_soft_dupl.assert_has_calls(soft_dupl_calls)
            self.assertTrue(mock_soft_dupl.call_count == 2)

    def test_search_all_dupl(self):
        out = ["Ala", "a_a", "A_A", "co2", "CO2", "H2O", "kot", "Kot", "KOT",
               "pies dingo", "pies Dingo", "pluton", "Pluton", "rak",
               "rąk", "rżą", "tom siódmy", "Tom siódmy", "ul pszczół",
               "wyż i niż", "wyŻ I Niż", "Wąsy i żaba", "żółw", "żÓŁw"]
        self.assertListEqual(self.model.search_all_dupl(self.INP), out)


if __name__ == '__main__':
    unittest.main()
