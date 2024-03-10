""" @ IOC - Joan Quintana - 2024 - CE IABD """
import logging
import pickle
import shutil
import mlflow
import mlflow.pyfunc
import pandas as pd
from sklearnmlflow import load_dataset, clean, extract_true_labels, group_by, standard_scaler, normalitzacio, clustering_kmeans, v_measure_score

# Define the model class
class CustomPredict_v2(mlflow.pyfunc.PythonModel):
	""" classe CustomPredict_v2 """
	def preprocessar(self, input, sc):
		""" preprocessar: retorna dades agrupades i normalitzades """
		df_dades_cotxe = pd.DataFrame(columns=['matricula', 'durada', 'hora', 'dia_setmana_dec'], data=input)
		df_dades_cotxe_gb = group_by(df_dades_cotxe)
		df_dades_cotxe_gb_norm = normalitzacio(df_dades_cotxe_gb, sc)
		return df_dades_cotxe_gb_norm

	# Evaluate input using custom_function()
	def predict(self, context, model_input, params=None):
		"""
		This is an abstract function. We customized it into a method to fetch the FastText model.
		Args:
			context ([type]): MLflow context where the model artifact is stored.
			model_input ([type]): the input data to fit into the model.
		Returns:
			[type]: the loaded model artifact.
		"""
		with open(context.artifacts['scaler'], 'rb') as f:
			sc = pickle.load(f)
		with open(context.artifacts['clustering_model'], 'rb') as f:
			cm = pickle.load(f)

		df_dades_cotxe_gb_norm = self.preprocessar(model_input, sc)

		return cm.predict(df_dades_cotxe_gb_norm)

if __name__ == "__main__":

	logging.basicConfig(format='%(message)s', level=logging.INFO) # canviar entre DEBUG i INFO

	path_dataset = './data/registre_durada.csv'
	parking_data = load_dataset(path_dataset)
	parking_data = clean(parking_data)
	true_labels = extract_true_labels(parking_data)
	parking_data = parking_data.drop('tipus', axis=1)
	parking_data_gb = group_by(parking_data)
	scaler = standard_scaler(parking_data_gb)
	parking_data_gb_norm = normalitzacio(parking_data_gb, scaler)

	K = 4
	max_iters = 300
	tol = 1e-4

	dataset = mlflow.data.from_pandas(parking_data_gb_norm, source=path_dataset)

	mlflow.log_input(dataset, context='training')

	clustering_model = clustering_kmeans(parking_data_gb_norm, K, max_iters, tol)

	artifacts = {
		"dades": "./data/registre_durada.csv",
		"dades_norm": "./data/registre_durada_norm.csv",
		"scaler": "model/scaler.pkl",
		"clustering_model": "model/clustering_model.pkl"
	}

	m = CustomPredict_v2()

	model_name = 'custom_model_v2'
	shutil.rmtree(model_name, ignore_errors=True)
	mlflow.pyfunc.save_model(
		path=model_name,
		python_model=m,
		artifacts=artifacts,
	)

	data_labels = clustering_model.labels_

	v_score = round(v_measure_score(true_labels, data_labels), 5)

	logging.info('K: %d, max_iters: %d, tol: %d', K, max_iters, tol)
	logging.info('V-measure: %.5f', v_score)

	tags = {
		"engineering": "JQC-IOC",
		"release.version": "1.1",
	}
	mlflow.set_tags(tags)

	mlflow.log_param("K", K)
	mlflow.log_param("max_iters", max_iters)
	mlflow.log_param("tol", tol)

	mlflow.log_metric("v_score", v_score)
