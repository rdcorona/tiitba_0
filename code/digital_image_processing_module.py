import cv2
import numpy as np
from PIL import Image
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QInputDialog


# Load imagen and pick on it class
class DIP_Module:
	"""
	DIGITAL IMAGE PROCESSING MODULE
    Define the digital image processing Class
	"""
	def __init__(self, path_to_file):
		"""
		parmeters:
			path_to_file (str): Path to image file
		"""
		self.imagefile = path_to_file
		self.directory = self.imagefile.split('/')
		

	def load_image(self):
		"""
		Loads an images annd open it with openCV
            Parameters:
                
			Returns:
				img (opencv object)	: Object image from openCV
				ppi (int)			: Pixels per inch of teh image
				directory (list)	: Listo of strings of the path to image file split by directory
				imagefile (str)		: Path to image file
		"""

		# imagefile, _ = QFileDialog.getOpenFileName(self, 'Load Seismogram Raster Image',
		# path, "Image Files (*.jpg *.png *.jpeg *.tif);; All files (*)")

		imagefile = self.imagefile
		directory = imagefile.split('/')
		try:
			ii = Image.open(imagefile)
			self.ppi = ii.info['dpi'][0]
		except KeyError:
			(inp, okPressed) = QInputDialog.getInt(self, 'Raster Image pixels per inch',
						'No PPI on raster information. \n'
						'Input PPI: ',600, 0, 3000, 2)
			if okPressed:
				self.ppi = float(inp)

		except NameError:
			QMessageBox.Critical(self,'Error!',
				'Without a PPI value, the usage of some functions will be limited')
		img = cv2.imread(self.imagefile,0)

		# img, points = self.pick_on_image(img, directory)

		return img
        # This functio should enable the image processing functions
	


