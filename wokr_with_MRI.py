import nibabel as nib
import numpy as np
import os
import pydicom as pyd
from pydicom.errors import InvalidDicomError
from unidecode import unidecode


data_path = r'C:\Users\Admin\Desktop\MRI-processing\data'
path_to_one = r'C:\Users\Admin\Desktop\MRI-processing\data\Dolmatov_MS'

def transform_dicom_to_nifti(path_to_scrutiny :str, orientation :str, mode : list[str]):
	'''
	:param path_to_scrutiny: путь до папки с дикомами
	:param orientation: назавние искомой ориентации (axial,coronal,sagittal)
	:param mode: режим забора (T1,T2,fluid,flair,...)
	:return:
	'''
	orientation_mass = dict(axial=[[1, 0, 0], [0, 1, 0]], coronal=[[1, 0, 0], [0, 0, 1]],
							sagittal=[[0, 1, 0], [0, 0, 1]])

	filter_orintation = orientation_mass[orientation]
	for root, dirs, files in os.walk(path_to_scrutiny):
		for file in files:
			path_to_file = os.path.join(root,file)
			#print(path_to_file)
			try:
				dicom_data = pyd.dcmread(path_to_file)
				print(path_to_file)
			except InvalidDicomError:
				print(f"Файл невозможно прочитать. Имя файла: {path_to_file}.")
				continue
			try:
				check = np.abs(np.round(dicom_data.ImageOrientationPatient))
				bool_orientation = filter_orintation == check
			except AttributeError:
				print(f'Ориентация указана неверно. Имя файла: {path_to_file}')
				continue
			series = dicom_data.SeriesDescription.lower()
			bool_mode = any(mini_mode.lower() in series for mini_mode in mode)
			if bool_mode and bool_orientation:
				print('xnj n')



transform_dicom_to_nifti(path_to_one,'axial',['flair','fluid'])
#нет смысла в функции
# def get_data(path_to_dir):
# 	'''
# 	:param path_to_dir: путь до файла NIFTI
# 	:return: распакованные данные поступившего файла
# 	'''
# 	nifti = nib.load(path_to_dir)
# 	return nifti

def rename_file_to_unicode(path_to_dir):
	'''
	:param path_to_dir: путь до биректории которую хотим переиметовать
	:return: файл переименуется в исходной папке, пример: прив е т -> priv_e_т
	Замечание: меняется только имя папки, но не путь до нее
	'''
	path_name = path_to_dir.split(os.path.sep)[:-1]
	name = unidecode(path_to_dir.split(os.path.sep)[-1]).replace(' ','_')
	path_name = os.path.join(os.path.sep.join(path_name),name)
	os.rename(path_to_dir,path_name)

