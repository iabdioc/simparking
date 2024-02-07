import HtmlTestRunner
import unittest
import os
import sys

sys.path.append("..")
from simulaciodades.simulaciodades import *

from datetime import datetime, timedelta

class TestGenerarDies(unittest.TestCase):
	def test_generar_caps_de_setmana(self):
		"""
		Test la longitud de l'array de dies dissabte/diumenge entre 15/01/2024 i 31/12/2024
		"""
		dia_inici = datetime(2024, 1, 15, 0, 0, 0)
		dia_fi = datetime(2024, 12, 31, 23, 59, 59)
		arr = generar_caps_de_setmana(dia_inici, dia_fi)
		self.assertEqual(len(arr), 100)

	def test_generar_feiners(self):
		"""
		Test la longitud de l'array de dies dissabte/diumenge entre 15/01/2024 i 31/12/2024
		"""
		dia_inici = datetime(2024, 1, 22, 0, 0, 0)
		dia_fi = datetime(2024, 1, 26, 22, 0, 0)
		arr = generar_feiners(dia_inici, dia_fi)
		self.assertEqual(len(arr), 5)

class TestGenerarMatricules(unittest.TestCase):

	def test_generar_fitxer_matricules(self):
		fitxer = 'data/matricules.txt'
		generar_matricules(10, fitxer)
		f = open(fitxer, 'r')
		arr_linies = f.readlines()
		self.assertEqual(len(arr_linies), 10)
		f.close()

	def test_generar_matricules_png(self):
		# primer eliminar el contingut
		os.system('rm matricules/*')

		fitxer = 'data/matricules.txt'
		generar_matricules_png(fitxer, False, 'matricules/') # sense imatge de fons

		count = 0
		for root_dir, cur_dir, files in os.walk(r'matricules'):
			count += len(files)
		self.assertEqual(count, 10)
		
if __name__ == '__main__':
	unittest.main(testRunner=HtmlTestRunner.HTMLTestRunner(output='informe'))
