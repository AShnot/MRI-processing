import cv2
import albumentations as A
import numpy as np
import matplotlib.pyplot as plt
from path_file import path_routing
import os
from itertools import groupby

# aug = A.Compose(
#         [
#             A.RandomBrightnessContrast(p=0.4),
#             A.RandomGamma(p=0.5),
#             A.CLAHE(p=0.4),
#             A.HueSaturationValue(hue_shift_limit=20, sat_shift_limit=50, val_shift_limit=50, p=0.4),
#             A.RGBShift(p=0.1),
#             A.Blur(p=0.3),
#             A.GaussNoise(p=0.6),
#             A.ElasticTransform(p=0.3),
#             A.Flip(p=0.5),
#             A.RandomRotate90(p=0.6)
#         ]
#     )
path_to_one = os.path.join(path_routing.processed_data_path,'Dolmatov_MS')
def show(imgs):
    if not isinstance(imgs, list):
        imgs = [imgs]
    fix, axs = plt.subplots(ncols=len(imgs), squeeze=False)
    for i, img in enumerate(imgs):
        axs[0, i].imshow(np.asarray(img))
        axs[0, i].set(xticklabels=[], yticklabels=[], xticks=[], yticks=[])

def augmentation(transform,image,masks):
    list_ = []
    # for i in range(num_augm):
    augmented = transform(image=image, masks=masks)
    mask_aug = augmented['masks']
    image_aug = augmented['image']
    list_.append(image_aug)
    list_.extend(mask_aug)
    return list_


def make_augmentation(path_main,num_augm):
    yolo = os.path.join(path_main,'Yolo')
    path_to_image = os.path.join(yolo,'images')
    path_to_mask = os.path.join(yolo,'annotation')
    image = sorted(os.listdir(path_to_image),key = lambda a: int(a.split('.')[0]))
    masks = sorted(os.listdir(path_to_mask),key = lambda a: int(a.split('.')[0].split('_')[1]))
    groups = groupby(masks,lambda a: int(a.split('.')[0].split('_')[1]))
    #тут нужно добавить группировку по индексу т.е. I_1.png и U_1.png мы группируем по 1
    print([[item[0] for item in data] for (key, data) in groups])

make_augmentation(path_to_one,1)
