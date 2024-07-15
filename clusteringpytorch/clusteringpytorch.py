'''
@ IOC - Joan Quintana - 2024 - CE IABD
'''

import os
import logging
from contextlib import contextmanager, redirect_stderr, redirect_stdout

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import torch

from sklearn import preprocessing
from sklearn.metrics.cluster import homogeneity_score, completeness_score, v_measure_score
from kmeans_pytorch import kmeans, kmeans_predict

@contextmanager
def suppress_stdout_stderr():
	"""A context manager that redirects stdout and stderr to devnull"""
	with open(os.devnull, 'w') as fnull:
		with redirect_stderr(fnull) as err, redirect_stdout(fnull) as out:
			yield (err, out)

# ----------------------------------------------

def load_dataset(path):
	"""
	Carrega el dataset de registres del parking

	arguments:
		path -- dataset

	Returns: dataframe
	"""
	return pd.read_csv(path, delimiter=';')

def EDA(df):
	"""
	Exploratory Data Analysis del dataframe

	arguments:
		df -- dataframe

	Returns: None
	"""
	logging.debug('\n%s', df.shape)
	logging.debug('\n%s', df[:5])
	logging.debug('\n%s', df.columns)
	logging.debug('\n%s', df.info())

def clean(df):
	"""
	Elimina les columnes que no són necessàries

	arguments:
		df -- dataframe

	Returns: dataframe
	"""
	# eliminem les columnes que no interessen
	df = df.drop('dia_hora', axis=1)
	df = df.drop('dia_setmana', axis=1)
	logging.debug('\nDataframe:\n%s\n...', df[:3])

	return df

def extract_true_labels(df):
	"""
	Fem un agrupament de les matrícules i ens guardem els seus labels vertaders

	arguments:
		df -- dataframe

	Returns: numpy ndarray (true labels)
	"""
	df_true_labels = df.groupby(['matricula']).mean()
	df_true_labels = df_true_labels.astype({'tipus': int})
	logging.debug('\nDades agrupades per matrícula:\n%s\n...', df_true_labels[:3])
	true_labels = df_true_labels["tipus"].to_numpy()

	return true_labels

def group_by(df):
	"""
	Agrupament del dataframe per matrícula, i les dades agrupades calculat la mitjana.
	Afegeix la columna count

	arguments:
		df -- dataframe

	Returns: dataframe
	"""
	df_gb = df.groupby(['matricula']).mean()
	df_gb = df_gb.merge(df.groupby(['matricula']).count()['durada'], how='inner', on='matricula')
	df_gb = df_gb.rename(columns={'durada_x': 'durada', 'durada_y': 'count'})
	logging.debug('\nDades agrupades per matrícula:\n%s\n...', df_gb[:3])

	return df_gb

def normalitzacio(df, sc):
	"""
	Normalitza les dades. Colummnes com la 'durada' són de l'ordre de desenes de milers (segons)

	arguments:
		df -- dataframe
		sc -- Scaler entrenat sobre el dataframe

	Returns: dataframe normalitzat
	"""
	# normalització de les dades amb StandardScaler
	df_norm = pd.DataFrame(sc.transform(df), index=df.index, columns=df.columns)
	logging.debug('\nDades normalitzades:\n%s\n...', df_norm[:3])

	return df_norm

def visualitzar_pairplot(df):
	"""
	Genera una imatge combinant entre sí tots els parells d'atributs.
	Serveix per apreciar si es podran trobar clústers.

	arguments:
		df -- dataframe

	Returns: None
	"""
	sns.pairplot(df)
	try:
		os.makedirs(os.path.dirname('img/'))
	except FileExistsError:
		pass
	plt.savefig("img/pairplot.png")
	#plt.show()

def clustering_kmeans(data, dev):
	"""
	Crea el model KMeans de sk-learn, amb 4 clusters (estem cercant 4 agrupacions)
	Entrena el model

	arguments:
		data -- el dataframe amb les dades seleccionades (en principi totes perquè hem eliminat les que no interessen)
		dev -- device (cpu o gpu)

	Returns: clusters (tupla de labels del dataset, i centers)
	"""
	# a pytorch treballem amb tensors
	tensor = torch.tensor(data.values)
	logging.debug('\nTensor:\n%s\n...', tensor[:3])

	cluster_ids_x, cluster_centers = kmeans(
		X=tensor, num_clusters=4, distance='euclidean', device=dev
	)

	return cluster_ids_x, cluster_centers

