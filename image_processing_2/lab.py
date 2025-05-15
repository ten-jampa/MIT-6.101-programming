#!/usr/bin/env python3

"""
6.101 Lab:
Image Processing 2
"""

# NO ADDITIONAL IMPORTS!
# (except in the last part of the lab; see the lab writeup for details)
import math
import os

# import typing  # optional import
from PIL import Image

# COPY THE FUNCTIONS THAT YOU IMPLEMENTED IN IMAGE PROCESSING PART 1 BELOW!

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


# VARIOUS FILTERS


def decompose_color_im(image):
    """_Helper function to decompose a color image
    into three single color images
    """
    height = image["height"]
    width = image["width"]
    red_pixels = [rgb[0] for rgb in image["pixels"]]
    green_pixels = [rgb[1] for rgb in image["pixels"]]
    blue_pixels = [rgb[2] for rgb in image["pixels"]]

    r_im = {"height": height, "width": width, "pixels": red_pixels}
    g_im = {"height": height, "width": width, "pixels": green_pixels}
    b_im = {"height": height, "width": width, "pixels": blue_pixels}

    return r_im, g_im, b_im


def compose_color_im(r_im, g_im, b_im):
    """Helper function that composes three single valuued image
    into a color image.
    """
    height = r_im["height"]
    width = r_im["width"]
    red_pixels = [red for red in r_im["pixels"]]
    green_pixels = [green for green in g_im["pixels"]]
    blue_pixels = [blue for blue in b_im["pixels"]]
    #
    return {
        "height": height,
        "width": width,
        "pixels": [(r, g, b) for r, g, b in zip(red_pixels, green_pixels, blue_pixels)],
    }


def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """

    def make_filter(image):
        r_im, g_im, b_im = decompose_color_im(image)
        # invert them
        inv_r_im = filt(r_im)
        inv_g_im = filt(g_im)
        inv_b_im = filt(b_im)
        # combine them
        out_im = compose_color_im(inv_r_im, inv_g_im, inv_b_im)
        return out_im

    return make_filter


def make_blur_filter(kernel_size):
    """Given a kernel size, returns a blur filter"""
    def apply_blur_filter(image):
        blurred_im = blurred(image, kernel_size)
        return blurred_im

    return apply_blur_filter


def make_sharpen_filter(kernel_size):
    """Given a kernel size, returns a blur filter"""
    def apply_sharp_filter(image):
        sharpened_im = sharpened(image, kernel_size)
        return sharpened_im

    return apply_sharp_filter


def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """

    def great_filter(image):
        for filter in filters:
            image = filter(image)
        return image

    return great_filter


# SEAM CARVING

# Main Seam Carving Implementation


def seam_carving(image, ncols):
    """
    Starting from the given image, use the seam carving technique to remove
    ncols (an integer) columns from the image. Returns a new image.
    """
    out_image = {
        "height": image["height"],
        "width": image["width"],
        "pixels": image["pixels"],
    }

    for count in range(ncols):
        # print_color_values(out_image)
        work_image = greyscale_image_from_color_image(out_image)
        # print_greyscale_values(work_image)
        energy_map = compute_energy(work_image)
        # print_greyscale_values(energy_map)
        cum_energy_map = cumulative_energy_map(energy_map)
        # print_greyscale_values(cum_energy_map)
        seam = minimum_energy_seam(cum_energy_map)
        # print(seam)
        # back to the colored form
        out_image = image_without_seam(out_image, seam)
        # print_color_values(out_image)
        if (count + 1) % 3 == 0:
            print(f"Removed {count+1} columns")
    return out_image


# Optional Helper Functions for Seam Carving


def greyscale_image_from_color_image(image):
    """
    Given a color image, computes and returns a corresponding greyscale image.

    Returns a greyscale image (represented as a dictionary).
    """
    height = image["height"]
    width = image["width"]
    pixels = [round(0.299 * r + 0.587 * g + 0.114 * b) for r, g, b in image["pixels"]]

    return {"height": height, "width": width, "pixels": pixels}


