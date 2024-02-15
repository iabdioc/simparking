'''
@ IOC - Joan Quintana - 2024 - CE IABD
'''

from utils.customformatter import CustomFormatter

import os
import sys
import re
import itertools
from datetime import datetime, timedelta
from threading import Timer
from threading import Thread # GUI
import signal
import logging

from tkinter import Tk, Label, Button # GUI
from PIL import Image
from PIL import ImageTk # GUI
import cv2
import imutils
import numpy as np
import pytesseract

from time import sleep

# els directoris simulacioparking i simulaciodades estan al mateix nivell.
# Així és com ho fem per importar un paquet que està al mateix nivell
sys.path.append("..")
from simulaciodades.simulaciodades import generar_caps_de_setmana, generar_diumenges, generar_feiners, generar_dies_tots, generar_dades_tipus

#logger = logging.getLogger(__name__)
logger = logging.getLogger("simulacioparking")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG) # canviar a DEBUG mentre es programa
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

# resolució temporal
# T1: salts de temps (temps d'ordinador, segons, decimal)
# T2: salt de temps (temps real, minuts)
# T1 segons de l'ordinador = T2*60 segons de temps real
# factor: T2*60/T1 = 15*60 = 900 (el temps passa a una velocitat de 900)
# per exemple, T1=1.0, T2=60 -> T2*60/T1 = 60*60/1 = 3600 (el temps passa a una velocitat de 3600)
T1 = 1.0
T2 = 60

def signal_handler(sig, frame):
	"""
	Captura Ctrl-C per acabar el programa de forma ordenada

	Returns: None
	"""
	global foutput
	foutput.close()
	sys.exit(0)

def ocr(fitxer):
	"""
	OCR: Optical Character Recognition per detectar els caràcters de les matrícules.
	S'utilitza la llibreria pytesseract, però hi ha altres possibilitats.

	arguments:
		fitxer -- imatge que conté la captura de la matrícula (les matrícules estan a ../simulaciodades/matricules)

	Returns:
		string -- la cadena que conté la matrícula detectada (o cadena buida si no l'ha trobat)
	"""
	txt_matricula = ""

	img = cv2.imread(fitxer, cv2.IMREAD_COLOR)
	img = cv2.resize(img, (450, 200)) # tamany original de les matrícules

	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #convert to grey scale
	gray = cv2.bilateralFilter(gray, 11, 17, 17) #Blur to reduce noise
	edged = cv2.Canny(gray, 30, 200) #Perform Edge detection

	try:
		os.makedirs(os.path.dirname('img/'))
	except FileExistsError:
		pass

	cv2.imwrite("img/edged.png", edged)

	# find contours in the edged image, keep only the largest ones, and initialize our screen contour
	cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:10]
	screenCnt = None

	# loop over our contours
	for c in cnts:
		# approximate the contour
		peri = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, 0.018 * peri, True)

		# if our approximated contour has four points, then
		# we can assume that we have found our screen
		if len(approx) == 4:
			screenCnt = approx
			break

	if screenCnt is None:
		logger.debug('No contour detected')
	else:
		cv2.drawContours(img, [screenCnt], -1, (0, 255, 0), 3)

		# Masking the part other than the number plate
		mask = np.zeros(gray.shape, np.uint8)
		cv2.drawContours(mask, [screenCnt], 0, 255, -1)

		# Now crop
		(x, y) = np.where(mask == 255)
		(topx, topy) = (np.min(x), np.min(y))
		(bottomx, bottomy) = (np.max(x), np.max(y))
		cropped = gray[topx:bottomx+1, topy:bottomy+1]
		cv2.imwrite("img/cropped.png", cropped)

		#Read the number plate
		try:
			txt_matricula = pytesseract.image_to_string(cropped, config='--psm 3') # --psm 11
			txt_matricula = txt_matricula.replace('\n', '').replace(' ', '').strip()
			txt_matricula = re.sub('[^A-Za-z0-9]+', '', txt_matricula) # eliminar caràcters especials
			txt_matricula = re.sub(r'(\d{4})', r'\1 ', txt_matricula) # posem un espai en blanc entre el grup de números i el grup de lletres
		except Exception as e:
			logger.debug('Exception: %s', e)

	return txt_matricula

