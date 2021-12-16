#!/usr/bin/env python
# coding: utf-8

import numpy as np

# ------- Start of imports for dataset building helper functions -------
# import os
# import re
# import hashlib
# import pandas as pd
# ------- End of imports for dataset building helper functions -------


# set reasonable minimum dimensions for an input image array
# in practice the range is in thousands of pixels
MIN_IMG_WIDTH = 500
MIN_IMG_HEIGHT = 300

# set a reasonable minimum dimensions for an input char array
# in practice this results in good amount of despecling
MIN_CHAR_WIDTH = 15     # lowest allowable width for "(" and ")"
MIN_CHAR_HEIGHT = 8     # lowest allowable height for "-"
MIN_LINE_HEIGHT = 50    # lowest allowable height for all but "+", "-" and "x"

# used for calculating custom threshold value
# expressed in units of sigma over the histogram of uint8 values
WHITE_SPREAD = 2

# used to mark specles which score very close to this max
# derived from sum of uint8 values over the framed "character" output
MAX_INK_VALUE = 102_000


def desaturate(img):
    """Custom desaturate RGB image

    Desaturate by keeping the value of the darkest pixel in any of the
    red, green and blue channel representations. White background and
    black ink are not affected but even bright ink of commonly used
    colors (ie blue and red) in the same image is desaturated to near
    black to facilitate thresholding.
    """

    return img.min(axis=2)


def autostretch(img, black=None, white=None):
    """Stretch dinamic range of an img

    By default it auto-adjusts black and white levels to 0 and 255
    respectiverly, stretcing the values between. Custom levels can be
    provided by arguments to `black` and/or `white` parameters.
    """

    img_out = img.astype(float)
    if black not in range(0, 256):
        black = img_out.min()
    if white not in range(0, 256):
        white = img_out.max()
    if black >= white:
        raise ValueError('cannot stretch a single value')
    img_out = np.round((img_out - black) / (white - black) * 255)
    img_out[img_out < 0] = 0

    return img_out.astype(np.uint8)


def autothresh(img):
    """Threshold an img to b/w

     Apply custom parameters based on assumptions of what a histogram
     of a blank paper with some ink on it should look like. Make it
     indifferent of underexposure which is to be commonly expected.

     TBD: Adaptive version to accommodate for uneven lighting and/or
     shadows.
     TBD: Despecling could be done here.
    """

    # autostretch it
    img_out = autostretch(img).astype(float)

    # median is a good approximation of the middle "background" value
    # mode was also tested, the difference was negligible
    median = np.median(img_out)

    # std is an indication of unevenness of lighting over the paper
    # ink values are basically outliers
    std = img_out.std()

    # instead of the classic IQR outlier detection:
    thresh = max(median - WHITE_SPREAD * std, median / 2)

    # apply the threshold
    img_out[img_out > thresh] = 255
    img_out[img_out <= thresh] = 0

    return img_out.astype(np.uint8)


def get_mask(img, axis=None):
    """Detect regions of interest

    Assuming white background, get a mask vector indicating
    rows or columns (depending on the argument to `axis`)
    that contain any number of non-white pixels. Return
    a one-dimensional boolean numpy array.

    Note: Along with `split-mask` functionality, this kind of
    implementation allows for creative recursive implementations
    by spliting each roi further and further in alternating
    row/column fashion until no more spliting can be done.

    Note 2: The speed of the implementation allowed for quickly
    processing a large batch of sheets of characters into
    >100,000 characters size labeled training/testing datasets

    TBD: Return the coordinates of the possition of the mask
    within the image.
    """

    if axis not in (0, 1):
        raise ValueError('missing or invalid argument to `axis`')

    return (img != 255).any(axis=axis)


def split_mask(mask, super=False, minsize=1):
    """
    Split the possibly fragmented mask returned by get_mask
    into descrete masks. Retrun a list of masks, each one representing
    one continuous fragment from the original mask.

    Optionally, if `super` is set to True, return a list with a single
    supermask indicating a continuous region of interst containing all
    sub-regions. Such mask cannot be split any further.

    TBD: Despecling could also be done here.
    """

    # extend by a single False to accomadate offset by 1
    mask1 = np.array([*mask, False], dtype=bool)

    # prepend by a single False to make it offset by 1
    mask2 = np.array([False, *mask], dtype=bool)

    # detect transitions from False to True and vice versa
    transitions = np.logical_xor(mask1, mask2)

    # get the actual indices of True values
    transitions = np.flatnonzero(transitions)

    submasks = []

    # extract the submasks
    if super is False:    # from ranges between pairs of transitions
        for idx in range(0, len(transitions), 2):
            start_pos = transitions[idx]
            end_pos = transitions[idx + 1]
            if (end_pos - start_pos) < minsize:
                continue
            submask = np.zeros(mask.shape)
            submask[start_pos:end_pos] = 1
            submasks.append(submask.astype(bool))
    else:                 # from the range between the outhermost pair
        start_pos = transitions[0]
        end_pos = transitions[-1]
        if (end_pos - start_pos) >= minsize:
            submask = np.zeros(mask.shape)
            submask[transitions[0]:transitions[-1]] = 1
            submasks.append(submask.astype(bool))

    return submasks


