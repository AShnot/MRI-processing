import cv2
import albumentations as A
from torchvision.utils import make_grid

def augmentation(image,masks,num_augm):
	transform = A.Compose(
		[
			A.RandomBrightnessContrast(p=0.5),
			A.RandomGamma(p=0.5),
			A.CLAHE(p=0.4),
			A.HueSaturationValue(hue_shift_limit=20, sat_shift_limit=50, val_shift_limit=50, p=0.4),
			A.RGBShift(p=0.5),
			A.Blur(p=0.5),
			A.GaussNoise(p=0.6),
			A.ElasticTransform(p=0.3),
			A.Flip(p=0.5),
			A.RandomRotate90(p=0.5)
		]
	)
	list_ = []
	# for i in range(num_augm):
	augmented = transform(image = image,masks = masks)
	mask_aug = augmented['masks']
	image_aug = augmented['image']
	list_.append(image_aug)
	list_.append(mask_aug)


