import unittest
import os
import itertools

from generarinforme.generarinforme import *

from datetime import datetime, timedelta

class TestGenerarInforme(unittest.TestCase):
	def test_creacio_array_cotxes(self):
		"""
		Test de com es crea l'array de cotxes a partir del fitxer de matricules.txt
		"""
		fitxer = 'simulaciodades/data/matricules.txt'
		f = open(fitxer, 'r')
		arr_linies = f.readlines()
		f.close()
		self.assertEqual(len(arr_linies), 1000)

		dicc = [
			{"name":"tipus I", "proporcio":.1, "perc": [20, 50], "mu_t": 21, "s_t": 1, "mu_d": 3, "s_d": 1},
			{"name":"tipus II", "proporcio":.1, "perc": [20, 50], "mu_t": 11, "s_t": 1, "mu_d": 3, "s_d": 1},
			{"name":"tipus III", "proporcio":.1, "perc": [20, 50], "mu_t": 9, "s_t": 1, "mu_d": 6, "s_d": 1},
			{"name":"tipus IV", "proporcio":.7, "perc": [1, 3], "mu_t": 12, "s_t": 8, "mu_d": 2, "s_d": 1}
		]

		arr = creacio_array_cotxes(dicc, arr_linies)
		arr_flatten = list(itertools.chain.from_iterable(arr))
		self.assertEqual(len(arr_linies), len(arr_flatten))

if __name__ == '__main__':
	unittest.main()