#####################################################################################
	# Rotate image 90° clockwise

	def setRotate(self, img):
		"""
		Rotate image 90° to the left
            Parameters:
                img (opencv object)	: Object image from openCV
                
			Returns:
			    img (opencv object)	: Object image from openCV rotated
		"""

		try:
			img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
			cv2.namedWindow(self.directory[-1], cv2.WINDOW_NORMAL)
			cv2.imshow(self.directory[-1], img)
		except NameError as e:
			QMessageBox.warning(self, 'Error!',
				f'{e}\nNo image file found!')
		cv2.waitKey(0)
		return img 
	
	#####################################################################################
	# Increase contrast

	def setContrast(self, img):
		"""
		Increase grayscale image constrast
            Parameters:
                img (opencv object)	: Object image from openCV
                
			Returns:
			    img (opencv object)	: Object image from openCV with higher contrast
		"""		
		try:
			clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))
			img = clahe.apply(img)
			cv2.namedWindow(self.directory[-1]+' contrast increase', cv2.WINDOW_NORMAL)
			cv2.imshow(self.directory[-1]+' contrast increase', img)
		except NameError as e:
			QMessageBox.warning(self, 'Error!',
				f'{e}\nNo image file found!')
		cv2.waitKey(0)
		return img
	
	#####################################################################################
	# Turn image in to binary

	def setBinary(self, img):
		"""
		Turns image into binary format (Black and Withe)
            Parameters:
                img (opencv object)	: Object image from openCV
                
			Returns:
			    img (opencv object)	: Object image from openCV black and withe
		"""		
		try:
			(thersh, img) = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY |
											cv2.THRESH_OTSU)
			cv2.namedWindow(self.directory[-1]+' Binary (B/W)', cv2.WINDOW_NORMAL)
			cv2.imshow(self.directory[-1]+' Binary (B/W)', img)
		except NameError as e:
			QMessageBox.warning(self, '!Error!',
				f'{e}\nNo image file found!')
		cv2.waitKey(0)
		return img 
	
	#####################################################################################
	# Trim Seismogram

	def TrimSeismogram(self, img):
		"""
		Trim image in a selected Rectangle of Interes area
            Parameters:
                img (opencv object)	: Object image from openCV
                
			Returns:
			    img (opencv object)	: Object image from openCV Trimed
		"""		
		# Select ROI
		try:
			fromCenter = False
			QMessageBox.information(self, 'Select ROI ',
						'Select Region Of Interest and then press SPACE or ENTER key!\n'
						'Cancel the selection process by pressing "c" key! ')

			self.text.append('Select ROI\n' +
						'Select a ROI and then press SPACE or ENTER key!\n' +
						'Cancel the selection process by pressing "c" key! ')

			cv2.namedWindow('Trim in '+self.directory[-1], cv2.WINDOW_NORMAL)
			cv2.imshow('Trim in '+self.directory[-1], img)
			r = cv2.selectROI('Trim in '+self.directory[-1], img, fromCenter)
		# Crop image
			imcp = img[int(r[1]):int(r[1] + r[3]), int(r[0]):int(r[0] + r[2])]
			cv2.destroyWindow('Trim in '+self.directory[-1])
		# Display cropped image
			img = imcp
			cv2.namedWindow(self.directory[-1]+' Trimmed', cv2.WINDOW_NORMAL)
			cv2.imshow(self.directory[-1]+' Trimmed', img)
		except NameError:
			QMessageBox.warning(self, 'Error!',
				'Cannot Trim, no image file found!')
		cv2.waitKey(0)
		return img
	
	#####################################################################################
	# Display image dimensions

	# def getInfo(self, img):
	####	self.text.append is a QTextEdit QtWidget that works as a pannel information in the Main GUI
	# 	try:
	# 		ro, co = img.shape[0:2]
	# 		ejex = (co / self.ppi) * 25.4  # image width on mm
	# 		ejey = (ro / self.ppi) * 25.4  # image height on mm
	# 		self.text.append('{:}= {:.4} {:} {:.4} {:}'.format('Raster Image Size', ejex,
	# 						'mm long, by', ejey, 'mm width'))

	# 		self.text.append('{:}={:} {:} {:} {:}'.format('Raster Image Size :', co,
	# 								'pixels long, by ', ro,'pixels width '))
	# 	except NameError:
	# 		self.text.append('{:}={:} {:} {:} {:}'.format('Raster Image Size :', co,
	# 								'pixels long, by ', ro,'pixels width '))

	# 	self.text.append('Image : ' + self.directory[-1])
	#####################################################################################
	# Save processed image

	def setSaveImg(self, img ):
		"""
		Saves img to disk with PPi resolution
            Parameters:
                img (opencv object)	: Object image from openCV
                
			Returns:
			    img (opencv object)	: Object image from openCV
		"""
		try:
			self.ppi * 1 
			outnameimg, _ = QFileDialog.getSaveFileName(self, 'Save Digitally Processed Image',
				self.imagefile[0:-4] + '.processed.jpg',
				"Images Files (*.jpg *.jpg *.tif);; All files (*)")
			PILimg = Image.fromarray(img)
			PILimg.save(outnameimg, dpi=(self.ppi,self.ppi))
		except NameError:
			sppi, okPressed = QInputDialog.getInt(self, 'Input Data',
										'Resolution Image in PPI :',600, 0, 2100)
			if okPressed:
				try:
					outnameimg, _ = QFileDialog.getSaveFileName(self, 'Save Digitally Processed Image',
						self.imagefile[0:-4] + '_processed',
						"Images Files (*.jpg *.jpg *.tif);; All files (*)")
					PILimg = Image.fromarray(img)
					PILimg.save(outnameimg, dpi=(sppi,sppi))
				except:
					pass
		except FileNotFoundError as e:
			pass
			QMessageBox.warning(self,'Warning', str(e))

		except:
			QMessageBox.warning(self, 'Warning!',
				'Image not saved!')
		return outnameimg
	
