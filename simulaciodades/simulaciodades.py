'''
@ IOC - Joan Quintana - 2024 - CE IABD
'''

from utils.customformatter import CustomFormatter

from datetime import datetime, timedelta
import random
import string
import logging
import numpy as np

from PIL import Image, ImageDraw, ImageFont, ImageFilter

#logger = logging.getlogger(__name__)
logger = logging.getLogger("simulaciodades")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG) # canviar a DEBUG mentre es programa
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

def generar_matricules(num=1000, str_fitxer='data/matricules.txt'):
	"""
	Genera el fitxer de matrícules amb el format EE (9999 XXX)

	arguments:
		num (int) -- número de matrícules a generar
		str_fitxer (str) -- el fitxer a generar

	Returns:
		None
	"""
	fout = open(str_fitxer, "w")

	for _ in range(num):
		majuscules = string.ascii_letters[26:52]
		mat = ''
		for _ in range(4):
			mat += str(random.randint(0, 9))

		mat += ' '

		for _ in range(3):
			mat += majuscules[random.randint(0, len(majuscules)-1)]

		fout.write(mat + '\n')

	fout.close()

def generar_matricules_png(fitxer_matricules, bool_imgfons=True, directori='matricules/'):
	"""
	Genera les imatges de les matrícules contingudes en el fitxer. Simula una placa real, afegint soroll i una certa distorsió

	arguments:
		fitxer_matricules -- fitxer de matrícules
		bool_imgfons -- inclou o no la imatge de fons que està a matricules/frontal/frontal.png
		directori -- directori destí

	Returns: None
	"""
	logger.info('Generant els png de les matrícules...')
	if bool_imgfons:
		frontal = Image.open(directori + "frontal/frontal.png")

	f = open(fitxer_matricules, 'r')
	matricules = f.readlines()

	for matricula in matricules:
		matricula = matricula.rstrip('\n')
		# Create white canvas and get drawing context
		w, h = 300, 50 # marc de la matrícula
		img = Image.new('RGB', (w, h), color='white')
		draw = ImageDraw.Draw(img)

		color = random.randint(10, 245)

		# Draw a random number of circles between 40-120
		cmin = random.randint(50, 70)
		cmax = random.randint(90, 120)
		for _ in range(cmin, cmax):
			# Choose RGB values for this circle, somewhat close (+/-10) to basic RGB
			r = color + random.randint(-10, 10)
			g = color + random.randint(-10, 10)
			b = color + random.randint(-10, 10)
			diam = random.randint(5, 11)
			x, y = random.randint(0, w), random.randint(0, h)
			draw.ellipse([x, y, x+diam, y+diam], fill=(r, g, b))

		# Blur the background a bit
		mat = img.filter(ImageFilter.BoxBlur(5))

		# Load font and draw text
		draw = ImageDraw.Draw(mat)
		fnt = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 42)
		draw.text((62, 5), matricula, font=fnt, fill=(0, 0, 0))

		#angle = random.randint(-10, 10)
		#mat = mat.rotate(angle, Image.NEAREST, expand=1)

		# imatge principal
		wimg, himg = 450, 200
		img = Image.new("RGB", (wimg, himg))

		if bool_imgfons:
			img.paste(frontal, (0, 0))

		img.paste(mat, (75, 75))
		# img.show()
		img.save(directori + matricula.replace(' ', '-') + ".png")
	f.close()



def generar_caps_de_setmana(dia_i, dia_f):
	"""
	Genera un array de dates entre dia_inici i dia_fi,
	corresponent als dissabtes i diumenges

	arguments:
		dia_i -- dia inicial
		dia_f -- dia final

	Returns:
	array
	"""
	lst_dies = []
	dia = dia_i

	while dia < dia_f:
		if (dia.weekday() == 5 or dia.weekday() == 6): # dissabte o diumenge
			lst_dies.append(dia)
		dia = dia + timedelta(days=1)
	return lst_dies

def generar_diumenges(dia_i, dia_f):
	"""
	Genera un array de dates entre dia_inici i dia_fi,
	corresponent als diumenges

	arguments:
		dia_i -- dia inicial
		dia_f -- dia final

	Returns:
	array
	"""
	lst_dies = []
	dia = dia_i

	while dia < dia_f:
		if dia.weekday() == 6: # diumenge
			lst_dies.append(dia)
		dia = dia + timedelta(days=1)
	return lst_dies

