import cv2
import glob
import numpy as np
import pandas as pd
import re
from skimage.feature import blob_log
import time
from utils.utils_ import numerical_sort, grid_positioning


def feature_extraction(image_path: str, min_sigma: int, max_sigma: int):
    '''
    :param image_path: path of the image
    :param min_sigma: int
    :param max_sigma: int
    :param num_sigma: int
    :return:
    '''

    IMAGE_ = cv2.imread(image_path)

    image_height, _, _ = IMAGE_.shape
    gray_scale = cv2.cvtColor(IMAGE_, cv2.COLOR_BGR2GRAY)

    ts1 = time.time()
    # Blob's detection and extraction
    blobs_array = (blob_log(gray_scale,
                            min_sigma=min_sigma, max_sigma=max_sigma,
                            threshold=0.07, overlap=1, exclude_border=2)).astype(int)

    time_blobs_detection = f'{round(time.time() - ts1, 4)}'

    blobs_number, _ = blobs_array.shape
    # average blobs diameter
    blobs_diameter = int(blobs_array[:, 2].mean()) * 2
    blobs_detected = pd.DataFrame(blobs_array[:, :2], columns=["x", "y"]).sort_values(
        ["x", "y"], ascending=[True, True]).reset_index(drop=True)

    ts2 = time.time()
    N, omega = grid_positioning(image_height, blobs_diameter, blobs_detected)
    time_grid = f'{round(time.time() - ts2, 4)}'

    return image_height, blobs_number, blobs_diameter, N, omega, time_blobs_detection, time_grid


def blob_extraction(attempt: str, txt_file: str):
    """
    :param attempt: folder with the set of images
    :param txt_file:
    :return:
    """

    global image_height, blobs_diameter, N

    if 'Image_6' in attempt or 'Image_7' in attempt or 'Image_1181' in attempt:
        min_sigma, max_sigma = 12, 16
    elif 'Image_228' in attempt or 'Image_852' in attempt or 'Image_974' in attempt or 'Image_140' in attempt \
            or 'Image_1060' in attempt or 'Image_1103' in attempt:
        min_sigma, max_sigma = 6, 14
    elif 'Image_265' in attempt:
        min_sigma, max_sigma = 8, 12
    elif 'Image_409' in attempt or 'Image_411' in attempt:
        min_sigma, max_sigma = 6, 8
    # elif 'Image_618' in attempt:
    #     min_sigma, max_sigma = 10, 20
    elif 'Image_972' in attempt:
        min_sigma, max_sigma = 6, 12
    elif 'Image_975' in attempt or 'Image_997' in attempt:
        min_sigma, max_sigma = 8, 18
    elif 'Image_1079' in attempt:
        min_sigma, max_sigma = 8, 20
    elif 'Image_1104' in attempt or 'Image_2366' in attempt:
        min_sigma, max_sigma = 10, 16
    elif 'tag1' in attempt or 'tag4' in attempt or 'tag5' in attempt or 'tag6' in attempt or 'tag7' in attempt \
            or 'tag8' in attempt:
        min_sigma, max_sigma = 4, 8
    elif 'tag11' in attempt or 'tag12' in attempt or 'tag13' in attempt:
        min_sigma, max_sigma = 4, 8
    else:
        min_sigma, max_sigma = 6, 10

    responses = sorted(glob.glob(attempt + '/*.jpg'), key=numerical_sort)
    omega_concat = []
    for response in responses:
        str0 = [m.start() for m in re.finditer(r"/", response)][-3]
        str1 = [m.start() for m in re.finditer(r"/", response)][-2]
        str2 = [m.start() for m in re.finditer(r"/", response)][-1]

        image_height, blobs_number, blobs_diameter, N, omega, time_blobs_detection, time_grid = \
            feature_extraction(response, min_sigma, max_sigma)

        omega_concat.append(omega)

        with open(txt_file, 'a') as file:
            file.write(response[str0 + 1:str1] + '\t'
                       + response[str1 + 1: str2] + '\t'
                       + response[str2 + 1:] + '\t'
                       + str(image_height) + '\t'
                       + str(blobs_number) + '\t'
                       + str(N) + '\t'
                       + str(N ** 2) + '\t'
                       + str(blobs_diameter) + '\t'
                       + time_blobs_detection + '\t'
                       + time_grid
                       + '\n')

    omega_concat = pd.concat(omega_concat, axis=1)

    return omega_concat, image_height, blobs_diameter, N


def robust_positions(omegas: pd.DataFrame, txt_file: str):
    """
    :param omegas: dataframe with n number of images
    :param txt_file: str
    :return: dataframe with robust positions
    """
    # A dataframe is created with the same size as df, filled with string values.
    omega_robust = pd.DataFrame(np.zeros((len(omegas), 2)).astype(str), columns=['x', 'y'])

    # threshold: half of the images. Defined as the total number of columns divided by 2 (x,y).
    # Then, by 2 for obtaining half of the images.
    threshold = len(omegas.columns.values) // 2 // 2

    if 'case1' in txt_file:
        # Case 1: blob in all acquired images
        for i in range(len(omegas)):
            if (omegas.loc[i] != '0.0').all():
                x = np.round(np.mean(omegas.loc[i]["x"]))
                y = np.round(np.mean(omegas.loc[i]["y"]))
                omega_robust.loc[i] = x.astype(int), y.astype(int)
            else:
                continue
    else:
        # Case 2: blob in the majority of the images
        for i in range(len(omegas)):
            if ((omegas.loc[i] != '0.0').sum() // 2) > threshold:
                x = np.round(omegas.loc[i]['x'].replace('0.0', np.NaN).mean())
                y = np.round(omegas.loc[i]['y'].replace('0.0', np.NaN).mean())
                omega_robust.loc[i] = x.astype(int), y.astype(int)
            else:
                continue

    robust_blobs = omega_robust[omega_robust['x'].astype(str).str.isdigit()].reset_index(drop=True)

    return robust_blobs
