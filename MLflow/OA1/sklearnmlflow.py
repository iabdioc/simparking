""" @ IOC - Joan Quintana - 2024 - CE IABD """
import os
import logging
from contextlib import contextmanager, redirect_stderr, redirect_stdout
import pickle

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn import preprocessing
from sklearn.cluster import KMeans
from sklearn.metrics.cluster import homogeneity_score, completeness_score, v_measure_score

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

def standard_scaler(df):
	""" return normalized data """
	return preprocessing.StandardScaler().fit(df)

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

def clustering_kmeans(data, K=8, max_iter=300, tol=1e-4):
	"""
	Crea el model KMeans de sk-learn, amb 4 clusters (estem cercant 4 agrupacions)
	Entrena el model

	arguments:
		data -- el dataframe amb les dades seleccionades (en principi totes perquè hem eliminat les que no interessen)

	Returns: model (objecte KMeans)
	"""
	#random_state és important si vull reproduir els resultats (sempre s'assignen els mateixos labels als mateixos grups)
	model = KMeans(n_clusters=K, random_state=42, max_iter=max_iter, tol=tol)

	with suppress_stdout_stderr():
		model.fit(data)

	return model

def visualitzar_clusters(data, labels):
	"""
	Visualitza els clusters en diferents colors. Probem diferents combinacions de parells d'atributs

	arguments:
		data -- el dataset sobre el qual hem entrenat
		labels -- l'array d'etiquetes a què pertanyen les dades (hem assignat les dades a un dels 4 clústers)

	Returns: None
	"""
	# Visualitzar els clústers/agrupaments

	try:
		os.makedirs(os.path.dirname('img/'))
	except FileExistsError:
		pass

	fig = plt.figure()
	sns.scatterplot(x='dia_setmana_dec', y='hora', data=data, hue=labels, palette="rainbow", s=25)
	plt.savefig("img/grafica1.png")
	fig.clf()

	fig = plt.figure()
	sns.scatterplot(x='hora', y='durada', data=data, hue=labels, palette="rainbow", s=25)
	plt.savefig("img/grafica2.png")
	fig.clf()

	fig = plt.figure()
	sns.scatterplot(x='hora', y='count', data=data, hue=labels, palette="rainbow", s=25)
	plt.savefig("img/grafica3.png")
	fig.clf()

	fig = plt.figure()
	sns.scatterplot(x='durada', y='count', data=data, hue=labels, palette="rainbow", s=25)
	plt.savefig("img/grafica4.png")
	fig.clf()

# ----------------------------------------------

if __name__ == "__main__":

	logging.basicConfig(format='%(message)s', level=logging.INFO) # canviar entre DEBUG i INFO
	logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR) # per tal de què el matplotlib no vomiti molts missatges

	path_dataset = './data/registre_durada.csv'
	parking_data = load_dataset(path_dataset)

	parking_data = clean(parking_data)

	true_labels = extract_true_labels(parking_data)

	parking_data = parking_data.drop('tipus', axis=1) # eliminem el tipus, ja no interessa
	parking_data_gb = group_by(parking_data)

	scaler = standard_scaler(parking_data_gb)
	# guardem el model de la normalització
	with open('model/scaler.pkl', 'wb') as f:
		pickle.dump(scaler, f)
	parking_data_gb_norm = normalitzacio(parking_data_gb, scaler)

	visualitzar_pairplot(parking_data_gb_norm)

	# clustering amb KMeans
	# seleccionar durada, hora, dia_setmana_dec, count (de fet ho seleccionem tot)
	selected_data = parking_data_gb_norm.iloc[:, 0:4]
	selected_data.to_csv('data/registre_durada_norm.csv', index=False)
	logging.debug('\nDades per l\'entrenament:\n%s\n...', selected_data[:3])

	clustering_model = clustering_kmeans(selected_data, 4)
	# guardem el model
	with open('model/clustering_model.pkl', 'wb') as f:
		pickle.dump(clustering_model, f)
	data_labels = clustering_model.labels_

	logging.info('\nHomogeneity: %.5f', homogeneity_score(true_labels, data_labels))
	logging.info('Completeness: %.5f', completeness_score(true_labels, data_labels))
	logging.info('V-measure: %.5f', v_measure_score(true_labels, data_labels))
	with open('model/scores.pkl', 'wb') as f:
		pickle.dump({
		"h": homogeneity_score(true_labels, data_labels),
		"c": completeness_score(true_labels, data_labels),
		"v": v_measure_score(true_labels, data_labels)
		}, f)

	visualitzar_clusters(selected_data, data_labels)
