#!/usr/bin/env python3

import os
import pickle
import hashlib

import lab
import pytest

TEST_DIRECTORY = os.path.dirname(__file__)


def object_hash(x):
    return hashlib.sha512(pickle.dumps(x)).hexdigest()


def compare_images(result, expected):
    assert set(result.keys()) == {'height', 'width', 'pixels'}, f'Incorrect keys in dictionary'
    assert result['height'] == expected['height'], 'Heights must match'
    assert result['width'] == expected['width'], 'Widths must match'
    assert len(result['pixels']) == result['height']*result['width'], f"Incorrect number of pixels, expected {result['height']*result['width']}"
    num_incorrect_val = 0
    first_incorrect_val = None
    num_bad_type = 0
    first_bad_type = None
    num_bad_range = 0
    first_bad_range = None

    row, col = 0, 0
    correct_image = True
    for index, (res, exp) in enumerate(zip(result['pixels'], expected['pixels'])):
        if not isinstance(res, int):
            correct_image = False
            num_bad_type += 1
            if not first_bad_type:
                first_bad_type = f'Pixels must all be integers!'
                first_bad_type += f'\nPixel had value {res} at index {index} (row {row}, col {col}).'
        if res < 0 or res > 255:
            num_bad_range += 1
            correct_image = False
            if not first_bad_range:
                first_bad_range = f'Pixels must all be in the range from [0, 255]!'
                first_bad_range += f'\nPixel had value {res} at index {index} (row {row}, col {col}).'
        if res != exp:
            correct_image = False
            num_incorrect_val += 1
            if not first_incorrect_val:
                first_incorrect_val = f'Pixels must match'
                first_incorrect_val += f'\nPixel had value {res} but expected {exp} at index {index} (row {row}, col {col}).'

        if col + 1 == result["width"]:
            col = 0
            row += 1
        else:
            col += 1

    msg = "Image is correct!"
    if first_bad_type:
        msg = first_bad_type + f"\n{num_bad_type} pixel{'s'*int(num_bad_type>1)} had this problem."
    elif first_bad_range:
        msg = first_bad_range + f"\n{num_bad_range} pixel{'s'*int(num_bad_range>1)} had this problem."
    elif first_incorrect_val:
        msg = first_incorrect_val + f"\n{num_incorrect_val} pixel{'s'*int(num_incorrect_val>1)} had incorrect value{'s'*int(num_incorrect_val>1)}."

    assert correct_image, msg


