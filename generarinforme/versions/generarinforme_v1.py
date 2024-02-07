'''
@ IOC - Joan Quintana - 2024 - CE IABD
'''

from utils.customformatter import CustomFormatter

from datetime import datetime
import sys
import itertools
#import random
#import string
import logging
#import numpy as np

sys.path.append("..")
from simulaciodades.simulaciodades import generar_caps_de_setmana, generar_diumenges, generar_feiners, generar_dies_tots, generar_dades_tipus

logger = logging.getLogger("generarinforme")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO) # canviar a DEBUG mentre es programa
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

def generacio_dades(c, dicc_, dies_):
	logger.info("SIMULACIO XXX")
	arr_cotxes = []
	for i in range(4):
		arr_cotxes.append(generar_dades_tipus(i, c[i], dicc_, dies_))

	# fem el flatten, i ordenem per les dates
	arr_cotxes = list(itertools.chain.from_iterable(arr_cotxes)) # amb un array de numpy això es fa amb flatten()

def creacio_array_cotxes(dicc_, matricules_):

	cotxes = [[], [], [], []] # tipus I, II, III i IV
	count = 0

	# assignació de cotxes a tipologia
	for mat in matricules:
		mat = mat.strip()

		if count <= int(dicc_[0]['proporcio']*len(matricules_)):
			cotxes[0].append(mat)
		elif count <= int((dicc_[0]['proporcio'] + dicc_[0]['proporcio'])*len(matricules_)):
			cotxes[1].append(mat)
		elif count <= int((dicc_[0]['proporcio'] + dicc_[0]['proporcio'] + dicc_[0]['proporcio'])*len(matricules_)):
			cotxes[2].append(mat)
		else:
			cotxes[3].append(mat)

		count += 1

	return cotxes

def creacio_diccionari(i):
	if i==0:
		dicc = [
			{"name":"tipus I", "proporcio":.1, "perc": [20, 50], "mu_t": 21, "s_t": 1, "mu_d": 3, "s_d": 1},
			{"name":"tipus II", "proporcio":.1, "perc": [20, 50], "mu_t": 11, "s_t": 1, "mu_d": 3, "s_d": 1},
			{"name":"tipus III", "proporcio":.1, "perc": [20, 50], "mu_t": 9, "s_t": 1, "mu_d": 6, "s_d": 1},
			{"name":"tipus IV", "proporcio":.7, "perc": [1, 3], "mu_t": 12, "s_t": 8, "mu_d": 2, "s_d": 1}
		]
	else:
		dicc = [
			{"name":"tipus I", "proporcio":.2, "perc": [20, 50], "mu_t": 21, "s_t": 1, "mu_d": 3, "s_d": 1},
			{"name":"tipus II", "proporcio":.2, "perc": [20, 50], "mu_t": 11, "s_t": 1, "mu_d": 3, "s_d": 1},
			{"name":"tipus III", "proporcio":.2, "perc": [20, 50], "mu_t": 9, "s_t": 1, "mu_d": 6, "s_d": 1},
			{"name":"tipus IV", "proporcio":.4, "perc": [1, 3], "mu_t": 12, "s_t": 8, "mu_d": 2, "s_d": 1}
		]

	return dicc

if __name__ == "__main__":

	dia_inici = datetime(2023, 1, 1, 0, 0, 0)
	dia_fi = datetime(2023, 12, 31, 23, 59, 59)

	dies = []
	dies.append(generar_caps_de_setmana(dia_inici, dia_fi))
	dies.append(generar_diumenges(dia_inici, dia_fi))
	dies.append(generar_feiners(dia_inici, dia_fi))
	dies.append(generar_dies_tots(dia_inici, dia_fi))

	str_matricules = '../simulaciodades/data/matricules.txt'
	f = open(str_matricules, 'r')
	matricules = f.readlines()
	f.close()

	# simulació 1
	dicc = creacio_diccionari(0)
	cotxes = creacio_array_cotxes(dicc, matricules)
	generacio_dades(cotxes, dicc, dies)

	# simulació 2
	dicc = creacio_diccionari(1)
	cotxes = creacio_array_cotxes(dicc, matricules)
	generacio_dades(cotxes, dicc, dies)

	logger.info("FINAL")
