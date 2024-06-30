import nibabel as nib
import numpy as np
import os
import pydicom as pyd
from pydicom.errors import InvalidDicomError
from unidecode import unidecode
import shutil
import dicom2nifti
import json
import cv2
from PIL import Image
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

root_path = os.path.dirname(os.path.abspath(__file__))
data_path = r'C:\Users\Admin\Desktop\MRI-processing\data'
path_to_one = r'C:\Users\Admin\Desktop\MRI-processing\data\Dolmatov_MS'
def transform_dicom_to_nifti(path_to_scrutiny :str, orientation :str, mode : list[str]):
    '''
    :param path_to_scrutiny: путь до папки с дикомами
    :param orientation: назавние искомой ориентации (axial,coronal,sagittal)
    :param mode: режим забора (T1,T2,fluid,flair,...)
    :return: путь до папки с файлом nifti
    '''

    processed = os.path.join(root_path,'processed_data')
    to_current_folder = os.path.join(processed,path_to_scrutiny.split(os.path.sep)[-1])
    path_to_dicom = os.path.join(to_current_folder,'DICOM')
    path_to_nifti = os.path.join(to_current_folder,'NIFTI')
    os.makedirs(processed,exist_ok= True)
    os.makedirs(path_to_dicom,exist_ok= True)
    os.makedirs(path_to_nifti,exist_ok= True)

    orientation_mass = dict(ax=[[1, 0, 0], [0, 1, 0]], cor=[[1, 0, 0], [0, 0, 1]],
                            sag=[[0, 1, 0], [0, 0, 1]])

    filter_orintation = orientation_mass[orientation]
    for root, dirs, files in os.walk(path_to_scrutiny):
        for file in files:
            path_to_file = os.path.join(root,file)
            #print(path_to_file)
            try:
                dicom_data = pyd.dcmread(path_to_file)
                print(path_to_file)
            except InvalidDicomError:
                print(f"Файл невозможно прочитать. Путь до файла: {path_to_file}.")
                continue
            try:
                check = np.abs(np.round(dicom_data.ImageOrientationPatient))
                bool_orientation = all(filter_orintation[0] == check[:3]) and all(filter_orintation[1] == check[3:])
            except AttributeError:
                print(f'Ориентация указана неверно. Путь до файла: {path_to_file}')
                continue
            series = dicom_data.SeriesDescription.lower()
            bool_mode = any(mini_mode.lower() in series for mini_mode in mode)
            if bool_mode and bool_orientation:
                shutil.copy(path_to_file,path_to_dicom)

    dicom2nifti.convert_directory(path_to_dicom,path_to_nifti,compression= True,reorient= True)
    return path_to_nifti


def create_demyelination_areas_markups(nifti_path: str, markup_path: str):
    '''
    :param nifti_path: путь до папки с файло nifti из функции transform_dicom_to_nifti
    :param markup_path: путь до коренной папки исследования
    :return: массив со значениями json файла
    '''

    print("Запуск функции create_demyelination_areas_markups")
    # read jsons and create a list of matrixes with coordinates for one nifti
    points_lps = []
    data_nifti = nib.load(os.path.join(nifti_path,os.listdir(nifti_path)[0]))
    # walk through .json filenames and add their location to list
    for root, dirs, files in os.walk(markup_path):
        for file in files:
            if file.endswith('.json'):
                json_file_path = os.path.join(root, file)
                with open(json_file_path, 'r') as f:
                    local_point_list = []
                    json_data = json.load(f)
                    # form a 4x1 np matrix using 'orientation' and 'position' from each .json
                    for point in json_data["markups"][0]["controlPoints"]:
                        orientation_matrix = np.reshape(np.array(point['orientation']), (3, 3))
                        position_matrix = np.reshape(np.array(point["position"]), (3, 1))
                        local_point_list.append(
                            np.vstack(((orientation_matrix @ position_matrix), [1])))
                    points_lps.append((file,local_point_list))
    new_points_lps = []
    for file, point in points_lps:
        local_list = []
        for local_point in point:
            index_coords = np.round(np.dot(np.linalg.inv(data_nifti.affine), np.array(local_point)))
            local_list.append(index_coords)
        new_points_lps.append((file,local_list))
    return new_points_lps

def create_yolo_data(path_to_nifti, new_points_lps, yolo_path):
    '''
    :param path_to_nifti: путь до обрабатываемого файла nifti
    :param new_points_lps: массив с точками из json (функция create_demyelination_areas_markups)
    :param yolo_path: путь по которому будут созранены размеченные изображения
    :return:
    '''
    epi_img = nib.load(os.path.join(path_to_nifti,os.listdir(path_to_nifti)[0]))
    print("Запуск функции create_yolo_data")
    #Объявление переменных путей
    path_to_Yolo_data = os.path.join(yolo_path, 'Yolo')
    path_to_annotation = os.path.join(path_to_Yolo_data, 'annotation')
    path_to_images = os.path.join(path_to_Yolo_data, 'images')
    path_to_labels = os.path.join(path_to_Yolo_data, 'labels')

    #Создание необходимых директорий
    os.makedirs(path_to_Yolo_data, exist_ok=True)
    os.makedirs(path_to_annotation, exist_ok=True)
    os.makedirs(path_to_images, exist_ok=True)
    os.makedirs(path_to_labels, exist_ok=True)

    for i in range(epi_img.shape[2]):
        #Создание массивов для распределения масок одного слоя по разным классам
        dct = dict.fromkeys(['I','P','S','U'],np.zeros(shape = (epi_img.shape[0], epi_img.shape[1])))

        for file, points in new_points_lps:
            if len(points) > 0 and int(points[0][2].item()) == i:
                contour = [(int(point[1].item()), int(point[0].item())) for point in points]
                mass = dct[file[0]].copy()
                cv2.fillPoly(mass, [np.array(contour)], 255)
                dct[file[0]] = mass
        plt.imshow(epi_img.get_fdata()[:,:,i],cmap='gray')
        plt.axis('off')
        plt.savefig(os.path.join(path_to_images,f'{i}.png'), bbox_inches='tight', pad_inches=0)
        for key,value in dct.items():
            # img = Image.fromarray(value*255).convert('L')
            # img.save(os.path.join(path_to_annotation,f'{key}_{i}.png'))
            plt.imshow(value, cmap='gray')
            plt.axis('off')
            name = f'{key}_{i}.png'
            plt.savefig(os.path.join(path_to_annotation,name), bbox_inches='tight', pad_inches=0)

path = transform_dicom_to_nifti(path_to_one,'ax',['flair','fluid'])
markups = create_demyelination_areas_markups(path,path_to_one)
create_yolo_data(path,markups,os.path.sep.join(path.split(os.path.sep)[:-1]))

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

#Добавить полосу загрузки через консоль