""" @ IOC - Joan Quintana - 2024 - CE IABD """
import logging
import pickle
import shutil
import mlflow
import mlflow.pyfunc
from mlflow.tracking import MlflowClient
from sklearnmlflow import load_dataset, clean, extract_true_labels, group_by, standard_scaler, normalitzacio, clustering_kmeans, v_measure_score

# Define the model class
class CustomPredict(mlflow.pyfunc.PythonModel):
	""" classe CustomPredict"""
	# Load artifacts
	def load_context(self, context):
		"""
		This method is called when loading an MLflow model with pyfunc.load_model(), as soon as the Python Model is constructed.
		Args:
			context: MLflow context where the model artifact is stored.
		"""

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
		with open(context.artifacts['clustering_model'], 'rb') as f:
			cm = pickle.load(f)

		return cm.predict(model_input)

if __name__ == "__main__":

	logging.basicConfig(format='%(message)s', level=logging.INFO) # canviar entre DEBUG i INFO

	client = MlflowClient()
	experiment_name = "flavor pyfunc"
	exp = client.get_experiment_by_name(experiment_name)

	if not exp:
		mlflow.create_experiment(experiment_name,
			tags={'mlflow.note.content':'simparking flavor pyfunc'})
		mlflow.set_experiment_tag("version", "1.0")
		mlflow.set_experiment_tag("scikit-learn", "K, max_iters, tol")
		exp = client.get_experiment_by_name(experiment_name)

	mlflow.set_experiment("flavor pyfunc")

	runs = MlflowClient().search_runs(
		experiment_ids=[exp.experiment_id],
	)

	def get_run_dir(artifacts_uri):
		""" retorna ruta del run """
		return artifacts_uri[7:-10]

	def remove_run_dir(run_dir):
		""" elimina path amb shutil.rmtree """
		shutil.rmtree(run_dir, ignore_errors=True)

	for run in runs:
		mlflow.delete_run(run.info.run_id)
		remove_run_dir(get_run_dir(run.info.artifact_uri))

	path_dataset = './data/registre_durada.csv'
	parking_data = load_dataset(path_dataset)
	parking_data = clean(parking_data)
	true_labels = extract_true_labels(parking_data)
	parking_data = parking_data.drop('tipus', axis=1)
	parking_data_gb = group_by(parking_data)
	scaler = standard_scaler(parking_data_gb)
	# guardem el model de la normalització
	with open('model/scaler.pkl', 'wb') as f:
		pickle.dump(scaler, f)
	parking_data_gb_norm = normalitzacio(parking_data_gb, scaler)

	K = 4
	max_iters = 300
	tol = 1e-4

	dataset = mlflow.data.from_pandas(parking_data_gb_norm, source=path_dataset)

	mlflow.start_run(description='K={}, max_iters={}, tol={}'.format(K, max_iters, tol))
	mlflow.log_input(dataset, context='training')

	clustering_model = clustering_kmeans(parking_data_gb_norm, K, max_iters, tol)
	with open('model/clustering_model.pkl', 'wb') as f:
		pickle.dump(clustering_model, f)

	artifacts = {
		"dades": "./data/registre_durada.csv",
		"dades_norm": "./data/registre_durada_norm.csv",
		"scaler": "model/scaler.pkl",
		"clustering_model": "model/clustering_model.pkl"
	}

	model_name = 'custom_model'
	mlflow.pyfunc.log_model(
		artifact_path=model_name,
		python_model=CustomPredict(),
		artifacts=artifacts,
	)
	# o bé:
	#shutil.rmtree(model_name, ignore_errors=True)
	#mlflow.pyfunc.save_model(
	#	path=model_name,
	#	python_model=CustomPredict(),
	#	artifacts=artifacts,
	#)

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

	mlflow.end_run()
