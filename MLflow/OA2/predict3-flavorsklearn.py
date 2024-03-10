""" @ IOC - Joan Quintana - 2024 - CE IABD """
import mlflow
from mlflow.tracking import MlflowClient
import pandas as pd

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

def nova_prediccio(dades, sc, model):
	"""
	Passem nous valors de registre en el parking, per tal d'assignar aquests valors a un dels 4 clústers

	arguments:
		dades -- array de Python (llista), que segueix l'estructura 'matricula', 'durada', 'hora', 'dia_setmana_dec'
		sc -- scaler model
		model -- clustering model

	Returns: (dades agrupades, prediccions del model)
	"""
	df_dades_cotxe = pd.DataFrame(columns=['matricula', 'durada', 'hora', 'dia_setmana_dec'], data=dades)

	df_dades_cotxe_gb = group_by(df_dades_cotxe)
	df_dades_cotxe_gb_norm = normalitzacio(df_dades_cotxe_gb, sc)

	return model.predict(df_dades_cotxe_gb_norm)

if __name__ == "__main__":

	client = MlflowClient()
	experiment_name = "flavor sklearn"
	exp = client.get_experiment_by_name(experiment_name)
	mlflow.set_experiment("flavor sklearn")

	runs = MlflowClient().search_runs(experiment_ids=[exp.experiment_id],)
	run_id = runs[0].info.run_id

	data_norm_logged_model = f'runs:/{run_id}/data_norm_model'
	clustering_logged_model = f'runs:/{run_id}/clustering_model'

	# Load model as a PyFuncModel.
	data_norm_loaded_model = mlflow.sklearn.load_model(data_norm_logged_model)
	clustering_loaded_model = mlflow.sklearn.load_model(clustering_logged_model)

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
	]*2

	print(nova_prediccio(dades_cotxe, data_norm_loaded_model, clustering_loaded_model))
