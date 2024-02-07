'''
@ IOC - Joan Quintana - 2024 - CE IABD
'''

from utils.customformatter import CustomFormatter

from datetime import datetime
import sys
import itertools
import logging
import pandas as pd
from sklearn import preprocessing
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append("..")
from simulaciodades.simulaciodades import generar_caps_de_setmana, generar_diumenges, generar_feiners, generar_dies_tots, generar_dades_tipus

logger = logging.getLogger("generarinforme")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO) # canviar a DEBUG mentre es programa
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

def creacio_array_cotxes(dicc_, matricules_):

	cotxes = [[], [], [], []] # tipus I, II, III i IV
	count = 0

	# assignació de cotxes a tipologia
	for mat in matricules_:
		mat = mat.strip()

		if count <= int(dicc_[0]['proporcio']*len(matricules_)):
			cotxes[0].append(mat)
		elif count <= int((dicc_[0]['proporcio'] + dicc_[1]['proporcio'])*len(matricules_)):
			cotxes[1].append(mat)
		elif count <= int((dicc_[0]['proporcio'] + dicc_[1]['proporcio'] + dicc_[2]['proporcio'])*len(matricules_)):
			cotxes[2].append(mat)
		else:
			cotxes[3].append(mat)
		count += 1

	return cotxes

def generacio_dades(c, dicc_, dies_):
	logger.debug(dicc_)
	arr_cotxes = []
	for i in range(len(c)):
		arr_cotxes.append(generar_dades_tipus(c[i], dicc_[i], dies_[i])[1])

	# fem el flatten, i ordenem per les dates
	arr_cotxes = list(itertools.chain.from_iterable(arr_cotxes)) # amb un array de numpy això es fa amb flatten()
	return arr_cotxes

def creacio_objecte_simulacio():

	dicc = []

	# la variació de paràmetres va de dades més barrejades (més difícil de separar els clústers)
	# a dades més separades (més fàcil de separar els clústers)
	# variació sobre les proporcions (90%, 75%, 60% de cotxes normals)
	for prop in [.90, .75, .60]:
		# variació de percentatges
		# ie, els cotxes tipus I utilitzen el pàrquing entre el 10% i el 20% dels caps de setmana (menys ús),
		# o bé entre el 20% i el 30%,
		# o bé entre el 30% i el 50% (ús més intensiu),
		# els cotxes tipus IV l'utilitzen entre el 1% i el 3% (fix)
		for perc in [[10, 20], [20, 35], [30, 50]]:

			# variació sobre la sigma de les distribucions normals (menys estretes, més estretes)
			# variació tant de l'hora d'entrada com de la durada
			# tipus I, II i III varia entre 1,5 hores (més ample) i 0.5 hores (més estret)
			# tipus IV: varia entre un rang de 12 h (es reparteix més tot el dia), 9h o 6h (no hi ha tant marge)
			for sigma in [[1.5, 12], [1.0, 9], [0.5, 6]]:
				dicctemp = [
					{"name":"tipus I", "proporcio":round((1.-prop)/3,2), "perc": [perc[0], perc[1]], "mu_t": 21, "s_t": sigma[0], "mu_d": 3, "s_d": sigma[0]},
					{"name":"tipus II", "proporcio":round((1.-prop)/3,2), "perc": [perc[0], perc[1]], "mu_t": 11, "s_t": sigma[0], "mu_d": 3, "s_d": sigma[0]},
					{"name":"tipus III", "proporcio":round((1.-prop)/3,2), "perc": [perc[0], perc[1]], "mu_t": 9, "s_t": sigma[0], "mu_d": 6, "s_d": sigma[0]},
					{"name":"tipus IV", "proporcio":prop, "perc": [1, 3], "mu_t": 12, "s_t": sigma[1], "mu_d": 2, "s_d": 1}
				]
				dicc.append(dicctemp)

	return dicc

def tractament_dades(lst_parking_data):
	#['9566 JVI', 6461, 1.5]
	# matrícula, durada, dia_setmana_decimal
	# dia_setmana_decimal: 0 (dilluns), 6 (diumenge), 0.9 significa dilluns a la nit
	logger.debug(lst_parking_data[20])

	parking_data = pd.DataFrame(lst_parking_data, columns =['matricula', 'durada', 'hora', 'dia_setmana_dec']) 

	parking_data_gb = parking_data.groupby(['matricula']).mean()
	parking_data_gb = parking_data_gb.merge(parking_data.groupby(['matricula']).count()['durada'], how='inner', on='matricula')
	parking_data_gb = parking_data_gb.rename(columns={'durada_x': 'durada', 'durada_y': 'count'})
	logger.debug(parking_data_gb)

	# Normalització de les dades
	scaler = preprocessing.StandardScaler().fit(parking_data_gb)
	parking_data_gb_norm = pd.DataFrame(scaler.transform(parking_data_gb), index=parking_data_gb.index, columns=parking_data_gb.columns)
	logger.debug(parking_data_gb_norm[:3])
	#return parking_data_gb_norm
	return parking_data_gb

def generar_imatges(dades_norm_, sim_):
	logger.debug(sim_[1])
	titol = 'prop123: {:.1f}%'.format(sim_[1][0]['proporcio']*100)
	titol += '\nprop4: {:.1f}%'.format(sim_[1][3]['proporcio']*100)
	titol += '\nperc123: {:d}-{:d}%'.format(sim_[1][0]['perc'][0], sim_[1][0]['perc'][1])
	titol += '\nperc4: {:d}-{:d}%'.format(sim_[1][3]['perc'][0], sim_[1][3]['perc'][1])
	titol += '\nsigma123: {:.1f}\nsigma4: {:.1f}'.format(sim_[1][0]['s_t'], sim_[1][3]['s_t'])
	sns.pairplot(dades_norm_)
	plt.suptitle(titol, x=0.1, ha='left')
	plt.savefig('img/' + str(sim_[0]) + '.png')
	#plt.show()
	plt.close()

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
		dades = generacio_dades(cotxes, sim[1], dies)
		dades_norm = tractament_dades(dades)
		generar_imatges(dades_norm, sim)

		#if sim[0] == 0:
		#	break

	logger.info("FINAL")
