'''
@ IOC - Joan Quintana - 2024 - CE IABD
'''
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

from . import clustering_model, scores, scaler, tipus_dict

import numpy
from json import JSONEncoder
import json
import pandas as pd

class NumpyArrayEncoder(JSONEncoder):
	def default(self, obj):
		if isinstance(obj, numpy.ndarray):
			return obj.tolist()
		return JSONEncoder.default(self, obj)

def nova_prediccio(dades, sc, model):
	"""
	Passem nous valors de registre en el parking, per tal d'assignar aquests valors a un dels 4 clústers

	arguments:
		dades -- array de Python (llista), que segueix l'estructura 'matricula', 'durada', 'hora', 'dia_setmana_dec'

	Returns: (dades agrupades, prediccions del model)
	"""
	df_dades_cotxe = pd.DataFrame(columns=['matricula', 'durada', 'hora', 'dia_setmana_dec'], data=dades)

	df_dades_cotxe_gb = group_by(df_dades_cotxe)
	df_dades_cotxe_gb_norm = normalitzacio(df_dades_cotxe_gb, sc)

	return df_dades_cotxe_gb, model.predict(df_dades_cotxe_gb_norm)

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

	return df_norm

app = Flask(__name__)

@app.after_request
def handle_options(response):
	response.headers["Access-Control-Allow-Origin"] = "*"
	response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Requested-With"
	return response

@app.route('/scores')
def get_model_scores():
	return json.dumps(scores)

@app.route('/centers')
def get_model_centers():
	encodedNumpyData = json.dumps(clustering_model.cluster_centers_, cls=NumpyArrayEncoder)

	return encodedNumpyData

@app.route('/prediccio', methods=['POST'])
def fer_prediccio():
	data = request.get_json()

	matricula = data["matricula"]
	registres = data["registres"]

	lst = registres.split(";")

	for i, ele in enumerate(lst):
		lst[i] = ele.split(",")

	registres = [list( map(float,i) ) for i in lst]
	registres = [[matricula] + x for x in registres]
	prediccio = nova_prediccio(registres, scaler, clustering_model)[1]
	return {"matricula": matricula, "tipus":tipus_dict[prediccio[0]]['name']}
