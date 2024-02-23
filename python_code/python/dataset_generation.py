import os
import random
import re
import cv2
import glob
import imutils
import numpy as np
import datetime
from utils.utils_ import numerical_sort, open_image

base_path = ''
ref_images_path = base_path + 'dataset/reference_images/'

TODAY = str(datetime.date.today()).replace('-', '')
database_path = base_path + 'csr_responses/' + TODAY + '/'


def resize_image(image_path: str, scale_percent: int = 70):
    """
    :param image_path: str
    :param scale_percent: int, value to be resized
    :rtype: (resized image)
    """
    image = open_image(image_path)
    height, width, _ = image.shape

    height_center, width_center = height // 2, width // 2
    center = min(height_center, width_center)

    h_0, h_1, w_0, w_1 = (height_center - center), (height_center + center), \
        (width_center - center), (width_center + center)

    squared_image = image[h_0:h_1, w_0:w_1, :]
    image_size = int((center * 2 * scale_percent) / 100)
    dimension = (image_size, image_size)

    resized = cv2.resize(squared_image, dimension, interpolation=cv2.INTER_AREA)

    return resized


def image_generation(folder_path, image_path, std_start=0, std_stop=0.3, rot='OFF',
                     blur_in=1, blur_out=4, stage='Enrollment'):
    """
    :param folder_path:
    :param image_path:
    :param std_start:
    :param std_stop:
    :param rot:
    :param blur_in:
    :param blur_out:
    :param stage:
    :return:
    """
    n_attempts = 1 if 'Enrollment' in stage else 20
    str_position = [m.start() for m in re.finditer(r"/", image_path)][-1]

    resized_image = resize_image(image_path)
    h, w, d = resized_image.shape

    for i in range(1, n_attempts + 1):
        folder_name = folder_path + stage + '/' + image_path[str_position + 1:-4] + '/F_{0}'.format(i)

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        counter = 7

        if rot == 'OFF':
            rnd_vals = np.random.uniform(std_start, std_stop, 6)
            for val in rnd_vals:
                gauss_noise = np.random.normal(0, val, resized_image.size)
                gauss_noise = gauss_noise.reshape(h, w, d).astype('uint8')
                img_gauss = cv2.add(resized_image, gauss_noise)
                for blur in range(blur_in, blur_out):
                    counter -= 1
                    ksize = (blur, blur)
                    image_blurred = cv2.blur(img_gauss, ksize)
                    if counter < 0:
                        break
                    else:
                        cv2.imwrite(folder_name + '/'
                                    + image_path[str_position + 1:-4]
                                    + '_gauss_' + str(round(val, 5)).replace('.', '_')
                                    + '_blur_' + str(blur)
                                    + '.jpg', image_blurred)
        else:
            # Copy the reference image into each folder
            cv2.imwrite(folder_name + '/'
                        + image_path[str_position + 1:-4]
                        + '.jpg', resized_image)
            rot_start, rot_stop = 1, 6
            for angle in random.sample(range(rot_start, rot_stop), (rot_stop - rot_start)):
                val = random.uniform(std_start, std_stop)
                gauss_noise = np.random.normal(0, val, resized_image.size)
                gauss_noise = gauss_noise.reshape(h, w, d).astype('uint8')
                img_gauss = cv2.add(resized_image, gauss_noise)
                image_rotated = imutils.rotate(img_gauss, angle)
                for blur in range(blur_in, blur_out):
                    counter -= 1
                    ksize = (blur, blur)
                    image_blurred = cv2.blur(image_rotated, ksize)
                    resized = cv2.resize(image_blurred)
                    if counter < 0:
                        break
                    else:
                        cv2.imwrite(folder_name + '/'
                                    + image_path[str_position + 1:-4]
                                    + '_rot_' + str(angle)
                                    + '_gauss_' + str(round(val, 4)).replace('.', '_')
                                    + '_blur_' + str(blur)
                                    + '.jpg', resized)


# Dataset Generation
def dataset_generation(path_reference_images):
    """
    :return: set of images
    """
    stages = ['Enrollment', 'Authentication']
    ref_images = sorted(glob.glob(path_reference_images + '*.jpg'), key=numerical_sort)
    for stage in stages[:]:
        for ref_image in ref_images[:]:
            image_generation(database_path, ref_image, stage=stage)


dataset_generation(ref_images_path)