def visualitzar_clusters(data, centers):
	"""
	Visualitza els clusters en diferents colors. Provem diferents combinacions de parells d'atributs

	arguments:
		data -- el dataset sobre el qual hem entrenat
		labels -- l'array d'etiquetes a què pertanyen les dades (hem assignat les dades a un dels 4 clústers)

	Returns: None
	"""
	# Visualitzar els clústers/agrupaments
	tensor = torch.tensor(data.values)

	plt.figure(figsize=(4, 3), dpi=160)
	plt.scatter(tensor[:, 2], tensor[:, 3], c=cluster_ids_x, s=1)
	for num_cluster in range(len(centers)):
		plt.scatter(cluster_centers[num_cluster, 2], cluster_centers[num_cluster, 3], label=num_cluster, edgecolors='black')
	plt.legend()
	plt.xlabel("dia setmana")
	plt.ylabel("count")
	plt.savefig("img/grafica1.png")
	#plt.show()
	plt.clf()

	plt.figure(figsize=(4, 3), dpi=160)
	plt.scatter(tensor[:, 1], tensor[:, 0], c=cluster_ids_x, s=1)
	for num_cluster in range(len(cluster_centers)):
		plt.scatter(cluster_centers[num_cluster, 1], cluster_centers[num_cluster, 0], label=num_cluster, edgecolors='black')
	plt.legend()
	plt.xlabel("hora")
	plt.ylabel("durada")
	plt.savefig("img/grafica2.png")
	#plt.show()
	plt.clf()

	plt.figure(figsize=(4, 3), dpi=160)
	plt.scatter(tensor[:, 1], tensor[:, 3], c=cluster_ids_x, s=1)
	for num_cluster in range(len(cluster_centers)):
		plt.scatter(cluster_centers[num_cluster, 1], cluster_centers[num_cluster, 3], label=num_cluster, edgecolors='black')
	plt.legend()
	plt.xlabel("hora")
	plt.ylabel("count")
	plt.savefig("img/grafica3.png")
	#plt.show()
	plt.clf()

def associar_clusters_patrons(tipus, centers):
	"""
	Associa els clústers (labels 0, 1, 2, 3) als patrons de comportament (I, II, III, IV).
	S'han trobat 4 clústers però aquesta associació encara no s'ha fet.

	arguments:
	tip -- un array de tipus de patrons que volem actualitzar associant els labels
	model -- model KMeans entrenat

	Returns: array de diccionaris amb l'assignació dels tipus als labels
	"""
	# durada, hora, dia_setmana_dec, count
	dicc = {'durada':0, 'hora': 1, 'dia_setmana_dec': 2, 'count': 3}

	logging.debug('\nCentres:')
	for j in range(len(tipus)):
		logging.debug('\n{:d}:\t(durada: {:.1f}\thora: {:.1f}\tdia_setmana_dec: {:.1f}\tcount: {:.1f})'.format(j, centers[j][dicc['durada']], centers[j][dicc['hora']], centers[j][dicc['dia_setmana_dec']], centers[j][dicc['count']]))

	# Procés d'assignació
	ind_label_0 = -1
	ind_label_1 = -1
	ind_label_2 = -1
	ind_label_3 = -1

	val_hora_max = -1
	val_count_max = -1
	val_count_min = 1000

	for j, center in enumerate(centers):
		v_hora = round(center[dicc['hora']].item(), 1)
		v_count = round(center[dicc['count']].item(), 1)

		if (v_hora) > val_hora_max:
			ind_label_0 = j
			val_hora_max = v_hora
		if (v_count) > val_count_max:
			ind_label_2 = j
			val_count_max = v_count
		if (v_count) < val_count_min:
			ind_label_3 = j
			val_count_min = v_count

	lst = [0, 1, 2, 3]
	lst.remove(ind_label_0)
	lst.remove(ind_label_2)
	lst.remove(ind_label_3)
	ind_label_1 = lst[0]
	tipus[0].update({'label': ind_label_0})
	tipus[1].update({'label': ind_label_1})
	tipus[2].update({'label': ind_label_2})
	tipus[3].update({'label': ind_label_3})

	return tipus

def nova_prediccio(dades, sc, cluster_centers):
	"""
	Passem nous valors de registre en el parking, per tal d'assignar aquests valors a un dels 4 clústers

	arguments:
		dades -- array de Python, que segueix l'estructura 'matricula', 'durada', 'hora', 'dia_setmana_dec'
		sc -- objecte Scaler
		cluster_centers -- objecte cluster_centers
	Returns: (dades agrupades, prediccions del model)
	"""
	df_dades_cotxe = pd.DataFrame(columns=['matricula', 'durada', 'hora', 'dia_setmana_dec'], data=dades)

	df_dades_cotxe_gb = group_by(df_dades_cotxe)
	df_dades_cotxe_gb_norm = normalitzacio(df_dades_cotxe_gb, sc)

	logging.debug('\nNous valors agrupats i normalitzats:\n%s', df_dades_cotxe_gb_norm[:3])
	tensor_cotxe = torch.tensor(df_dades_cotxe_gb_norm.values)

	cluster_ids_y = kmeans_predict(
		tensor_cotxe, cluster_centers, 'euclidean', device=device
	)

	return df_dades_cotxe_gb, cluster_ids_y