def compute_energy(grey):
    """
    Given a greyscale image, computes a measure of "energy", in our case using
    the edges function from last week.

    Returns a greyscale image (represented as a dictionary).
    """
    energy_map = edges(grey)
    return energy_map


def min_adjacent(cem, row, col):
    """Given an energy map (same structure as a greyscale image),
        compute the min energy in cells adjacent to the cell at (row, col)

    Returns:
        int: pixel value
    """
    height = cem["height"]
    width = cem["width"]

    min_val = get_pixel_extend(cem, row - 1, col - 1)
    min_index = row - 1, col - 1
    for i in range(2):
        val = get_pixel_extend(cem, row - 1, col + i)
        if val < min_val:
            min_val = val
            min_index = row - 1, col + i
        else:
            continue

    return min_val, min_index


def cumulative_energy_map(energy):
    """
    Given a measure of energy (e.g., the output of the compute_energy
    function) greyscale image, computes a "cumulative energy map" as described
    in the lab 2 writeup.

    Returns a dictionary with 'height', 'width', and 'pixels' keys (but where
    the values in the 'pixels' array may not necessarily be in the range [0,
    255].
    """
    height = energy["height"]
    width = energy["width"]
    cum_energy_map = {
        "height": height,
        "width": width,
        "pixels": [0] * (height * width),
    }
    cem_pixels = cum_energy_map["pixels"]

    for row in range(height):
        for col in range(width):
            # we have a particular cell now
            index = row * width + col
            cum_energy = get_pixel(energy, row, col)
            min_cum_energy, _ = min_adjacent(cum_energy_map, row, col)
            cum_energy += min_cum_energy
            cem_pixels[index] = cum_energy
    return cum_energy_map


def minimum_energy_seam(cem):
    """
    Given a cumulative energy map dictionary, returns a list of the indices into
    the 'pixels' list that correspond to pixels contained in the minimum-energy
    seam (computed as described in the lab 2 writeup).
    """
    seam = []
    height = cem["height"]
    width = cem["width"]

    # find the min_value and index in the bottom row
    row = height - 1
    min_val = float("inf")
    min_index = row, 0
    for col in range(width):
        val = get_pixel(cem, row, col)
        if val < min_val:
            min_val = val
            min_index = row, col
    seam.insert(
        0, min_index[0] * width + min_index[1]
    )  # finding the min_index on the bottom row

    # Now find the next step:
    for row in reversed(range(0, height - 1)):
        # specifying the new search range
        mid_col = min_index[1]
        if mid_col == 0:
            start_col, stop_col = mid_col, mid_col + 2
        elif mid_col == width - 1:
            start_col, stop_col = mid_col - 1, mid_col + 1
        else:
            start_col, stop_col = mid_col - 1, mid_col + 2
        # search for the min value and the index
        min_val = float("inf")
        for col in range(start_col, stop_col):
            val = get_pixel(cem, row, col)
            if val < min_val:
                min_val = val
                min_index = row, col
        seam.insert(0, min_index[0] * width + min_index[1])
        # print(seam)

    return seam


def image_without_seam(image, seam):
    """
    Given a (color) image and a list of indices to be removed from the image,
    return a new image (without modifying the original) that contains all the
    pixels from the original image except those corresponding to the locations
    in the given list.
    """
    height = image["height"]
    width = image["width"] - 1

    out_pixels = []
    for i, val in enumerate(image["pixels"]):
        if i in seam:
            continue
        else:
            out_pixels.append(val)

    return {"height": height, "width": width, "pixels": out_pixels}


## Custom Functions + shapes inside a draw object
## What do I want to do?