def generar_feiners(dia_i, dia_f):
	"""
	Genera un array de dates entre dia_inici i dia_fi,
	corresponent als dies feiners (dilluns-divendres)

	arguments:
		dia_i -- dia inicial
		dia_f -- dia final

	Returns:
	array
	"""
	dia = dia_i
	lst_dies = []

	while dia < dia_f:
		if dia.weekday() >= 0 and dia.weekday() <= 4: # dilluns a divendres
			lst_dies.append(dia)
		dia = dia + timedelta(days=1)
	return lst_dies

def generar_dies_tots(dia_i, dia_f):
	"""
	Genera un array de dates entre dia_inici i dia_fi,
	corresponent a tots els dies

	arguments:
		dia_i -- dia inicial
		dia_f -- dia final

	Returns:
	array
	"""
	dia = dia_i
	lst_dies = []

	while dia < dia_f:
		lst_dies.append(dia)
		dia = dia + timedelta(days=1)
	return lst_dies

def generar_dades_tipus(arr_cotxes, dicc_, dies_, fout=None, fout_d=None):
	"""
	Simulació: Genera un array de dates entre dia_inici i dia_fi per a cadascun dels cotxes de l'array,
	i els escriu als dos fitxers

	arguments:
		arr_cotxes -- arr de matrícules de cotxes
		dicc_ -- el diccionari amb les especificacions de com s'ha d'omplir la simulació
		dies_ -- llista de dies que seran assignats
		foutput -- fitxer d'escriptura del registre d'entrades i sortides al parking
		foutput_d -- fitxer d'escriptura del registre d'entrades, amb la durada de l'estacionament al parking

	Returns:
		tuple -- tuple of arrays. Tupla amb els registres dels cotxes (format E/S, i format durada)
		Com a resultat hem escrit en els fitxers data/registre.csv i data/registre_durada.csv
	"""
	arr_reg_ES = []
	arr_reg_durada = []

	for cotxe in arr_cotxes:
		logger.info('---------------')
		logger.info('%s', cotxe)
		# s'utilitza el parking entre un 20% i un 50% dels dies, per ex
		num_dies = int(((dicc_['perc'][0] + random.random()*(dicc_['perc'][1]-dicc_['perc'][0]))*len(dies_))/100)

		# he d'escollir de forma aleatòria els dies que utilitzen el pkg
		compt = num_dies
		lst = []

		while compt > 0:
			val = random.randint(0, len(dies_)-1)
			if val not in lst:
				lst.append(val)
				compt -= 1
		# dies que s'utilitza el parking:
		dies_pkg_entrada = []
		dies_pkg_sortida = []
		for i in lst:
			dies_pkg_entrada.append(dies_[i])
		for i in range(len(lst)):
			# ja tenim els dies del parking. Ara necessitem una hora d'entrada i una hora de sortida
			dies_pkg_entrada[i] = dies_pkg_entrada[i] + timedelta(hours=dicc_['mu_t'])
			ts_dia_inici = int(dies_pkg_entrada[i].timestamp())
			mu = ts_dia_inici
			sigma = dicc_['s_t']*3600 # 1 hores
			ts_dia_inici = int(np.random.normal(mu, sigma))
			dies_pkg_entrada[i] = datetime.fromtimestamp(ts_dia_inici)

			# durada
			mu_durada = dicc_['mu_d']*3600 # segons durada
			sigma_durada = dicc_['s_d']*3600 # desviació típica
			durada = int(np.random.normal(mu_durada, sigma_durada))
			if durada < 0: # pot donar-se el cas perquè són distribucions normals
				durada = mu_durada

			ts_dia_fi = ts_dia_inici + durada
			dies_pkg_sortida.append(datetime.fromtimestamp(ts_dia_fi))

		logger.info('%s', dies_pkg_entrada[0])
		logger.info('%s', dies_pkg_sortida[0])
		logger.info('...')

		# escriure a fitxer
		for i in range(len(lst)):
			logger.debug('%s', cotxe)
			logger.debug('%s', dies_pkg_entrada[i])
			durada = int((dies_pkg_sortida[i] - dies_pkg_entrada[i]).total_seconds())
			dia_setmana = dies_pkg_entrada[i].weekday()
			hora = round(dies_pkg_entrada[i].hour + dies_pkg_entrada[i].minute/60 + dies_pkg_entrada[i].second/3600, 1)
			dia_setmana_dec = round(dia_setmana + hora/24, 1)
			if fout and fout_d:
				fout.write("{};E;{};{}\n".format(cotxe, dies_pkg_entrada[i], dies_pkg_entrada[i].weekday()))
				fout.write("{};S;{};{}\n".format(cotxe, dies_pkg_sortida[i], dies_pkg_entrada[i].weekday()))
				fout_d.write("{};{};{};{};{};{}\n".format(cotxe, dies_pkg_entrada[i], durada, hora, dia_setmana, dia_setmana_dec))
			arr_reg_ES.append([cotxe, 'E', dies_pkg_entrada[i], dies_pkg_entrada[i].weekday()])
			arr_reg_ES.append([cotxe, 'S', dies_pkg_sortida[i], dies_pkg_entrada[i].weekday()])
			arr_reg_durada.append([cotxe, durada, hora, dia_setmana_dec])
	return arr_reg_ES, arr_reg_durada