def generar_informes(df, tipus):
	"""
	Generació dels informes a la carpeta informes/. Tenim un dataset de cotxes i 4 clústers, i generem
	4 fitxers de matrícules per cadascun dels clústers

	arguments:
		df -- dataframe
		tipus -- objecte que associa els patrons de comportament amb els labels dels clústers

	Returns: None
	"""
	cotxes_label = [
		df[df['label'] == 0],
		df[df['label'] == 1],
		df[df['label'] == 2],
		df[df['label'] == 3]
	]

	try:
		os.makedirs(os.path.dirname('informes/'))
	except FileExistsError:
		pass

	for tip in tipus:
		fitxer = tip['name'].replace(' ', '_') + '.txt'
		foutput = open("informes/" + fitxer, "w")
		t = [t for t in tipus if t['name'] == tip['name']]
		matricules = cotxes_label[t[0]['label']].index
		for matricula in matricules:
			foutput.write(matricula + '\n')

		foutput.close()

	logging.info('\nS\'han generat els informes en la carpeta informes/')

# ----------------------------------------------

if __name__ == "__main__":

	logging.basicConfig(format='%(message)s', level=logging.INFO) # canviar entre DEBUG i INFO
	logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR) # per tal de què el matplotlib no vomiti molts missatges

	path_dataset = '../simulaciodades/data/registre_durada.csv'
	parking_data = load_dataset(path_dataset)

	EDA(parking_data)

	parking_data = clean(parking_data)

	true_labels = extract_true_labels(parking_data)

	parking_data = parking_data.drop('tipus', axis=1) # eliminem el tipus, ja no interessa
	parking_data_gb = group_by(parking_data)

	scaler = preprocessing.StandardScaler().fit(parking_data_gb)
	parking_data_gb_norm = normalitzacio(parking_data_gb, scaler)

	visualitzar_pairplot(parking_data_gb_norm)

	# clustering amb KMeans
	# seleccionar durada, hora, dia_setmana_dec, count (de fet ho seleccionem tot)
	selected_data = parking_data_gb_norm.iloc[:, 0:4]
	logging.debug('\nDades per l\'entrenament:\n%s\n...', selected_data[:3])

	# set device
	if torch.cuda.is_available():
		device = torch.device('cuda:0')
	else:
		device = torch.device('cpu')

	cluster_ids_x, cluster_centers = clustering_kmeans(selected_data, device)

	logging.info('\nHomogeneity: %.3f', homogeneity_score(true_labels, cluster_ids_x))
	logging.info('Completeness: %.3f', completeness_score(true_labels, cluster_ids_x))
	logging.info('V-measure: %.3f', v_measure_score(true_labels, cluster_ids_x))

	visualitzar_clusters(selected_data, cluster_centers)

	# array de diccionaris que assignarà els tipus als labels
	tipus = [{'name': 'tipus I'}, {'name': 'tipus II'}, {'name': 'tipus III'}, {'name': 'tipus IV'}]

	# afegim la columna label al dataframe
	parking_data_gb['label'] = cluster_ids_x.tolist()

	logging.debug('\nColumna label:\n%s', parking_data_gb[:5])

	tipus = associar_clusters_patrons(tipus, cluster_centers)
	logging.info('\nTipus i labels:\n%s', tipus)

	# Classificació de nous valors
	dades_cotxe = [
		['6897 JWK', 12195, 12.2, 6.5],
		['6897 JWK', 11881, 11.2, 6.5],
		['6897 JWK', 12885, 11.5, 6.5],
		['6897 JWK', 10549, 11.1, 6.5],
		['6897 JWK', 2359, 11.6, 6.5],

		['3560 ROQ', 7197, 21.5, 6.9],
		['3560 ROQ', 4941, 21.1, 5.9],
		['3560 ROQ', 13461, 20.1, 6.8],
		['3560 ROQ', 13818, 19.4, 5.8],
		['3560 ROQ', 11251, 19.9, 6.8]
	]*8

	logging.debug('\nNous valors:\n%s', dades_cotxe[:5])
	dades_cotxe_gb, pred = nova_prediccio(dades_cotxe, scaler, cluster_centers)
	# NOTA: a pytorch l'assignació dels dos cotxes als tipus I i II no sempre es fa de forma correcta (la majoria de les vegades sí. Fixar-se en el valor que dóna es scores)
	logging.info('\nPredicció dels valors:\n%s', pred)

	#Assignació dels nous valors als tipus
	for i, p in enumerate(pred):
		t = [t for t in tipus if t['label'] == p]
		logging.info('%s: %s', dades_cotxe_gb.index[i], t[0]['name'])

	# Generació d'informes
	generar_informes(parking_data_gb, tipus)