class Draw:
    """Creates a draw object which is an image where
    you can repeatedly draw shapes on.
    """

    def __init__(self, image):
        self.image = {
            "height": image["height"],
            "width": image["width"],
            "pixels": image["pixels"][:],
        }
        self.height = image["height"]
        self.width = image["width"]

    def get_image(self):
        """Returns the image"""
        return self.image

    def vline(self, color, x0, y0, y1, thick=True):
        """Draws a vertical line from (x0,y0) to (x1,y1)
        If thickness is set to true, the line is drawn in a thickly manner
        """
        image = self.image
        for yi in range(min(y0, y1), max(y0, y1) + 1):
            if thick:
                for delta in range(-3, 3):
                    set_pixel(image, yi, x0 + delta, color)
            else:
                set_pixel(image, yi, x0, color)

    def hline(self, color, x0, y0, x1, thick=True):
        """Draws a horizontal line from (x0,y0)
        to (x0, y1). Thickness = True for thicker lines
        """
        image = self.image
        for xi in range(min(x0, x1), max(x0, x1) + 1):
            if thick:
                for delta in range(-3, 3):
                    set_pixel(image, y0 + delta, xi, color)
            else:
                set_pixel(image, y0, xi, color)

    def circle(self, color, radius, center, only_outline=False):
        """Draws a circle object of some radius at some center"""
        image = self.image
        height = image["height"]
        width = image["width"]
        x0, y0 = center
        epsilon = 64
        # Only loop over the square that could contain the circle
        for y in range(max(0, y0 - radius), min(height, y0 + radius + 1)):
            for x in range(max(0, x0 - radius), min(width, x0 + radius + 1)):
                # Check if point is within circle
                if only_outline:
                    if (x - x0) ** 2 + (y - y0) ** 2 in range(
                        radius**2 - epsilon, radius**2 + epsilon + 1
                    ):  # within some error range
                        # Calculate 1D index from 2D coordinates
                        set_pixel(image, y, x, color)
                else:
                    # print(f'(x-x0)^2 + (y-y0)^2 = {(x - x0)**2 + (y - y0)**2}')
                    if (x - x0) ** 2 + (y - y0) ** 2 <= radius**2:
                        # Calculate 1D index from 2D coordinates
                        set_pixel(image, y, x, color)

    def rectangle(self, start, color, length, breadth):
        """_draws a rectangle object"""
        image = self.image
        height = self.image["height"]
        width = self.image["width"]
        x0, y0 = start  # left upper corner

        # confine the rectangle:
        for xi in range(x0, x0 + breadth + 1):
            for yi in range(y0, y0 + length + 1):
                set_pixel(image, yi, xi, color)


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


def print_color_values(image):
    """
    Given a color image dictionary, prints a string representation of the
    image pixel values to the terminal. This function may be helpful for
    manually testing and debugging tiny image examples.

    Note that RGB values will be rounded to the nearest int.
    """
    out = f"Color image with {image['height']} rows"
    out += f" and {image['width']} columns:\n"
    space_sizes = {}
    space_vals = []

    col = 0
    for pixel in image["pixels"]:
        for color in range(3):
            val = str(round(pixel[color]))
            space_vals.append((col, color, val))
            space_sizes[(col, color)] = max(len(val), space_sizes.get((col, color), 0))
        if col == image["width"] - 1:
            col = 0
        else:
            col += 1

    for col, color, val in space_vals:
        space_val = val.center(space_sizes[(col, color)])
        if color == 0:
            out += f" ({space_val}"
        elif color == 1:
            out += f" {space_val} "
        else:
            out += f"{space_val})"
        if col == image["width"] - 1 and color == 2:
            out += "\n"
    print(out)


def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
    i = load_color_image('test_images/cat.png')
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img = img.convert("RGB")  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        width, height = img.size
        return {"height": height, "width": width, "pixels": pixels}


