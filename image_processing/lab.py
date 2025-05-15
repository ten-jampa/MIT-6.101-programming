#!/usr/bin/env python3

"""
6.101 Lab:
Image Processing
"""

import math
import os
from PIL import Image

# NO ADDITIONAL IMPORTS ALLOWED!


# The base get_pixel function


def get_pixel(image, row, col):
    """The function takes in a grey-scale image dictionary and returns
    the pixel value at (row +1) and col+1); The function assumes that
    the row and col given in the function maps onto a proper index.

    Args:
        image (dict): grey-scale image dictionary
        row (int)
        col (int)
        OOB (str): A parameter for out of bound behavior



    Returns:
        int: The pixel value of the image at the targeted place
    """
    width = image["width"]
    index = row * width + col
    return image["pixels"][index]


# Some helper functions


def get_pixel_zero(image, row, col):
    """Given an image object with row and col specified,
    returns the pixel value at the row, and column
    according to the zero rule.

    Returns:
        int: Pixel value
    """
    height = image["height"]
    width = image["width"]
    if row not in range(height):
        return 0
    elif col not in range(width):
        return 0
    else:
        return get_pixel(image, row, col)


def get_pixel_extend(image, row, col):
    """
    Given the row, col, and the image,
    returns the value of the pixel at row, col
    by the extend rule.

    Returns:
        int: pixel value
    """
    height = image["height"]
    width = image["width"]
    # out of bound behavoir
    if row < 0:
        row = max(row, 0)
    elif row > (height - 1):
        row = min(row, height - 1)

    if col < 0:
        col = max(col, 0)
    elif col > (width - 1):
        col = min(col, width - 1)

    return get_pixel(image, row, col)


def get_pixel_wrap(image, row, col):
    """Given row, col, and the image,
    this function returns the pixel value
    while following the wrap rule.

    returns:
        int: pixel value
    """
    height = image["height"]
    width = image["width"]
    row = row % (height)
    col = col % (width)

    return get_pixel(image, row, col)


def get_pixel_general(image, row, col, boundary_behavoir="extend"):
    """The wrapper get_pixel function that takes in
        image, row, col and the boundary behavoir it must follow.
        If boundary behavoir is not given, the extend rule is
        used as default.

    Returns:
        int: Pixel Value
    """
    if boundary_behavoir == "zero":
        return get_pixel_zero(image, row, col)
    elif boundary_behavoir == "extend":
        return get_pixel_extend(image, row, col)
    elif boundary_behavoir == "wrap":
        return get_pixel_wrap(image, row, col)
    else:
        raise ValueError("You have not provided a legitimate boundary")


def set_pixel(image, row, col, color):
    """Given an image, it reassigns the pixel value at the row, col given
    to be the color value provided.
    """

    width = image["width"]
    height = image["height"]
    # just
    if col >= width:
        raise IndexError(
            f"The col {col} exceeds the width {width} of the image provided"
        )
    elif row >= height:
        raise IndexError(
            f"The row {row} exceeds the height {height} of the image provided"
        )
    index = row * width + col
    image["pixels"][index] = color


def apply_per_pixel(image, func, boundary_behavoir="extend"):
    """for a given image, the function applies
    the given function to each of the pixel
    values and returns a new image
    """
    result = {
        "height": image["height"],
        "width": image["width"],
        "pixels": image["pixels"][:],  # shallow copy
    }
    for row in range(image["height"]):
        for col in range(image["width"]):
            curr_color = get_pixel_general(image, row, col, boundary_behavoir)
            new_color = func(curr_color)
            set_pixel(result, row, col, new_color)
    return result


def inverted(image):
    """For a given image, this function inverts
    the pixel values such that black bepytcomes
    white and vice versa
    """
    return apply_per_pixel(image, lambda color: 255 - color)


def extract_subimage_matrix(image, row, col, kernel, boundary_behavoir):
    """This is a helper function to extract
    the sub_marix from an image for the correlation
    calculation/kernel calculation while following a
    specified OOB( Out of boundary behavoir)
    """

    sub_im = []
    # kernel will be represented using a dictionary
    width = kernel["width"]
    height = kernel["height"]
    mid_width = width // 2
    mid_height = height // 2
    for r in range(row - mid_height, row + mid_height + 1):
        for c in range(col - mid_width, col + mid_width + 1):
            pixel = get_pixel_general(image, r, c, boundary_behavoir)
            sub_im.append(pixel)
    return sub_im


