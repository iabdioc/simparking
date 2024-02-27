'''
@ IOC - Joan Quintana - 2024 - CE IABD
'''
from json import JSONEncoder
import json

from flask import Flask, request
from flask_selfdoc import Autodoc

import numpy
import pandas as pd

from . import clustering_model, scores, scaler, tipus_dict

class NumpyArrayEncoder(JSONEncoder):
	"""
	Converteix objecte array de numpy a llista, que no hi tindrà problemes per ser convertida a JSON.

	arguments:
		JSONEncoder -- array de numpy

	Returns: llista
	"""
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
auto = Autodoc(app)

@app.after_request
def handle_options(response):
	"""
	Control CORS. Posa la capçalera adequada a la resposta per evitar el CORS.
	"""
	response.headers["Access-Control-Allow-Origin"] = "*"
	response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Requested-With"
	return response

@app.route('/scores')
@auto.doc()
def get_model_scores():
	"""
	Retorna els scores del model

	Example:
	$ curl --request GET 'http://127.0.0.1:5000/scores' --header 'Content-Type: application/json'

	Returns: JSON
	{"h": 0.931366282698716, "c": 0.8958543254055538, "v": 0.9132652173381394}
	"""
	return json.dumps(scores)

@app.route('/scores/h')
@auto.doc()
def get_model_homogeneity():
	"""
	Retorna l'homogeneïtat del model

	Example:
	$ curl --request GET 'http://127.0.0.1:5000/scores/h' --header 'Content-Type: application/text'

	Returns: string
	0.931366282698716
	"""
	return str(scores['h'])

@app.route('/centers')
@auto.doc()
def get_model_centers():
	"""
	Retorna els centroides dels clusters

	Example:
	$ curl --request GET 'http://127.0.0.1:5000/centers' --header 'Content-Type: application/json'

	Returns: JSON
	[[0.2242540209613247, 2.2606465608835116, 1.596285207559031, 0.6122960306889422], [0.2682463031764706, -0.40933210267036024, 1.616786643352545, -0.13234769611396516], [2.740392013529282, -0.9534183673924265, -1.129679028834299, 2.679694638003091], [-0.48403306692212505, -0.14317158601961397, -0.3566550708444334, -0.46782453313730643]]
	"""
	encodedNumpyData = json.dumps(clustering_model.cluster_centers_, cls=NumpyArrayEncoder)

	return encodedNumpyData

@app.route('/prediccio', methods=['POST'])
@auto.doc()
def fer_prediccio():
	"""
	Fa una predicció de tipus de clúster a partir d'un registre d'entrades de cotxe

	Example:
	$ curl -X POST -H "Content-Type: application/json" -d '{
	"matricula": "6897 JWK",
	"registres": "12195,12.2,6.5;11881, 11.2, 6.5;12885, 11.5, 6.5;10549, 11.1, 6.5;2359, 11.6, 6.5"
	}' http://localhost:5000/prediccio

	Returns: JSON
	{
		"matricula": "6897 JWK",
		"tipus": "tipus II"
	}
	"""
	data = request.get_json()

	matricula = data["matricula"]
	registres = data["registres"]

	lst = registres.split(";")

	for i, ele in enumerate(lst):
		lst[i] = ele.split(",")

	registres = [list(map(float, i)) for i in lst]
	registres = [[matricula] + x for x in registres]
	prediccio = nova_prediccio(registres, scaler, clustering_model)[1]
	return {"matricula": matricula, "tipus":tipus_dict[prediccio[0]]['name']}

# This route generates HTML of documentation
@app.route('/documentation')
def documentation():
	"""
	documentation
	"""
	return auto.html()