def sort_masks(masks, ascending=False):
    """Sort masks by size

    Return a new list of masks sorted by size of their unmasked area.
    Sort in descending order by default.
    """

    reverse = not ascending
    sorted_masks = sorted(masks, key=lambda x: x.sum(), reverse=reverse)

    return sorted_masks


def extract_lines(img):
    """Line extractor

    Receive an RGB image in a form of numpy array and return vertically
    cropped blocks of content as a list of numpy arrays.

    TBD: Return a corresponding list of height coordinates for each
         cropped area from the original image.
    """

    # TBD: write an input validaton function to dry this block out
    if not isinstance(img, np.ndarray):
        raise TypeError('not a valid numpy array')
    elif (img.ndim != 3) or (img.shape[2] != 3):
        raise ValueError(f'the image must be a three-channel RGB image')
    elif img.shape[0] < MIN_IMG_HEIGHT or img.shape[1] < MIN_IMG_WIDTH:
        raise ValueError(f'minimum image dimensions are {MIN_IMG_WIDTH} by {MIN_IMG_HEIGHT}')

    img = desaturate(img)
    # cv.imwrite('desaturate.jpg', img)
    img = autothresh(img)
    # cv.imwrite('autothresh.jpg', img)

    # extract roi from image
    vmask = get_mask(img, axis=1)
    linemasks = split_mask(vmask, minsize=MIN_LINE_HEIGHT)
    if not len(linemasks):
        raise Exception(f'unable to detect a line of content at least {MIN_LINE_HEIGHT} pixels high')

    # crop the top and bottom of each line
    lines = [img[mask] for mask in linemasks]

    return lines


def extract_chars(line):
    """Char dextractor

    Receive a single numpy array from a list returned by `extract_lines`
    and return horizontally cropped blocks of content as a list of numpy
    arrays.

    TBD: Return a list of coords where each block was detected.
    Note: Ask for specification of "coordinates", ie:
          - rectangular bounding box corners, if so, which two?
          - center of mass?
          - ...
    """

    # TBD: write an input validaton function to dry this block out
    if not isinstance(line, np.ndarray):
        raise TypeError('not a valid numpy array')
    elif line.ndim != 2:
        raise ValueError(f'the image must be a greyscale image')
    elif line.shape[0] < MIN_LINE_HEIGHT or line.shape[1] < MIN_IMG_WIDTH:
        raise ValueError(f'minimum line dimensions are {MIN_IMG_WIDTH} by {MIN_LINE_HEIGHT}')

    # further subdivide the line into charater candidates
    hmask = get_mask(line, axis=0)
    charmasks = split_mask(hmask, minsize=MIN_CHAR_WIDTH)

    if len(charmasks) < 3:
        raise Exception(f'unable to detect at least 3 consecutive characters at least {MIN_CHAR_WIDTH} pixels wide')

    # assume all tokens are captured in this roi as multiple characters
    # and crop the white area around each
    chars = []
    for charmask in charmasks:
        char = line[:, charmask]          # crop char left and right
        char_vmask = get_mask(char, axis=1)
        char_vmasks = split_mask(char_vmask, minsize=MIN_CHAR_HEIGHT)
        char_vmasks = sort_masks(char_vmasks)

        # if fragmented, select the tallest fragment of char roi or
        # alternatively, use `super=True` in the previous mask split
        #
        # in practice, 'super=True' misses an oportunity to despecle
        # the roi which can confuse the classifier
        char_vmask = char_vmasks[0]
        char = char[char_vmask]    # crop char top and bottom
        chars.append(char)

    return chars


# ------- Start of dataset building helper functions -------
# TBD: documentation
# def get_filenames(folder, regex):
#     pagename_re = re.compile(regex)
#     pages = []
#     page_IDs = []

#     for filename in os.listdir(folder):
#         if (match := pagename_re.match(filename)):
#             page_IDs.append(match.group(1))
#             pagefilename = os.path.join(folder, filename)
#             pages.append(pagefilename)

#     return page_IDs, pages


# def get_img_sig(img):
#     img_string = ' '.join(img.ravel().astype(str))
#     img_string_hashed = hashlib.md5(img_string.encode('utf-8')).hexdigest()

#     return img_string_hashed


# def get_ink_fraction(img):
#     return img.sum() / MAX_INK_VALUE


# def get_outliers(df):
#     idxs = []
#     for scriptstyle in df.scriptstyle.unique():
#         for label in df.label.unique():
#             subdf = df.loc[(df.scriptstyle == scriptstyle) & (df.label == label)]
#             Q1 = subdf.ink_fraction.quantile(0.25)
#             Q3 = subdf.ink_fraction.quantile(0.75)
#             IQR = Q3 - Q1
#             low = Q1 - 1.5 * IQR
#             high = Q3 + 1.5 * IQR
#             idxs.extend(list(subdf.loc[(subdf.ink_fraction < low) | (subdf.ink_fraction > high)].index))

#     return idxs
# ------- End of dataset building helper functions -------