def correlate(image, kernel, boundary_behavior):
    """
    Compute the result of correlating the given image with the given kernel.
    `boundary_behavior` will one of the strings "zero", "extend", or "wrap",
    and this function will treat out-of-bounds pixels as having the value zero,
    the value of the nearest edge, or the value wrapped around the other edge
    of the image, respectively.

    if boundary_behavior is not one of "zero", "extend", or "wrap", return
    None.

    Otherwise, the output of this function should have the same form as a 6.101
    image (a dictionary with "height", "width", and "pixels" keys), but its
    pixel values do not necessarily need to be in the range [0,255], nor do
    they need to be integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    DESCRIBE YOUR KERNEL REPRESENTATION HERE
    The kernel representation is similar to the image representation in that
    it uses a dictionary with three keys (height, width, values). Height and
    Values specification so that the most general shaped kernel is possible.
    The values will be a list that will be the 2d matrix flattened into 1d
    which can be retrieved in much the same manner as we do with the image pixel
    values.
    """

    acceptable_behavoir = ["zero", "extend", "wrap"]
    if boundary_behavior not in acceptable_behavoir:
        return None

    correlated_pixels = []
    im_height = image["height"]
    im_width = image["width"]

    # kernel represented using dictionaries
    ker_values = kernel["values"]

    for row in range(im_height):
        for col in range(im_width):
            # extract the sub_image matrix for the row and col
            sub_im = extract_subimage_matrix(image, row, col, kernel, boundary_behavior)
            correlated_pixels.append(
                sum([im_val * ker_val for im_val, ker_val in zip(sub_im, ker_values)])
            )

    return {"height": im_height, "width": im_width, "pixels": correlated_pixels}

def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the "pixels" list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    pixels = image["pixels"][:]  # shallow to create a new image entirely
    for i, pixel in enumerate(pixels):
        # round
        pixel = round(pixel)
        # clipping
        if pixel < 0:
            pixel = 0
        elif pixel > 255:
            pixel = 255
        pixels[i] = pixel

    return {"height": image["height"], "width": image["width"], "pixels": pixels}


# FILTERS
def create_blur_kernel(kernel_size):
    """Given a kernel size n, the function prepares
    the n x n blurring kernel where the values of the kernel
    are all identical and sum up to 1."""

    ker_values = [1 / kernel_size**2] * (kernel_size * kernel_size)
    return {"height": kernel_size, "width": kernel_size, "values": ker_values}


def blurred(image, kernel_size, boundary_behavior="extend", clipped=True):
    """
    Return a new image representing the result of applying a box blur (with the
    given kernel size) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    boundary behavoir: Defaults to extend

    clipped: extra parameter to clarify whether the function should
    return a rounded_and_clipped image or not. The parameter makes it
    versatile to be called in the sharpened function. Defaults to True.
    """
    if clipped:
        blur_kernel = create_blur_kernel(kernel_size)
        blurred_im = correlate(image, blur_kernel, boundary_behavior)
        blurred_im = round_and_clip_image(blurred_im)
        return blurred_im
    else:
        blur_kernel = create_blur_kernel(kernel_size)
        blurred_im = correlate(image, blur_kernel, boundary_behavior)
        return blurred_im


def sharpened(image, kernel_size, clipped=True):
    """Given an image, and a kernel size, the function
    returns a new image that is sharpened!

    clipped: extra argument to specify whether we want
    a rounded and clipped image to be returned. Defaults to
    True.
    """
    height = image["height"]
    width = image["width"]
    im_pixels = image["pixels"]
    blurred_image = blurred(image, kernel_size, clipped=False)
    blur_pixels = blurred_image["pixels"]
    sharpened_pixels = []
    for im_val, blur_val in zip(im_pixels, blur_pixels):
        sharpened_pixels.append(2 * im_val - blur_val)

    sharpened_im = {"height": height, "width": width, "pixels": sharpened_pixels}

    if clipped:
        sharpened_im = round_and_clip_image(sharpened_im)
    return sharpened_im


