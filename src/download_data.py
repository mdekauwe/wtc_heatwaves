#!/usr/bin/env python

"""
Download all of the data from the library at Western Sydney University
"""

import os
import io
import zipfile
import requests

__author__  = "Martin De Kauwe"
__version__ = "1.0 (19.03.2018)"
__email__   = "mdekauwe@gmail.com"

def main():

    url = ("http://hie-pub.westernsydney.edu.au/"
           "07fcd9ac-e132-11e7-b842-525400daae48/"
           "WTC_TEMP-PARRA_HEATWAVE-FLUX-PACKAGE_L1.zip")

    r = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall()

    # clean up
    os.remove("bag-info.txt")
    os.remove("bagit.txt")
    os.remove("manifest-md5.txt")
    os.remove("manifest-sha1.txt")
    os.rename("data", "raw_data")

if __name__== "__main__":

    main()
