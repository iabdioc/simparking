""" @ IOC - Joan Quintana - 2024 - CE IABD """
import mlflow

v_score_filter = "metrics.v_score > 0.40"

dfres = mlflow.search_runs(experiment_names=["K sklearn simparking"],
  filter_string=v_score_filter,
  order_by=["metrics.v_score DESC"])

print(dfres[['metrics.v_score', 'params.K', 'tags.mlflow.runName', 'tags.mlflow.note.content']])
