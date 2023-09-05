import cv2
import numpy as np
import os  
from PIL import Image
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QInputDialog


# Load imagen and pick on it class
class Vectorization_Module:
	"""
	"""
	def __init__(self, img, ppi, imagefile, directory):
		"""
		Parameters:
					img: opencv object
						Object image from opneCV
					directory: list
						List of strings of the path to image file split by directory
					ppi: int
						Path to image file
		Returns:
					vr: float
						speed rotation of recording drum (for continuos time Marks option)
					amp0: float
						amplitude zero value (for continuos time Marks option)
					x_vaues: list
						x corrdinate for opposite corners of the image
					y_vaues: list
						y corrdinate for opposite corners of the image
		"""
		self.img = img
		self.ppi = ppi
		self.imagefile = imagefile
		self.directory = directory
		

	def referenceSystem(self):
		"""
		Function to scale the output data.
			1.- Calculates the distance between two time-marks on the  record,
			to obtain amplitude zero value, and paper drums speed rotation.
			or
			2.- Input opposite corners x,y coordinate values.
				Pick over an image using openCV modules

		"""

		img = self.img
		ro, co = img.shape[:2]
		item = ('Continuous Time-marks','Opposite image corners values')
		# Define time marks scale function
		def timeMarks(heightimg):
			global clone, dot
			try:
				clone = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
			except:
				clone = img.copy()
			dot = []
			QMessageBox.information(self, 'Instructions',
				'DobleClick over at least three continuous time-marks before\n'
				'the first arrival on the same or earlier trace. \n'
				'By pressing "Esc", the process ends and the image closes')
			self.text.append('Instructions \n' +
				'DobleClick over at least three continuous time-marks before \n' +
				'the first arrival on the same or earlier trace\n' +
				'By pressing "Esc", the process ends and the image closes')

			def distance(event, x, y, flags, params):
				global  dot, clone
				if event == cv2.EVENT_LBUTTONDBLCLK:
					cv2.circle(clone, (x, y), round(self.ppi*0.005), (0, 255, 0), -1)
					dot.append((x, y))
			# paper drums speed rotation 'vr' considering the image resolution in (mm/s)
			# To correct the amplitude 'amp0' (amplitude on mm near baseline trace)
			cv2.namedWindow('Define time/amplitude scale', cv2.WINDOW_NORMAL)
			cv2.setMouseCallback('Define time/amplitude scale', distance)
			while True:
				cv2.imshow('Define time/amplitude scale', clone)
				k = cv2.waitKey(1)
				if k == 27 & 0xff:
					break
			cv2.destroyWindow('Define time/amplitude scale')
			if len(dot) > 2:
				dd = np.array(dot)
				suma = np.array([])
				for i in range(len(dd) - 1):
					suma = np.append(suma,dd[i+1,0]-dd[i,0])
				mean = np.mean(suma)
				vr = ((mean * 25.4) / self.ppi) / 60
				(vr, ok) = QInputDialog.getDouble(self, 'The drum speed rotation ',
				'The computed Drum speed Rotation in mm/s is:',vr, 0, 5, 4)
				amp0 = (((dd[0,1] + dd[1,1]) / 2) / self.ppi) * 25.4
				amp0 = (-1*amp0 + heightimg)
			return vr, amp0
		# Opposite corner coordinates function
		def getpoint():
			X_values = np.empty(2)
			Y_values = np.empty(2)
			try:
				(X_values[0], ok) = QInputDialog.getDouble(self, 'Input Values ',
				'Left X value:',0, -10000000000000, 1000000000000, 3)
				(Y_values[0], ok) = QInputDialog.getDouble(self, 'Input Values ',
				'Up Y value:',0, -10000000000000, 1000000000000, 3)
				(X_values[1], ok) = QInputDialog.getDouble(self, 'Input Values ',
				'Right X value :',0, -10000000000000, 1000000000000, 3)
				(Y_values[1], ok) = QInputDialog.getDouble(self, 'Input Values ',
				'Down Y value :',0, -10000000000000, 1000000000000, 3)
			except:
				QMessageBox.critical(self,'Error',
					'Both corners values must be defined')
			return X_values, Y_values
		
		try:
			imheight = (ro/self.ppi) * 25.4  # image height on mm
			item, okPressed = QInputDialog.getItem(self,'Define time/amplitude scale ',
									'How to scale the output data? : ',item, 0, False)

			if okPressed and item == 'Opposite image corners values':
				X_values, Y_values = getpoint()
				# self.text.append('\n{:}={:},{:} '.format('Left Up corner values:  ',
				# 		X_values[0], Y_values[0]))
				# self.text.append('{:}={:},{:} '.format('Right Down corner values: ',
				# 		X_values[1],Y_values[1]))
				return X_values, Y_values

			elif okPressed and item == 'Continuous Time-marks':
				vr, amp0 = timeMarks(imheight)

				# self.text.append('\n{:}={:.4} {:}'.format('Average distance between' +
				# 										' time-marks',(vr * 60), 'mm'))
				# self.text.append('{:}={:.4} {:}'.format('Average distance between' +
				# 										' time-marks',mean, 'pixels'))
				# self.text.append('{:}={:.4} {:}'.format('Average paper drums speed rotation' +
				# 									' of the seismograph: ', vr, ' mm/s'))
				return vr, amp0

		except NameError:
			X_values, Y_values = getpoint()
			# self.text.append('\n{:}={:},{:} '.format('Left Up corner values:  ',
			# 		X_values[0], Y_values[0]))
			# self.text.append('{:}={:},{:} '.format('Right Down corner values: ',
			# 		X_values[1],Y_values[1]))
			return X_values, Y_values

	def vectorize(self):
		"""
		Pick over an image using openCV modules
			Parameters:
					img (opencv object)	: Object image from opneCV
					directory (list)	: Listo of strings of the path to image file split by directory
					imagefile (str)		: Path to image file
			Returns:
					points (list)		: Listo fo x,y coordinates of every point picked over the image
					img (openCV object) : Object image from opneCV with the picked points
		"""
		import time
		ro, co = img.shape[:2]
		check=0
		img = self.img
		try:
			color = (255, 0, 225)
			img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
		except:
			# img = clone.copy()
			colors = [(255,0,0),(0,0,255),(0,255,0),(255,255,0),(255,0,255),(0,255,255),(255,136,0)]
			color = colors[np.random.choice(len(colors))]

		# mb = QMessageBox()
		# mb.setIcon(QMessageBox.Information)
		# mb.setWindowTitle('Instructions',)
		print('"DobleClick"	Mark the coordinate on the seismogram image \n'
			'"z" 	   Undo the last marked point\n'
			'"r" 	   restarts vectorization function \n'
			'"Esc" 	   ends vectorization function')

		points = []

		def mouseDrawing(event, x, y, flags, params):
			if event == cv2.EVENT_LBUTTONDBLCLK:
				points.append((x, y))
		cv2.namedWindow(f'Vectorize on {self.directory[-1]}', cv2.WINDOW_NORMAL)
		cv2.resizeWindow(f'Vectorize on {self.directory[-1]}',(int(600), int(400))) # This size can be adapated to the screen resolution
		cv2.setMouseCallback(f'Vectorize on {self.directory[-1]}', mouseDrawing)
		while True:
			clone = img.copy()
			for cp in points:
				cv2.circle(clone, cp, 3, (0, 0, 255), -1)
				if len(points) > 1:
					for i in range(len(points)):
						if i != 0:
							cv2.line(clone, points[i-1], points[i], color, 2)
			cv2.imshow(f'Vectorize on {self.directory[-1]}',clone)
			key = cv2.waitKey(delay=1) & 0xff
			if key == ord('z'):
				points = points[:len(points) - 1]
			elif key == ord('r'):
				points = []
			elif key == 27:
				break
		img = clone.copy()
		del clone
		cv2.destroyWindow(f'Vectorize on {self.directory[-1]}')
		return img, points
	

	#####################################################################################
	# Graphical representation of data on matplotlib canvas on the main window of the GUI

	def prePlot(self, points, amp0=0.0, vr=0.0, X_values=[0,0], Y_values=[0,0]):
		ro, co = self.img.shape[0:2]
		amp = []
		treg = []
		for i in range(len(points)):
			amp.append(float(points[i][1]))
			treg.append(float(points[i][0]))
		imheight = (ro/self.ppi) * 25.4  # image height on mm
		self.ax.clear()
		try:
			if vr != 0.0:		
				# plot in canvas figure in the GUI a is a matplotlib canvas defined in the main window
				self.ax.plot(((np.array(treg)/self.ppi) * 25.4) / vr,
					((((np.array(amp)/self.ppi) * 25.4) * -1) + imheight) - amp0, 'k')
				self.ax.set_ylabel('$ Amplitude_{mm} $')
				self.ax.set_xlabel('$ time_{sec} $')
				self.ax.grid()
				self.canvas.draw()
			elif Y_values.any() != 0.0:
				i = 0
				ti_v = np.empty(len(treg))
				amp_v = np.empty(len(amp))
				if Y_values[0] > Y_values[1]:
					amp = (np.array(amp) * -1) + ro
				else:
					amp = np.array(amp)
					self.ax.invert_yaxis()

				for x, y in zip(np.array(treg), np.array(amp)):
					ti_v[i] = X_values.min() + ((x * (X_values[1] - X_values[0])) / co)   # 
					amp_v[i] = Y_values.min() + ((y * np.abs(Y_values[1] - Y_values[0])) / ro)  #
					i += 1
				self.ax.plot(ti_v, amp_v, 'k')
				self.ax.set_ylabel('$ Amplitude [mm] $')
				self.ax.set_xlabel('$ time [sec] $')
				self.ax.grid()
				self.canvas.draw()
			else:
		# except NameError:
				# plot in canvas figure in the GUI
				self.ax.clear()
				self.ax.plot(np.array(treg), (np.array(amp) * -1) + ro, 'k')
				self.ax.set_ylabel('$ Y [pixels] $')
				self.ax.set_xlabel('$ X [pixels] $')
				self.ax.grid()
				self.canvas.draw()
		except:
			pass
	#####################################################################################
	# Save Data in ASCII format

	def saveData(self, points, amp0=0.0, vr=0.0, X_values=[0,0], Y_values=[0,0]):
		amp = np.empty(len(points))
		treg = np.empty(len(points))
		ro, co = self.img.shape[0:2]
		imheight = (ro/self.ppi) * 25.4
		for i in range(len(points)):
			amp[i] = points[i][1]
			treg[i] = points[i][0]
		ampPX = (amp * -1) + ro
		tregPX = treg
	# functions for reference data

		def timeMarks(amp0, imheight, vr, a, t):
			amp = ((((a/self.ppi) * 25.4) * -1) + imheight) - amp0
			tr = ((t/self.ppi) * 25.4) / vr
			return amp, tr

		def pix2coord(a, t, Xpixmax, Ypixmax, x_val, y_val):
			import numpy as np
			X_scale = np.empty(len(t))
			Y_scale = np.empty(len(a))
			if y_val[0] > y_val[1]:
				a = (np.array(a) * -1) + Ypixmax
			else:
				a = np.array(a)
			i = 0
			for x, y in zip(t,a):
				X_scale[i] = x_val.min() + ((x * (x_val[1] - x_val[0])) / Xpixmax)

				Y_scale[i] = y_val.min() + ((y * np.abs(y_val[1] - y_val[0])) / Ypixmax)
				i = i+1
			return Y_scale, X_scale

			# ti_v[i] = X_values.min() + ((x * (X_values[1] - X_values[0])) / co)  # 
			# amp_v[i] = Y_values.min() + ((y * (Y_values[1] - Y_values[0])) / ro)  #
		##################################
		try:
			if vr != 0.0:
				amp_mm, treg_s = timeMarks(amp0,imheight,self.ppi,vr,amp,treg)
			elif Y_values.any() != 0.0:
				amp_mm, treg_s = pix2coord(amp,treg,co,ro,X_values,Y_values)
			outdata = np.array([treg_s, amp_mm])
			outdata = outdata.T
			item = ('Scaled time-series', 'Pixels')
			(item, okPressed) = QInputDialog.getItem(self,'Save Data',
							'          Data : ',item, 0, False)
			if okPressed and item == 'Pixels':
				outdata = np.array([tregPX, ampPX])
				outdata = outdata.T
				outname, _ = QFileDialog.getSaveFileName(self, 'Save as ASCII file ',
							self.imagefile[0:-4]+'_pixel.txt', "Text files (*.txt *.dat);; All files (*)")
				with open(outname, 'w+'):
					np.savetxt(outname, outdata, fmt=['%e','%e'], delimiter='	')

			elif okPressed and item == "Scaled time-series":
				outname, _ = QFileDialog.getSaveFileName(self, 'Save as ASCII file ',
							self.imagefile[0:-4]+'_refe.txt', "Text files (*.txt *.dat);; All files (*)")
				with open(outname, 'w+'):
					np.savetxt(outname, outdata, fmt=['%e','%e'], delimiter='	')
			else:
				pass
		except:
			outdata = np.array([tregPX, ampPX])
			outdata = outdata.T
			outname, _ = QFileDialog.getSaveFileName(self, 'Save as ASCII File ',
						self.imagefile[0:-4]+'_pixel.txt', "Text Files (*.txt *.dat);; All files (*)")
			try:
				with open(outname, 'w+'):
					np.savetxt(outname, outdata, fmt=['%e','%e'], delimiter='	')
			except FileNotFoundError:
				pass

