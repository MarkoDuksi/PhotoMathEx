#!/usr/bin/env python
# coding: utf-8

import os
import sys
from itertools import compress
import numpy as np
import cv2 as cv
import extractor
from tensorflow.keras import models
import solver


# actual values for predicted labels
LABELS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
          '+', '-', '*', '/', '(', ')']


# simple preprocessing
def framechar(char, reshape=False):
    """Frame the character, optionally reshape

    Receive a character as a single-channel image in a 2D uint8 numpy
    array format. Frame the character array by scaling its larger dimension
    down or up to 20 pixels along with scaling the smaller dimension
    by the same factor. Invert the colors. Center it inside a 28 by 28
    black frame. If `reshape` set to True, reshape the array as required
    by CNN classifier. Return the new uint8 numpy array.
    """

    # determine the scaling factor
    max_dim = max(char.shape)
    scale = 20 / max_dim

    # resize to 20 px along longer axis, keep aspect ratio
    char = cv.resize(char, (0, 0), fx=scale, fy=scale)

    # invert image to make background dark and ink light
    char = 255 - char

    # create a 28 by 28 black canvas
    new_canvas = np.zeros((28, 28), dtype=np.uint8)

    # coords of the upper right corner of char within the new canvas
    height, width = char.shape
    top = (28 - height) // 2
    left = (28 - width) // 2

    # place the char in the center
    new_canvas[top:(top + height), left:(left + width)] = char

    # classifer needs a different shape
    if reshape is True:
        new_canvas = new_canvas.reshape(-1, 28, 28, 1)

    return new_canvas


def main():
    if len(sys.argv) == 1:
        print('Provide valid image filenames as command line arguments.')
        return

    # fetch image file names from command line arguments
    img_names = sys.argv[1:]

    # determine which files exist, exit if none
    valid_img_names_indices = list(map(os.path.exists, img_names))
    if not any(valid_img_names_indices):
        print("No existing file name was specified.")
        return

    # extract the names of existing files
    valid_img_names = list(compress(img_names, valid_img_names_indices))

    # extract the names of non-existing files and report them
    invalid_img_names_indices = [not item for item in valid_img_names_indices]
    if any(invalid_img_names_indices):
        invalid_img_names = list(compress(img_names, invalid_img_names_indices))
        print('Could not found:', *invalid_img_names)

    # load a trained CNN
    my_cls = models.load_model('pm_model_md.h5')

    for img_name in valid_img_names:
        if not os.path.exists(img_name):
            print(f'cannot find image: {img_name}')
            continue

        try:
            img = cv.imread(img_name, 1)
        except Exception as e:
            print(f'Error reading image file: {img_name}')
            print(e)
            continue

        # extract line candidates
        lines = extractor.extract_lines(img)

        for line in lines:
            try:
                # extract token candidates
                chars = extractor.extract_chars(line)

                # classify extracted candidates
                predicted = []
                for char in chars:
                    char = framechar(char, reshape=True)
                    pred = my_cls.predict(char)
                    label = LABELS[np.argmax(pred)]
                    predicted.append(label)

                # generate expression string and check if it is valid
                expression_candidate = ' '.join(predicted)
                validated_expression = solver.validate(expression_candidate)

                # print the current filename if more was specified
                if len(img_names) > 1:
                    print(f'\nfrom {img_name}:')

                if validated_expression is not None:
                    # do not print the outermost parentheses
                    print(f'{validated_expression[2: -2]} = ', end='')
                    result = solver.evaluate(validated_expression)
                    print(result)
                else:
                    print(f'{expression_candidate}\nnot a valid expression')

            except Exception as e:
                print(e)


if __name__ == '__main__':
    main()
