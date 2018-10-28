
import cv2
from PIL import Image
import pprint
import numpy as np

file = "../../data/images/back.gif"
fg = "#999999"


def _hex_str_to_rgb(colour_str):
    colour_str = colour_str.strip("#")
    r = int(colour_str[0:2], 16)
    g = int(colour_str[2:4], 16)
    b = int(colour_str[4:6], 16)
    return r, g, b


image = Image.open(file)
image.load()
arr = np.array(image)
arr = cv2.cvtColor(arr, cv2.COLOR_GRAY2RGBA)
cv2.imshow("s", arr)
cv2.waitKey()
print(arr)
