#!/usr/bin/env python
# coding: utf-8

import sys
import numpy as np
import cv2 as cv
import extractor
import solver
from tensorflow.keras import models


# actual values for predicted labels
LABELS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
          '+', '-', '*', '/', '(', ')']


# simple preprocessing
def framechar(char, reshape=False):
    """Frame the character, optionally reshape

    Frame the character array by scaling its larger dimension
    down or up to 20 pixels along with scaling the smaller dimension
    by the same factor. Invert the colors. Center it inside a 28 by 28
    black frame and return the resulting new array. If `reshape` set to
    True, add the 3rd dimension needed by CNN classifier.
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

    # classifer needs a dedicated monochrome channel as a 3rd dimension
    if reshape is True:
        new_canvas.reshape(28, 28, 1)

    return new_canvas


def main():
    if len(sys.argv) == 1:
        print('Provide image filenames as command line arguments.')
        return

    # load a trained CNN
    my_cls = models.load_model('pm_model_md.h5')

    img_names = sys.argv[1:]
    for img_name in img_names:
        try:
            img = cv.imread(cv.samples.findFile(img_name, 1))
        except Exception as e:
            print(f'Error reading image file: {img_name}')
            print(e)
            return

        # extract line candidates
        lines = extractor.extract_lines(img)

        for line in lines:
            try:
                # extract token candidates
                chars = extractor.extract_chars(line)

                # classify extracted candidates
                predicted = []
                for idx, char in enumerate(chars, start=1):
                    # cv.imwrite(f'extracted_char_{idx:02}.jpg', char)
                    char = framechar(char)
                    # cv.imwrite(f'framed_char_{idx:02}.jpg', char)
                    char = char.reshape(-1, 28, 28, 1)
                    pred = my_cls.predict(char)
                    label = LABELS[np.argmax(pred)]
                    predicted.append(label)

                expression_candidate = ' '.join(predicted)
                print(f'\nfrom {img_name}: {expression_candidate}')

                validated_expression = solver.validate(expression_candidate)

                if validated_expression is not None:
                    result = solver.evaluate(validated_expression)
                    # print(f'expression as validated: {validated_expression}')

                    result = solver.evaluate(validated_expression)
                    print(f'{result = }')
                else:
                    print(f'not a valid expression')

            except Exception as e:
                print(e)


if __name__ == '__main__':
    main()
