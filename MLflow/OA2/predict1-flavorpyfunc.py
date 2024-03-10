""" @ IOC - Joan Quintana - 2024 - CE IABD """
import mlflow
import mlflow.pyfunc
from mlflow.tracking import MlflowClient
import pandas as pd

client = MlflowClient()
experiment_name = "flavor pyfunc"
exp = client.get_experiment_by_name(experiment_name)
mlflow.set_experiment("flavor pyfunc")

runs = MlflowClient().search_runs(experiment_ids=[exp.experiment_id],)
run_id = runs[0].info.run_id
print(run_id)

custom_loaded_model = mlflow.pyfunc.load_model(f'runs:/{run_id}/custom_model')
# o bé
#custom_loaded_model = mlflow.pyfunc.load_model("custom_model")

# durada, hora, dia_setmana_dec, count
data_norm = [
	[2.732830354476496, -0.9207855070928049, -1.1320593348043717, 3.769733523650502],
	[0.26790930806008045, -0.4215349655828905, 1.7062354659081376, -0.19415503682400367],
	[-0.9302374156792241, 0.4369914852445514, -0.47976588389927294, -0.45841427418897074]
]

# convertim a dataframe
df_norm = pd.DataFrame(columns=['durada', 'hora', 'dia_setmana_dec', 'count'], data=data_norm)
print(custom_loaded_model.predict(data_norm))
