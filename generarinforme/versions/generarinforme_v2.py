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

def creacio_objecte_simulacio():
	'''
	dicc = [
		{"name":"tipus I", "proporcio":.1, "perc": [20, 50], "mu_t": 21, "s_t": 1, "mu_d": 3, "s_d": 1},
		{"name":"tipus II", "proporcio":.1, "perc": [20, 50], "mu_t": 11, "s_t": 1, "mu_d": 3, "s_d": 1},
		{"name":"tipus III", "proporcio":.1, "perc": [20, 50], "mu_t": 9, "s_t": 1, "mu_d": 6, "s_d": 1},
		{"name":"tipus IV", "proporcio":.7, "perc": [1, 3], "mu_t": 12, "s_t": 8, "mu_d": 2, "s_d": 1}
	]
	'''
	dicc = []

	# variació sobre les proporcions (60%, 75%, 90% de cotxes normals)
	for prop in [.60, .75, .90]:
		# variació de percentatges
		# ie, els cotxes tipus I utilitzen el pàrquing entre el 10% i el 20% dels caps de setmana (menys ús),
		# o bé entre el 20% i el 30%,
		# o bé entre el 30% i el 50% (ús més intensiu),
		# els cotxes tipus IV l'utilitzen entre el 1% i el 3% (fix)
		for perc in [[10, 20], [20, 35], [30, 50]]:

			# variació sobre la sigma de les districbucions normals (menys estretes, més estretes)
			# variació tant de l'hora d'entrada com de la durada
			# tipus I, II i III varia entre 0,5hores (més estret) i 1.5 hores (menys estret)
			# tipus IV: varia entre un rang de 12 h (es reparteix més tot el dia), 9h o 6h (no hi ha tant marge)
			for sigma in [[0.5, 12], [1.0, 9], [1.5, 6]]:

				dicctemp = [
					{"name":"tipus I", "proporcio":1.-prop, "perc": [perc[0], perc[1]], "mu_t": 21, "s_t": sigma[0], "mu_d": 3, "s_d": sigma[0]},
					{"name":"tipus II", "proporcio":1.-prop, "perc": [perc[0], perc[1]], "mu_t": 11, "s_t": sigma[0], "mu_d": 3, "s_d": sigma[0]},
					{"name":"tipus III", "proporcio":1.-prop, "perc": [perc[0], perc[1]], "mu_t": 9, "s_t": sigma[0], "mu_d": 6, "s_d": sigma[0]},
					{"name":"tipus IV", "proporcio":prop, "perc": [1, 3], "mu_t": 12, "s_t": sigma[1], "mu_d": 2, "s_d": 1}
				]
				dicc.append(dicctemp)


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

	dicc_simulacio = creacio_objecte_simulacio() # array d'array de diccionaris
	
	# recorrem tots els diccionaris de simulació
	for sim in enumerate(dicc_simulacio):
		logger.info("SIMULACIO " + str(sim[0]))
		cotxes = creacio_array_cotxes(sim[1], matricules)
		generacio_dades(cotxes, sim[1], dies)
		if sim[0] == 0:
			break

	logger.info("FINAL")