def processar_timer_cli(t, fout): # pragma: no cover
	"""
	Donat un intèrval de temps, cerca dins de l'array de simulació tots els cotxes que entren o surten en aquest intèrval.

	arguments:
		t -- timestamp
		fout -- fitxer d'escriptura

	Returns:
		arr -- array d'entrades i sortides futures (ja hem eliminat els que han entrat i sortit)
	"""

	# utilitzem la variable global (que no és l'opció més elegant), perquè aquesta funció la crida el Timer,
	# i retornar un valor (l'array actualitzat) passa a ser molt complicat (https://stackoverflow.com/questions/25189389/python-how-to-get-the-output-of-the-function-used-in-timer)
	global arr_cotxes_ordenats
	str_t = t.strftime("%d-%m-%Y %H:%M:%S")
	logger.info("timer: %s", str_t)
	# imprimir tots els cotxes que han d'actuar
	while arr_cotxes_ordenats[0][3].timestamp() < t.timestamp():
		matricula = arr_cotxes_ordenats[0][0]
		logger.info("%s", matricula)
		matricula_png = matricula.replace(' ', '-') + '.png'
		logger.debug(arr_cotxes_ordenats[0][3])
		logger.debug(matricula_png)
		txt_matricula = ocr('../simulaciodades/matricules/' + matricula_png)
		logger.info("detectat: %s", txt_matricula)
		try:
			fout.write("{};{};{};{}\n".format(txt_matricula, arr_cotxes_ordenats[0][2], arr_cotxes_ordenats[0][3], arr_cotxes_ordenats[0][3].weekday()))
		except Exception as e:
			logger.debug('Exception: %s (registre no gravat)', e)

		arr_cotxes_ordenats.pop(0)

def processar_temps_gui(self, t1, t2, dia, fout): # pragma: no cover
	"""
	Funció que simula com passa el temps accelerat, i no bloqueja el funcionament del programa

	arguments:
		t1: salts de temps (temps d'ordinador, segons)
		t2: salt de temps (temps real, minuts)
		dia: timestamp (timestamp en la simulació)
		fout: fitxer d'escriptura

	Returns: None
	"""
	while 1:
		# data
		self.lbl_dia = Label(self.root, text=dia.strftime("%d-%m-%Y %H:%M:%S"), font=("Arial", 15), background="#ffe4b4")
		self.lbl_dia.pack()
		self.lbl_dia.place(width=200, height=20, x=450, y=700)

		t = Timer(t1, processar_timer_gui, args=[self, dia, fout])
		t.start()
		t.join()
		dia = dia + timedelta(minutes=t2)

def processar_timer_gui(self, t, fout): # pragma: no cover
	"""
	(versió GUI) Donat un intèrval de temps, cerca dins de l'array de simulació tots els cotxes que entren o surten en aquest intèrval.

	arguments:
		t -- timestamp
		fout -- fitxer d'escriptura

	Returns:
		arr -- array d'entrades i sortides futures (ja hem eliminat els que han entrat i sortit)
	"""
	global arr_cotxes_ordenats
	str_t = t.strftime("%d-%m-%Y %H:%M:%S")
	logger.info("\ntimer: %s", str_t)
	# imprimir tots els cotxes que han d'actuar
	while arr_cotxes_ordenats[0][3].timestamp() < t.timestamp():
		matricula = arr_cotxes_ordenats[0][0]
		logger.info("%s", matricula)
		matricula_png = matricula.replace(' ', '-') + '.png'
		logger.debug(matricula_png)

		txt_matricula = ocr('../simulaciodades/matricules/' + matricula_png)
		logger.info("detectat: %s", txt_matricula)
		fout.write("{};{};{};{}\n".format(txt_matricula, arr_cotxes_ordenats[0][2], arr_cotxes_ordenats[0][3], arr_cotxes_ordenats[0][3].weekday()))

		# data
		self.lbl_temps = Label(self.root, text=arr_cotxes_ordenats[0][3].strftime("%d-%m-%Y %H:%M:%S"), background='#ffe4b4', font=("Arial", 35))
		self.lbl_temps.pack()
		self.lbl_temps.place(width=450, height=120, x=10, y=120)

		# E/S (entra/surt)
		str_ES = "Entra" if arr_cotxes_ordenats[0][2] == 'E' else "Surt"
		self.lbl_ES = Label(self.root, text=f"{str_ES}", background='#ffe4b4', font=("Arial", 35))
		self.lbl_ES.pack()
		self.lbl_ES.place(width=150, height=90, x=480, y=250)

		# imatge original
		self.img_or = ImageTk.PhotoImage(Image.open('../simulaciodades/matricules/' + matricula_png))
		self.lbl_or = Label(self.root, image=self.img_or, background="#ffe4b4")
		self.lbl_or.pack() # fill = BOTH, expand = 1
		self.lbl_or.place(width=450, height=200, x=10, y=250)

		# imatge edge
		self.img_ed = ImageTk.PhotoImage(Image.open('img/edged.png'))
		self.lbl_ed = Label(self.root, image=self.img_ed, background="#ffe4b4")
		self.lbl_ed.pack()
		self.lbl_ed.place(width=450, height=200, x=10, y=460)

		# imatge cropped
		self.img_cr = ImageTk.PhotoImage(Image.open('img/cropped.png' if txt_matricula != '' else 'img/no_detectat.png'))
		self.lbl_cr = Label(self.root, image=self.img_cr, background="#ffe4b4")
		self.lbl_cr.pack()
		self.lbl_cr.place(width=350, height=75, x=10, y=670)

		arr_cotxes_ordenats.pop(0)
		# aquesta funció bloqueja l'aplicació, però com que s'exeucuta de forma periòdica,
		# no afecta el funcionament del programa i, per exemple, es pot tancar la finestra sense problemes
		self.lbl_bar = Label(self.root, text="Aixeca barrera", background="#ffe4b4", font=("Arial", 15))
		self.lbl_bar.pack()
		self.lbl_bar.place(width=150, height=90, x=480, y=350)
		sleep(1)
		self.lbl_bar.config(text="Tanca barrera")
		sleep(1)
		self.lbl_temps.config(text="")
		self.lbl_bar.config(text="")
		self.lbl_ES.config(text="")
		self.lbl_or.config(image='')
		self.lbl_ed.config(image='')
		self.lbl_cr.config(image='')
		sleep(2)
		self.lbl_bar.config(text="")

