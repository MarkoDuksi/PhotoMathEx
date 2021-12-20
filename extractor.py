#!/usr/bin/env python
# coding: utf-8

import numpy as np
# import cv2 as cv

# set reasonable minimum dimensions for an input image array
# in practice the range is in thousands of pixels
# if providing already cropped images, decrease both accordingly
MIN_IMG_WIDTH = 500
MIN_IMG_HEIGHT = 300

# set a reasonable minimum dimensions for an input char array
# in practice this results in good amount of despecling
MIN_CHAR_WIDTH = 15     # lowest allowable width for "(" and ")"
MIN_CHAR_HEIGHT = 8     # lowest allowable height for "-"
MIN_LINE_HEIGHT = 50    # lowest allowable height for the whole line

# used for calculating custom threshold value
# expressed in units of sigma over the histogram of uint8 values
WHITE_SPREAD = 3


def desaturate(img):
    """Desaturate an RGB or BGR image

    Receive an RGB or BGR image as a 3D uint8 numpy array. Custom
    desaturate by keeping only the value of the darkest pixel in any of
    the channels. White background and black ink are therefore not
    affected but even very bright ink of commonly used colors (namely
    blue and red but also valid for green, cyan, magenta and even yellow)
    in the same image is desaturated to near black to facilitate
    thresholding. Return a single-channel image as a 2D uint8 numpy array.

    Note: Specifically for text detection against a white-balanced
    background this should be the preferred desaturating method followed
    by custom thresholding even (especially) if the intent is to use the
    thresholded result by OpenCV contour detection or similar algorithms.
    """

    return img.min(axis=2)


def autostretch(img, black=None, white=None):
    """Stretch the dynamic range of a single-channel image

    Receive a single-channel image as a 2D uint8 numpy array. By default,
    auto-adjust black and white levels to 0 and 255, respectively,
    stretching linearly the values in between. Custom levels can be
    provided by arguments to `black` and/or `white` parameters. Return a new
    image in original format.
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
    """Threshold a single-channel image to black and white

     Receive a single-channel image as a 2D uint8 numpy array. Apply
     custom parameters based on assumptions of what a histogram of a
     blank paper with some ink on it should look like. Make it
     indifferent to underexposure which is to be commonly expected.
     Return a new image in original format.

     Note: This is a very, very basic implementation but even this
     slight tailoring to text detection purpose yields better results
     than OpenCV implementations.

     TBD: Accommodate for uneven lighting and/or shadows.
    """

    # autostretch it
    img_out = autostretch(img).astype(float)

    # median is a good approximation of the middle "background" value
    # mode was also tested but the difference was negligible
    median = np.median(img_out)

    # std is an indication of unevenness of lighting over the paper
    # ink values are basically outliers
    std = img_out.std()

    # instead of the classic IQR outlier detection, a custom one:
    thresh = max(median - WHITE_SPREAD * std, median / 2)

    # apply the threshold
    img_out[img_out > thresh] = 255
    img_out[img_out <= thresh] = 0

    return img_out.astype(np.uint8)


def get_mask(img, axis=None):
    """Detect regions of interest in a thresholded image

    Receive a thresholded single-channel image as a 2D uint8 numpy array.
    Assuming white background, get a mask vector
    indicating rows or columns (depending on the argument to `axis`)
    that contain any number of non-white pixels. Return the mask vector
    as a 1D boolean numpy array.

    Note: The speed of the implementation allowed for quickly
    processing sheets of characters into >120,000 separate
    characters labeled for training/validating dataset.
    """

    if axis not in (0, 1):
        raise ValueError('missing or invalid argument to `axis`')

    return (img != 255).any(axis=axis)


def split_mask(mask, super=False, minsize=1):
    """Split a multi-roi mask into single-roi submasks

    Receive a mask vector as returned by `get_mask`. Split the possibly
    fragmented mask into discrete masks, each for a single roi. Return a
    list of mask vectors in original format.

    Optionally, if `super` is set to True, return a list with a single
    supermask vector indicating a continuous region of interest
    containing all sub-regions. Such mask cannot be split any further.
    """

    # extend by a single False to accommodate offset by 1
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
            # ignore the subregions smaller than minsize
            if (end_pos - start_pos) < minsize:
                continue
            submask = np.zeros(mask.shape)
            submask[start_pos:end_pos] = 1
            submasks.append(submask.astype(bool))
    else:                 # from the range between the outermost pair
        start_pos = transitions[0]
        end_pos = transitions[-1]
        if (end_pos - start_pos) >= minsize:
            submask = np.zeros(mask.shape)
            submask[transitions[0]:transitions[-1]] = 1
            submasks.append(submask.astype(bool))

    return submasks


def sort_masks(masks, ascending=False):
    """Sort masks by roi size

    Receive a list of mask vectors as returned by `split_mask`. Return
    a new list of mask vectors sorted by size of their respective roi.
    """

    reverse = not ascending
    sorted_masks = sorted(masks, key=lambda x: x.sum(), reverse=reverse)

    return sorted_masks


def extract_lines(img):
    """Line extractor

    Receive an RGB or BGR image as a 3D uint8 numpy array. Return
    top/bottom-cropped blocks of content as a list of single-channel
    black and white images in a 2D uint8 numpy array format.
    """

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
    """Character extractor

    Receive a single image from a list returned by `extract_lines`.
    Return all-around cropped blocks of content as a list of images in
    original format, albeit of expectedly different shape.

    Left out: Return a list of coordinates where each block was detected.
    Note: ask for specifications of "coordinates", ie:
          - rectangular bounding box corners?
          - if so, which two corners?
          - with respect to origin located where?
          - how are the exes defined?
    """

    if line.shape[0] < MIN_LINE_HEIGHT or line.shape[1] < MIN_IMG_WIDTH:
        raise ValueError(f'minimum line dimensions are {MIN_IMG_WIDTH} by {MIN_LINE_HEIGHT}')

    # further subdivide the line into character candidates
    hmask = get_mask(line, axis=0)
    charmasks = split_mask(hmask, minsize=MIN_CHAR_WIDTH)

    if len(charmasks) < 3:
        raise Exception(f'unable to detect at least 3 consecutive characters at least {MIN_CHAR_WIDTH} pixels wide')

    # assume all tokens are captured in this roi as multiple characters
    # and crop the white area around each
    chars = []
    for charmask in charmasks:
        # first crop left and right
        char = line[:, charmask]

        # then mask out empty space above and below
        char_vmask = get_mask(char, axis=1)

        # in case the mask is vertically fragmented
        char_vmasks = split_mask(char_vmask, minsize=MIN_CHAR_HEIGHT)
        char_vmasks = sort_masks(char_vmasks)

        # select the tallest fragment in the roi or alternatively,
        # use `super=True` in the previous mask split
        #
        # Note: In practice, 'super=True' missed the opportunity to
        # despecle the roi and there was at least one instance where
        # a single specle was able to confuse the classifier.
        char_vmask = char_vmasks[0]
        char = char[char_vmask]
        chars.append(char)

    return chars