def save_color_image(image, filename, mode="PNG"):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    # make folders if they do not exist
    path, _ = os.path.split(filename)
    if path and not os.path.exists(path):
        os.makedirs(path)

    # save image in folder specified (by default the current folder)
    out = Image.new(mode="RGB", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns an instance of this class
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
    i = load_greyscale_image('test_images/cat.png')
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
    by the 'mode' parameter.
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

    # 1.
    # cat = load_color_image('test_images/cat.png')
    # color_inv = color_filter_from_greyscale_filter(inverted)
    # inverted_color_cat = color_inv(cat)
    # save_color_image(inverted_color_cat, 'submissions/inv_color_cat.png')

    # 2.
    # python = load_color_image('test_images/python.png')
    # blur_color_im = color_filter_from_greyscale_filter(make_blur_filter(9))
    # blurred_python = blur_color_im(python)
    # save_color_image(blurred_python, 'submissions/blurred_python.png')

    # 3.
    # sparrowchick = load_color_image('test_images/sparrowchick.png')
    # sharpen_color_im = color_filter_from_greyscale_filter(make_sharpen_filter(7))
    # sharpened_sparrowchick = sharpen_color_im(sparrowchick)
    # save_color_image(sharpened_sparrowchick, 'submissions/sharp_sparrowchick.png')

    # 4.
    # frog = load_color_image('test_images/frog.png')
    # filter1 = color_filter_from_greyscale_filter(edges)
    # filter2 = color_filter_from_greyscale_filter(make_blur_filter(5))
    # filt = filter_cascade([filter1, filter1, filter2, filter1])
    # frog_filtered = filt(frog)
    # save_color_image(frog_filtered, 'submissions/frog_filtered.png')

    # 5. Debuggin Seam carving
    # pattern = load_color_image('test_images/pattern.png')
    # seamed_pattern = seam_carving(pattern, 1)

    # 6. seam_carving_tests
    # energy = {
    # 'width': 9,
    # 'height': 4,
    # 'pixels': [160, 160,  0, 28,  0, 28,  0, 160, 160,
    #             255, 218, 10, 22, 14, 22, 10, 218, 255,
    #             255, 255, 30,  0, 14,  0, 30, 255, 255,
    #             255, 255, 31, 22,  0, 22, 31, 255, 255]
    #             }
    # result = cumulative_energy_map(energy)
    # expected = {
    #     'width': 9,
    #     'height': 4,
    #     'pixels': [160, 160,  0, 28,  0, 28,  0, 160, 160,
    #                415, 218, 10, 22, 14, 22, 10, 218, 415,
    #                473, 265, 40, 10, 28, 10, 40, 265, 473,
    #                520, 295, 41, 32, 10, 32, 41, 295, 520]
    # }
    # print_greyscale_values(expected)
    # print_greyscale_values(result)
    # seam = minimum_energy_seam(result)
    # print(seam)

    # # #7.
    # twocats = load_color_image('test_images/twocats.png')
    # seamed_cat = seam_carving(twocats, 100)
    # save_color_image(seamed_cat, 'submissions/seamed_twocat.png')

    # # 8.
    # color__ = (244, 100, 110)
    # tree = load_color_image('test_images/tree.png')
    # # #print_color_values(tree)

    # #let's try to draw a human face
    # draw_on_tree = Draw(tree)

    # #the colors we will working with
    # face_color = (220, 180, 150)
    # eye_color = (136, 104, 73)
    # nose_color = (255, 0, 0)
    # mouth_color = (0,0,0)
    # hair_color = mouth_color

    # #let's draw our base face
    # draw_on_tree.circle(face_color, 64, (150, 100))
    # #let's draw our smaller eyes
    # draw_on_tree.circle(eye_color, 14, (120, 90))
    # draw_on_tree.circle(eye_color, 14, (178, 91))
    # #let's draw our nose
    # draw_on_tree.rectangle((147,110), nose_color, 7,7)
    # #let's draw our mouth
    # draw_on_tree.hline(mouth_color, 130, 134, 178)
    # #let's draw some hair
    # for xi in range(150-50, 150+50,2):
    #     draw_on_tree.vline(hair_color, xi, 20, 65, thick = True)
    # save_color_image(draw_on_tree.get_image(), 'face_on_tree.png')

    # #print_color_values(tree_circle)

    # save_color_image(tree_square, 'submissions/tree_square.png')

    # 9.
    # twocats = load_color_image('test_images/twocats.png')
    # added_cat = seam_adding(twocats, ncols = 25)
    # save_color_image(added_cat, 'submissions/added_twocat.png')
    pass