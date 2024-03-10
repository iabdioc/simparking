""" @ IOC - Joan Quintana - 2024 - CE IABD """
import logging
import shutil
import mlflow
from mlflow.tracking import MlflowClient

from sklearnmlflow import load_dataset, clean, extract_true_labels, group_by, standard_scaler, normalitzacio, clustering_kmeans, homogeneity_score, completeness_score, v_measure_score

if __name__ == "__main__":

	logging.basicConfig(format='%(message)s', level=logging.INFO) # canviar entre DEBUG i INFO

	client = MlflowClient()
	experiment_name = "flavor sklearn"
	exp = client.get_experiment_by_name(experiment_name)

	if not exp:
		mlflow.create_experiment(experiment_name,
			tags={'mlflow.note.content':'simparking flavor sklearn'})
		mlflow.set_experiment_tag("version", "1.0")
		mlflow.set_experiment_tag("scikit-learn", "K, max_iters, tol")
		exp = client.get_experiment_by_name(experiment_name)

	mlflow.set_experiment("flavor sklearn")

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
		#print(run.info.run_id)
		mlflow.delete_run(run.info.run_id)
		remove_run_dir(get_run_dir(run.info.artifact_uri))

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

	#with mlflow.start_run(description='K={}, max_iters={}, tol={}'.format(K, max_iters, tol)) as run:
	mlflow.start_run(description='K={}, max_iters={}, tol={}'.format(K, max_iters, tol))
	mlflow.log_input(dataset, context='training')

	clustering_model = clustering_kmeans(parking_data_gb_norm, K, max_iters, tol)

	# guardem els models de 2 maneres: amb log_model i amb save_model
	mlflow.sklearn.log_model(scaler, 'data_norm_model')
	mlflow.sklearn.log_model(clustering_model, 'clustering_model')
	# eliminem primer la carpeta, sembla ser que no hi ha opció overwrite
	shutil.rmtree('data_norm_model/', ignore_errors=True)
	shutil.rmtree('clustering_model/', ignore_errors=True)
	mlflow.sklearn.save_model(scaler, path='data_norm_model/')
	mlflow.sklearn.save_model(clustering_model, path='clustering_model/')

	data_labels = clustering_model.labels_

	h_score = round(homogeneity_score(true_labels, data_labels), 5)
	c_score = round(completeness_score(true_labels, data_labels), 5)
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

	mlflow.log_metric("h", h_score)
	mlflow.log_metric("c", c_score)
	mlflow.log_metric("v_score", v_score)

	mlflow.log_artifact("./data/registre_durada.csv")
	mlflow.log_artifact("./data/registre_durada_norm.csv")

	mlflow.end_run()
