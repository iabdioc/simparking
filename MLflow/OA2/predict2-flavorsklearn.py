""" @ IOC - Joan Quintana - 2024 - CE IABD """
import mlflow
from mlflow.tracking import MlflowClient
import pandas as pd

client = MlflowClient()
experiment_name = "flavor sklearn"
exp = client.get_experiment_by_name(experiment_name)
mlflow.set_experiment("flavor sklearn")

runs = MlflowClient().search_runs(experiment_ids=[exp.experiment_id],)
run_id = runs[0].info.run_id

#local_path
clustering_loaded_model = mlflow.sklearn.load_model('clustering_model/')

# durada, hora, dia_setmana_dec, count
data_norm = [
  [2.732830354476496, -0.9207855070928049, -1.1320593348043717, 3.769733523650502],
  [0.26790930806008045, -0.4215349655828905, 1.7062354659081376, -0.19415503682400367],
  [-0.9302374156792241, 0.4369914852445514, -0.47976588389927294, -0.45841427418897074]
]

# convertim a dataframe
df_norm = pd.DataFrame(columns=['durada', 'hora', 'dia_setmana_dec', 'count'], data=data_norm)

print(clustering_loaded_model.predict(df_norm))