def test_load():
    result = lab.load_greyscale_image(os.path.join(TEST_DIRECTORY, 'test_images', 'centered_pixel.png'))
    expected = {
        'height': 11,
        'width': 11,
        'pixels': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 255, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    compare_images(result, expected)

def test_get_pixel():
    im = {
        'height':1,
        'width': 4,
        'pixels': [18,76, 135, 203]
    }

    result1 = lab.get_pixel(im, 0, 2)
    expected1 = 135
    # result2 = lab.get_pixel(im, 1,0)
    # expected2 = IndexError

    assert result1 == expected1
    # assert result2 == expected2

def test_inverted_1():
    im = lab.load_greyscale_image(os.path.join(TEST_DIRECTORY, 'test_images', 'centered_pixel.png'))
    result = lab.inverted(im)
    expected = {
        'height': 11,
        'width': 11,
        'pixels': [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 0, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255],
    }
    compare_images(result, expected)



def test_inverted_2():
    im = {
        'height':1,
        'width': 4,
        'pixels': [18,76, 135, 203]
    }
    result = lab.inverted(im)
    expected = {
        'height': 1,
        'width':4,
        'pixels': [237, 179, 120, 52]
    }
    compare_images(result, expected)

@pytest.mark.parametrize("fname", ['mushroom', 'twocats', 'chess'])
def test_inverted_images(fname):
    inpfile = os.path.join(TEST_DIRECTORY, 'test_images', '%s.png' % fname)
    expfile = os.path.join(TEST_DIRECTORY, 'test_results', '%s_invert.png' % fname)
    im = lab.load_greyscale_image(inpfile)
    oim = object_hash(im)
    result = lab.inverted(im)
    expected = lab.load_greyscale_image(expfile)
    assert object_hash(im) == oim, 'Be careful not to modify the original image!'
    compare_images(result, expected)


@pytest.mark.parametrize("kernsize", [1, 3, 7])
@pytest.mark.parametrize("fname", ['mushroom', 'twocats', 'chess'])
def test_blurred_images(kernsize, fname):
    inpfile = os.path.join(TEST_DIRECTORY, 'test_images', '%s.png' % fname)
    expfile = os.path.join(TEST_DIRECTORY, 'test_results', '%s_blur_%02d.png' % (fname, kernsize))
    input_img = lab.load_greyscale_image(inpfile)
    input_hash = object_hash(input_img)
    result = lab.blurred(input_img, kernsize)
    expected = lab.load_greyscale_image(expfile)
    assert object_hash(input_img) == input_hash, "Be careful not to modify the original image!"
    compare_images(result, expected)

def test_blurred_black_image():
    # REPLACE THIS with your 1st test case from section 5.1
    k_size1 = 3
    k_size2 = 7
    pixels = [0]*(6*5) #0 for black pixels
    im = {'height':6, 'width':5, 'pixels':pixels}
    compare_images(im, lab.blurred(im, k_size1))



def test_blurred_centered_pixel():
    # REPLACE THIS with your 2nd test case from section 5.1
    k_size1 = 3
    k_size2 = 7
    im = lab.load_greyscale_image('test_images/centered_pixel.png')
    im_blurred_1 = lab.blurred(im, k_size1)
    expected1 = {'height': im['height'],
                 'width': im['width'],
                 'pixels': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 28, 28, 28, 0, 0, 0, 0,
                            0, 0, 0, 0, 28, 28, 28, 0, 0, 0, 0,
                            0, 0, 0, 0, 28, 28, 28, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}
    im_blurred_2 = lab.blurred(im, k_size2)
    expected2 = {'height': im['height'],
                 'width': im['width'],
                 'pixels': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                            0, 0, 5, 5, 5, 5, 5, 5, 5, 0, 0,
                            0, 0, 5, 5, 5, 5, 5, 5, 5, 0, 0,
                            0, 0, 5, 5, 5, 5, 5, 5, 5, 0, 0,
                            0, 0, 5, 5, 5, 5, 5, 5, 5, 0, 0,
                            0, 0, 5, 5, 5, 5, 5, 5, 5, 0, 0,
                            0, 0, 5, 5, 5, 5, 5, 5, 5, 0, 0,
                            0, 0, 5, 5, 5, 5, 5, 5, 5, 0, 0,
                            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}

    compare_images(expected1, im_blurred_1)
    compare_images(expected2, im_blurred_2)

@pytest.mark.parametrize("kernsize", [1, 3, 9])
@pytest.mark.parametrize("fname", ['mushroom', 'twocats', 'chess'])
def test_sharpened_images(kernsize, fname):
    inpfile = os.path.join(TEST_DIRECTORY, 'test_images', '%s.png' % fname)
    expfile = os.path.join(TEST_DIRECTORY, 'test_results', '%s_sharp_%02d.png' % (fname, kernsize))
    input_img = lab.load_greyscale_image(inpfile)
    input_hash = object_hash(input_img)
    result = lab.sharpened(input_img, kernsize)
    expected = lab.load_greyscale_image(expfile)
    assert object_hash(input_img) == input_hash, "Be careful not to modify the original image!"
    compare_images(result, expected)


@pytest.mark.parametrize("fname", ['mushroom', 'twocats', 'chess'])
def test_edges_images(fname):
    inpfile = os.path.join(TEST_DIRECTORY, 'test_images', '%s.png' % fname)
    expfile = os.path.join(TEST_DIRECTORY, 'test_results', '%s_edges.png' % fname)
    input_img = lab.load_greyscale_image(inpfile)
    input_hash = object_hash(input_img)
    result = lab.edges(input_img)
    expected = lab.load_greyscale_image(expfile)
    assert object_hash(input_img) == input_hash, "Be careful not to modify the original image!"
    compare_images(result, expected)

def test_edges_centered_pixel():
    # REPLACE THIS with your test case from section 6
    im = lab.load_greyscale_image('test_images/centered_pixel.png')
    im_edges = lab.edges(im)
    expected = {'height': im['height'], 
                'width': im['width'],
                'pixels':  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 255, 255, 255, 0, 0, 0, 0,
                            0, 0, 0, 0, 255, 0, 255, 0, 0, 0, 0,
                            0, 0, 0, 0, 255, 255, 255, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}
    
    compare_images(im_edges, expected)