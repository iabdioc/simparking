""" @ IOC - Joan Quintana - 2024 - CE IABD """
# https://stackoverflow.com/questions/74257370/mlflow-pyfunc-load-model-mlflow-pyfunc-save-model-how-to-pass-additional-art
import shutil
import pandas as pd
import mlflow

# dummy data
data = {'col1': [1, 2], 'col2': [3, 4]}
df = pd.DataFrame(data=data)

# create class
class PredictSpeciality(mlflow.pyfunc.PythonModel):
	""" classe PredictSpeciality"""
	def fit(self):
		""" fit method """
		print('fit')
		d = {'mult': 2}
		return d

	def predict(self, context, X, y=None):
		""" predict method """
		print('predict')
		df, d = X
		df['pred'] = df['col1'] * d['mult']
		return df

# create instance of model, return weights dict
m = PredictSpeciality()
d = m.fit()

# create model input for predict function as tuple
model_input = ([df, d])
print(m.predict(None, model_input))

# save and re-load from ML flow
shutil.rmtree("temp_model/", ignore_errors=True)
mlflow.pyfunc.save_model(path="temp_model", python_model=m)

m2 = mlflow.pyfunc.load_model("temp_model")
print(m2.predict(model_input))
