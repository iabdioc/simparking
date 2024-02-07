import unittest
import os

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

	def test_generar_diumenges(self):
		"""
		Test la longitud de l'array de dies dissabte/diumenge entre 15/01/2024 i 31/12/2024
		"""
		dia_inici = datetime(2024, 2, 5, 0, 0, 0)
		dia_fi = datetime(2024, 2, 23, 23, 59, 59)
		arr = generar_diumenges(dia_inici, dia_fi)
		self.assertEqual(len(arr), 2)

	def test_generar_dies_tots(self):
		"""
		Test la longitud de l'array de dies dissabte/diumenge entre 15/01/2024 i 31/12/2024
		"""
		dia_inici = datetime(2024, 2, 5, 0, 0, 0)
		dia_fi = datetime(2024, 2, 11, 23, 59, 59)
		arr = generar_dies_tots(dia_inici, dia_fi)
		self.assertEqual(len(arr), 7)

class TestGenerarMatricules(unittest.TestCase):

	def test_generar_fitxer_matricules(self):
		fitxer = 'tests/data/matricules.txt'
		generar_matricules(10, fitxer)
		f = open(fitxer, 'r')
		arr_linies = f.readlines()
		self.assertEqual(len(arr_linies), 10)
		f.close()

	def test_generar_matricules_png(self):
		# primer eliminar el contingut
		os.system('rm tests/matricules/*')

		fitxer = 'tests/data/matricules.txt'
		generar_matricules_png(fitxer, False, 'tests/matricules/') # sense imatge de fons

		count = 0
		for root_dir, cur_dir, files in os.walk(r'tests/matricules'):
			count += len(files)
		self.assertEqual(count, 10)

	def test_num_arxius_frontal(self):
		folder = "simulaciodades/matricules/frontal"
		#print(os.listdir(folder))
		self.assertEqual(len(os.listdir(folder)), 6)

	def test_num_matricules(self):
		folder = "simulaciodades/matricules/"
		num_pngs = len(os.listdir(folder)) # la carpeta folder també compta, i per tant en surten 1001 en comptes de 1000
		fitxer_matricules = "simulaciodades/data/matricules.txt"
		with open(fitxer_matricules, "r") as f:
			num_linies = len(f.readlines())

		self.assertEqual(num_pngs - 1, num_linies)



if __name__ == '__main__':
	unittest.main()