def edges(image, save_intermediates=False):
    """Given an image, this function finds the edges in the image
    and returns the edges image.
    """
    # kernel values
    ker1 = {"height": 3, "width": 3, "values": [-1, -2, -1, 0, 0, 0, 1, 2, 1]}
    ker2 = {"height": 3, "width": 3, "values": [-1, 0, 1, -2, 0, 2, -1, 0, 1]}

    # intermediate images
    im1 = correlate(image, ker1, "extend")
    im2 = correlate(image, ker2, "extend")

    # if you want to save the intermideriate images:
    if save_intermediates:
        save_greyscale_image(im1, "edge_1.png")
        save_greyscale_image(im2, "edge_2.png")

    edge_pixels = []
    for im1_val, im2_val in zip(im1["pixels"], im2["pixels"]):
        edge_pixel = math.sqrt(im1_val**2 + im2_val**2)
        edge_pixels.append(edge_pixel)

    edge_im = {
        "height": image["height"],
        "width": image["width"],
        "pixels": edge_pixels,
    }

    return round_and_clip_image(edge_im)


# HELPER FUNCTIONS FOR DISPLAYING, LOADING, AND SAVING IMAGES


def print_greyscale_values(image):
    """
    Given a greyscale image dictionary, prints a string representation of the
    image pixel values to the terminal. This function may be helpful for
    manually testing and debugging tiny image examples.

    Note that pixel values that are floats will be rounded to the nearest int.
    """
    out = f"Greyscale image with {image['height']} rows"
    out += f" and {image['width']} columns:\n "
    space_sizes = {}
    space_vals = []

    col = 0
    for pixel in image["pixels"]:
        val = str(round(pixel))
        space_vals.append((col, val))
        space_sizes[col] = max(len(val), space_sizes.get(col, 2))
        if col == image["width"] - 1:
            col = 0
        else:
            col += 1

    for col, val in space_vals:
        out += f"{val.center(space_sizes[col])} "
        if col == image["width"] - 1:
            out += "\n "
    print(out)


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image("test_images/cat.png")
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith("RGB"):
            pixels = [
                round(0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]) for p in img_data
            ]
        elif img.mode == "LA":
            pixels = [p[0] for p in img_data]
        elif img.mode == "L":
            pixels = list(img_data)
        else:
            raise ValueError(f"Unsupported image mode: {img.mode}")
        width, height = img.size
        return {"height": height, "width": width, "pixels": pixels}


def save_greyscale_image(image, filename, mode="PNG"):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the "mode" parameter.
    """
    # make folders if they do not exist
    path, _ = os.path.split(filename)
    if path and not os.path.exists(path):
        os.makedirs(path)

    # save image in folder specified (by default the current folder)
    out = Image.new(mode="L", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.

    # 1. Inverted Bluegill
    # bluegill = load_greyscale_image('test_images/bluegill.png')
    # inv_bluegill = inverted(bluegill)
    # save_greyscale_image(inv_bluegill, 'submission/inv_bluegill.png')

    # # 2. Correlation test with pigbird
    # kernel_values = [0] * (13 * 13)
    # kernel_values[26] = 1
    # test_kernel = {"height": 13, "width": 13, "values": kernel_values}
    # pigbird = load_greyscale_image('test_images/pigbird.png')

    # # 2.1. With zero behavoir
    # pig_bird_zero = correlate(pigbird, test_kernel, 'zero')
    # save_greyscale_image(pig_bird_zero, 'submissions/pigbird_zero.png')

    # # 2.1. With extend behavoir
    # pig_bird_extend = correlate(pigbird, test_kernel, 'extend')
    # save_greyscale_image(pig_bird_extend, 'submissions/pigbird_extend.png')

    # # 2.1. With wrap behavoir
    # pig_bird_wrap = correlate(pigbird, test_kernel, 'wrap')
    # save_greyscale_image(pig_bird_wrap, 'submissions/pigbird_wrap.png')

    # # 3. Blurred Cat
    # cat = load_greyscale_image('test_images/cat.png')
    # cat_blur_extend = blurred(cat, 13, 'extend')
    # cat_blur_zero = blurred(cat, 13, 'zero')
    # cat_blur_wrap = blurred(cat, 13, 'wrap')
    # save_greyscale_image(cat_blur_extend, 'submissions/cat_blurred_extend.png')
    # save_greyscale_image(cat_blur_zero, 'submissions/cat_blurred_zero.png')
    # save_greyscale_image(cat_blur_wrap, 'submissions/cat_blurred_wrap.png')

    # #4. Sharpened

    # python = load_greyscale_image('test_images/python.png')
    # python_sharpened = sharpened(python, 11)
    # save_greyscale_image(python_sharpened, 'submissions/python_sharpened.png')

    # #5. Edges of Construction;

    # construct = load_greyscale_image('test_images/construct.png')
    # construct_edges = edges(construct)
    # save_greyscale_image(construct_edges, 'submissions/construct_edges.png')

    print("End of Lab")
