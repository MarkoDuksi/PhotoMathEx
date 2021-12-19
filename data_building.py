#!/usr/bin/env python
# coding: utf-8

import os
import re
import hashlib
import numpy as np
import pandas as pd


# for a 20 by 20 unframed char, MAX_INK_VALUE = 20*20*256 = 102000
# frame is black so framing does not change this value
MAX_INK_VALUE = 102_000


# TBD: documentation
def get_filenames(folder, regex):
    pagename_re = re.compile(regex)
    pages = []
    page_IDs = []

    for filename in os.listdir(folder):
        if (match := pagename_re.match(filename)):
            page_IDs.append(match.group(1))
            pagefilename = os.path.join(folder, filename)
            pages.append(pagefilename)

    return page_IDs, pages


def get_img_sig(img):
    img_string = ' '.join(img.ravel().astype(str))
    img_string_hashed = hashlib.md5(img_string.encode('utf-8')).hexdigest()

    return img_string_hashed


def get_ink_fraction(img):
    return img.sum() / MAX_INK_VALUE


def get_outliers(df):
    idxs = []
    for scriptstyle in df.scriptstyle.unique():
        for label in df.label.unique():
            subdf = df.loc[(df.scriptstyle == scriptstyle) & (df.label == label)]
            Q1 = subdf.ink_fraction.quantile(0.25)
            Q3 = subdf.ink_fraction.quantile(0.75)
            IQR = Q3 - Q1
            low = Q1 - 1.5 * IQR
            high = Q3 + 1.5 * IQR
            idxs.extend(list(subdf.loc[(subdf.ink_fraction < low) | (subdf.ink_fraction > high)].index))

    return idxs
