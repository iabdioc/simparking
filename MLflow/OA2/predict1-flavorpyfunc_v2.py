""" @ IOC - Joan Quintana - 2024 - CE IABD """
import mlflow
import mlflow.pyfunc

custom_loaded_model = mlflow.pyfunc.load_model("custom_model_v2")

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

print(custom_loaded_model.predict(dades_cotxe))
