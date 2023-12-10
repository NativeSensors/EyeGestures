from sklearn.cluster import DBSCAN
import numpy as np
import time  
X = np.array([[1, 2], [2, 2], [2, 3], [8, 7], [8, 8], [25, 80], [8, 20], [8, 21]])

Dbscan = DBSCAN(eps=3, min_samples=2)

start = time.time()
clustering = Dbscan.fit(X)
print(clustering.labels_, time.time() - start)


X = np.array([[8, 7], [8, 8], [25, 80], [8, 20], [8, 21], [1, 2], [2, 2], [2, 3]])
start = time.time()
clustering = Dbscan.fit_predict(X)
print(clustering.labels_, time.time() - start)
