'''
@ IOC - Joan Quintana - 2024 - CE IABD
'''
import pickle

from sklearn import preprocessing
from sklearn.cluster import KMeans

with open("clusteringsklearn/model/scores.pkl", "rb") as f:
	scores = pickle.load(f)

with open("clusteringsklearn/model/scaler.pkl", "rb") as f:
	scaler = pickle.load(f)

with open("clusteringsklearn/model/clustering_model.pkl", "rb") as f:
	clustering_model = pickle.load(f)

with open("clusteringsklearn/model/tipus_dict.pkl", "rb") as f:
	tipus_dict = pickle.load(f)
