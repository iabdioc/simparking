# Table of contents
1. [simparking](#simparking)
2. [Execució](#run)
3. [Docker](#docker)
3. [Testing](#tests)
4. [Llicència](#licence)

# simparking <a name="simparking"></a>
**simparking** és un projecte de simulació d'entrades i sortides de cotxes en un pàrquing de la ciutat.

Es vol crear dades sintètiques per poder fer un anàlisi de les dades amb IA (bàsicament un problema de clustering).

Consta de dues parts:

- simulaciodades: crea a la carpeta data/ dades simulades. En principi es simulen 4 comportaments de cotxes, que donaran lloc a 4 categories/clústers.
- simulacioparking: és l'aplicatiu des del punt de vista de l'operari del pàrking. Veu com entren i surten els cotxes. Contsta d'una interfície de consola, i d'una interfície gràfica.

Consta també de diferents carpetes i scripts relacionats amb l'anàlisi de les dades i la solució amb IA del problema del clustering.

# Execució <a name="run"></a>

Per instal·lar les dependències del projecte:
<pre>
$ pip install -r requirements.txt
</pre>
<pre>
$ cd simulaciodades
$ python simulaciodades.py
</pre>

<pre>
$ cd simulacioparking
$ python simulacioparking.py [cli | gui]
</pre>
Utilitza l'opció <em>gui</em> per la interfície gràfica (llibreria tkinter).

# Docker <a name="docker"></a>

# Testing <a name="tests"></a>

# Llicència <a name="licence"></a>
Joan Quintana - IOC (2024)
Llicència MIT. LICENCE.txt per més detalls