class GUI(): 
	"""
	Classe GUI (Interfície Gràfica d'Usuari), que executa funcions a temps regulars, però sense bloquejar l'execució.
	"""
	def __init__(self, t1, t2, dia, fout): # pragma: no cover
		"""
		Constructor de la classe

		arguments:
			t1: salts de temps (temps d'ordinador, segons)
			t2: salt de temps (temps real, minuts)
			dia -- temps en què comença la simulació
			fout -- fitxer d'escriptura

		Returns: None
		"""
		self.root = Tk()
		self.root.geometry("700x800")
		self.root.configure(background='#ffe4b4') 
		self.root.title("Projecte Parking")

		self.img_titol = ImageTk.PhotoImage(Image.open('img/titol.png'))
		self.lbl_titol = Label(self.root, image=self.img_titol)
		self.lbl_titol.pack() # fill = BOTH, expand = 1
		self.lbl_titol.place(width=450, height=100, x=10, y=10)

		self.bt_start = Button(self.root, text="Start", font=("Arial", 35))
		self.bt_start.pack()
		self.bt_start.place(x=480, y=20)
		self.bt_start.config(command=lambda: self.action(t1, t2, dia, fout))

	def run(self): # pragma: no cover
		"""
		Executa el bucle principal de l'aplicació gràfica

		Returns: None
		"""
		self.root.mainloop()

	def action(self, t1, t2, dia, fout): # pragma: no cover
		"""
		Acció de clicar el botó, comença la simulació. Els arguments provenen del constructor, i es propaguen a la següent fase.

		arguments:
			dia -- temps en què comença la simulació
			fout -- fitxer d'escriptura

		Returns: None
		"""
		self.bt_start["state"] = "disabled"
		self.t = Thread(target=processar_temps_gui, args=[self, t1, t2, dia, fout])
		self.t.setDaemon(True)
		self.t.start()

		return 1

# ==============================================================

if __name__ == "__main__":

	n = len(sys.argv)
	mode = 'cli'
	if n > 2:
		print("Mode d'ús: python simulacioparking.py [cli|gui]")
		sys.exit(0)
	elif n == 2:
		mode = sys.argv[1]

	if mode not in ['cli', 'gui']:
		print("Mode d'ús: python simulacioparking.py [cli|gui]")
		sys.exit(0)

	signal.signal(signal.SIGINT, signal_handler)
	ara = datetime.now()
	#dia_inici = datetime(ara.year, ara.month, ara.day) # dia actual, però a les 00:00:00
	dia_inici = datetime(ara.year, ara.month, ara.day, ara.hour, ara.minute)
	dia_fi = dia_inici + timedelta(days=365)

	str_matricules = '../simulaciodades/data/matricules.txt'

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

	arr_cotxes = []
	for i in range(len(cotxes_tipus)):
		arr_cotxes.append(generar_dades_tipus(i+1, cotxes_tipus[i], dicc[i], dies[i])[0])

	# fem el flatten, i ordenem per les dates
	arr_cotxes = list(itertools.chain.from_iterable(arr_cotxes)) # amb un array de numpy això es fa amb flatten()
	arr_cotxes_ordenats = sorted(arr_cotxes, key=lambda x: x[3]) # ordenem per dia

	logger.info("Tasca prèvia finalitzada, comença la simulació\n")
	sleep(2)

	#dia = dia_inici + timedelta(hours=ara.hour) # hora actual
	dia = dia_inici + timedelta(minutes=15) # hora actual

	try:
		os.makedirs(os.path.dirname('data/'))
	except FileExistsError:
		pass

	foutput = open("data/registre.csv", "a") # mode append per tal de què es vagin acumulant tots els valors
	if mode == 'cli':

		# bucle principal
		while 1:
			t = Timer(T1, processar_timer_cli, args=[dia, foutput])
			t.start()
			t.join()
			dia = dia + timedelta(minutes=T2)
	elif mode == 'gui':
		a = GUI(T1, T2, dia, foutput)
		a.run()

	foutput.close()
