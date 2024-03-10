""" @ IOC - Joan Quintana - 2024 - CE IABD """
import logging
import pickle
import shutil
import mlflow
from mlflow.tracking import MlflowClient

from sklearnmlflow import load_dataset, clean, extract_true_labels, group_by, normalitzacio, clustering_kmeans, homogeneity_score, completeness_score, v_measure_score

if __name__ == "__main__":

	logging.basicConfig(format='%(message)s', level=logging.INFO) # canviar entre DEBUG i INFO

	client = MlflowClient()
	experiment_name = "max_iter-tol sklearn simparking"
	exp = client.get_experiment_by_name(experiment_name)

	if not exp:
		mlflow.create_experiment(experiment_name,
			tags={'mlflow.note.content':'simparking variació de paràmetres max_iter i tol'})
		mlflow.set_experiment_tag("version", "1.0")
		mlflow.set_experiment_tag("scikit-learn", "max_iter, tol")
		exp = client.get_experiment_by_name(experiment_name)

	mlflow.set_experiment("max_iter-tol sklearn simparking")

	def get_run_dir(artifacts_uri):
		""" retorna ruta del run """
		return artifacts_uri[7:-10]

	def remove_run_dir(run_dir):
		""" elimina path amb shutil.rmtree """
		shutil.rmtree(run_dir, ignore_errors=True)

	runs = MlflowClient().search_runs(
		experiment_ids=[exp.experiment_id],
	)

	#esborrem tots els runs de l'experiment
	for run in runs:
		mlflow.delete_run(run.info.run_id)
		remove_run_dir(get_run_dir(run.info.artifact_uri))

	path_dataset = './data/registre_durada.csv'
	parking_data = load_dataset(path_dataset)
	parking_data = clean(parking_data)
	true_labels = extract_true_labels(parking_data)
	parking_data = parking_data.drop('tipus', axis=1)
	parking_data_gb = group_by(parking_data)
	with open('model/scaler.pkl', 'rb') as f:
		scaler = pickle.load(f)
	parking_data_gb_norm = normalitzacio(parking_data_gb, scaler)

	K = 4
	max_iters = [1, 10, 50, 80, 120, 200, 300]
	tols = [1e-1, 1e-2, 1e-3, 1e-4]

	for max_iter in max_iters:
		for tol in tols:
			dataset = mlflow.data.from_pandas(parking_data, source=path_dataset)

			mlflow.start_run(description='max_iter={}, tol={}, per a K={}'.format(max_iter, tol, K))
			mlflow.log_input(dataset, context='training')

			clustering_model = clustering_kmeans(parking_data_gb_norm, K, max_iter, tol)
			data_labels = clustering_model.labels_
			h_score = round(homogeneity_score(true_labels, data_labels), 5)
			c_score = round(completeness_score(true_labels, data_labels), 5)
			v_score = round(v_measure_score(true_labels, data_labels), 5)
			logging.info('K: %d, max_iter: %d, tol: %.4f', K, max_iter, tol)
			logging.info('H-measure: %.5f', h_score)
			logging.info('C-measure: %.5f', c_score)
			logging.info('V-measure: %.5f', v_score)

			tags = {
				"engineering": "JQC-IOC",
				"release.candidate": "RC1",
				"release.version": "1.1.2",
			}
			mlflow.set_tags(tags)

			# https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html
			mlflow.log_param("K", K)
			mlflow.log_param("max_iter", max_iter)
			mlflow.log_param("tol", tol)

			mlflow.log_metric("h", h_score)
			mlflow.log_metric("c", c_score)
			mlflow.log_metric("v_score", v_score)

			mlflow.log_artifact("./data/registre_durada.csv")
			mlflow.log_artifact("./data/registre_durada_norm.csv")
			mlflow.end_run()