# ----------------------------------------------

if __name__ == "__main__":

	random.seed(10) # reproduir els resultats
	np.random.seed(10)

	str_matricules = 'data/matricules.txt'
	generar_matricules(1000) # 1000 matrícules (cotxes)
	generar_matricules_png(str_matricules)

	dia_inici = datetime(2023, 1, 1, 0, 0, 0)
	dia_fi = datetime(2023, 12, 31, 23, 59, 59)

	dicc = [
		{"name":"tipus I", "proporcio":.1, "perc": [20, 50], "mu_t": 21, "s_t": 1, "mu_d": 3, "s_d": 1},
		{"name":"tipus II", "proporcio":.1, "perc": [20, 50], "mu_t": 11, "s_t": 1, "mu_d": 3, "s_d": 1},
		{"name":"tipus III", "proporcio":.1, "perc": [20, 50], "mu_t": 9, "s_t": 1, "mu_d": 6, "s_d": 1},
		{"name":"tipus IV", "proporcio":.7, "perc": [1, 3], "mu_t": 12, "s_t": 8, "mu_d": 2, "s_d": 1}
	]

	f = open(str_matricules, 'r')
	matricules = f.readlines()
	f.close()

	count = 0
	cotxes_tipus_I = []
	cotxes_tipus_II = []
	cotxes_tipus_III = []
	cotxes_tipus_IV = []
	
	# assignació de cotxes a tipologia
	for mat in matricules:
		mat = mat.strip()

		if count <= int(dicc[0]['proporcio']*len(matricules)):
			cotxes_tipus_I.append(mat)
		elif count <= int((dicc[0]['proporcio'] + dicc[1]['proporcio'])*len(matricules)):
			cotxes_tipus_II.append(mat)
		elif count <= int((dicc[0]['proporcio'] + dicc[1]['proporcio'] + dicc[2]['proporcio'])*len(matricules)):
			cotxes_tipus_III.append(mat)
		else:
			cotxes_tipus_IV.append(mat)

		count += 1
	
	cotxes_tipus = [cotxes_tipus_I, cotxes_tipus_II, cotxes_tipus_III, cotxes_tipus_IV]

	dies = []
	dies.append(generar_caps_de_setmana(dia_inici, dia_fi))
	dies.append(generar_diumenges(dia_inici, dia_fi))
	dies.append(generar_feiners(dia_inici, dia_fi))
	dies.append(generar_dies_tots(dia_inici, dia_fi))

	foutput = open("data/registre.csv", "w")
	foutput_d = open("data/registre_durada.csv", "w")

	foutput.write("matricula;ES;dia_hora;dia_setmana\n")
	foutput_d.write("matricula;dia_hora;durada;hora;dia_setmana;dia_setmana_dec\n")

	arr_cotxes = []
	for i in range(len(cotxes_tipus)):
		arr_cotxes.append(generar_dades_tipus(cotxes_tipus[i], dicc[i], dies[i], foutput, foutput_d))

	foutput.close()
	foutput_d.close()

	logger.info("\ns'ha generat data/registre.csv i data/registre_durada.csv")
