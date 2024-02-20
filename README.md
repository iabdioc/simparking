# Table of contents
1. [simparking](#simparking)
2. [Execució](#run)
3. [Docker](#docker)
3. [Testing](#tests)
4. [Llicència](#licence)

# simparking <a name="simparking"></a>
**simparking** és un projecte de simulació d'entrades i sortides de cotxes en un pàrquing de la ciutat.

ENG: This is a Python project that simulates a parking car activity. 4 behaviour patterns have been coded.
The ultimate goal is to train a KMeans clustering algorythm to discover the four patterns.

Es vol crear dades sintètiques per poder fer un anàlisi de les dades amb IA (bàsicament un problema de clustering).

Consta de dues parts:

- simulaciodades: crea a la carpeta data/ dades simulades. En principi es simulen 4 comportaments de cotxes, que donaran lloc a 4 categories/clústers.
- simulacioparking: és l'aplicatiu des del punt de vista de l'operari del pàrking. Veu com entren i surten els cotxes. Contsta d'una interfície de consola, i d'una interfície gràfica.

Consta també de diferents carpetes i scripts relacionats amb l'anàlisi de les dades i la solució amb IA del problema del clustering.

# Execució <a name="run"></a>

Pots crear un entorn virtual fent:
```
$ python -m venv venv
 o bé:
$ virtualenv venv

$ source venv/bin/activate
```

i tot seguit instal·lar els mòduls necessaris:
```
$ pip install -r requirements.txt
```

Per executar:
```
$ cd simulaciodades
$ python simulaciodades.py
```

```
$ cd simulacioparking
$ python simulacioparking.py [cli | gui]
```
Utilitza l'opció <em>gui</em> per la interfície gràfica (llibreria tkinter).

# Docker <a name="docker"></a>

```
Descarrega:
$ docker pull iabdioc/simparking:latest

Crea i arrenca el contenidor:
$ docker run --name simparking -dit -p 8888:8888 iabdioc/simparking:latest /bin/sh

Accedir al contenidor
$ docker exec -it simparking /bin/bash

Dins del contenidor pots arrencar el servidor web de Jupyter:
$ arrencar_jupyter.sh

Pots testejar un quadern de Jupyter a:
simparking/clusteringsklearn/jupyter/clusteringsklearn.ipynb
```

# Testing <a name="tests"></a>

Des de l'arrel del projecte:
```
$ python -m unittest discover -s tests
```

# Llicència <a name="licence"></a>
Joan Quintana - IOC (2024)
Llicència MIT. [LICENSE.txt](LICENSE.txt) per més detalls


