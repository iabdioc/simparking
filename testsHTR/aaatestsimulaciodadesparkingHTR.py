import HtmlTestRunner
import unittest
import sys

sys.path.append("..")
from simulacio_parking.simulacio_parking import ocr

class TestOCR(unittest.TestCase):
	def test_ocr(self):
		"""
		Test del reconeixement d'una placa de matrícula
		"""
		# recordar que hi ha matrícules que no es reconeixen. L'eficàcia no és del 100%
		# aquestes sí que es reconeixen:
		arr_matricules = ['2117-FZG.png', '2776-ENR.png', '3234-RLY.png']
		for mat in arr_matricules:
			# ho estic executant des de l'arrel del projecte, i la ruta del fitxer ha de ser des d'aquí
			str_matricula = ocr('img/' + mat)
			self.assertEqual(str_matricula, mat.replace('.png', '').replace('-', ' '))

if __name__ == '__main__':
	unittest.main(testRunner=HtmlTestRunner.HTMLTestRunner(output='informe'))
