"""
6.101 Lab:
Audio Processing
"""

import wave
import struct

# No additional imports allowed!


def backwards(sound):
    """
    Returns a new sound containing the samples of the original in reverse
    order, without modifying the input sound.

    Args:
        sound: a dictionary representing the original mono sound

    Returns:
        A new mono sound dictionary with the samples in reversed order
    """
    sample_rate = sound["rate"]
    samples = sound["samples"][:]
    rev_samples = samples[::-1] 
    rev_sound = {"rate": sample_rate, "samples": rev_samples}
    return rev_sound


def mix(sound1, sound2, p):
    """
    The function mixes two sound dictionaries together
    to create a new sound dictionary.
    Args:
        sound1 (dict): a sound dictionary with parameters: rate and samples
        sound2 (dict): a sound dictionary with parameters: rate and samples
        p (float): mixing parameter 0<= p <= 1
    Returns:
        mix_sound (dict): mixed sound
    """
    # mix 2 good sounds
    if sound1["rate"] != sound2["rate"]:
        return None

    mixed_rate = sound1["rate"]  # get rate
    sound1 = sound1["samples"]
    sound2 = sound2["samples"]

    dur1, dur2 = len(sound1), len(sound2)
    max_dur = max(dur1, dur2)

    mixed_samples = []
    if dur1 == max_dur:
        for samp1, samp2 in zip(sound1, sound2):
            mixed_sample = p * samp1 + (1 - p) * samp2
            mixed_samples.append(mixed_sample)
        mixed_samples += [p * sound1[i] for i in range(dur2, dur1)]
    else:
        for samp1, samp2 in zip(sound1, sound2):
            mixed_sample = p * samp1 + (1 - p) * samp2
            mixed_samples.append(mixed_sample)
        mixed_samples += [(1 - p) * sound2[i] for i in range(dur1, dur2)]

    return {"rate": mixed_rate, "samples": mixed_samples}  # return new sound


def convolve(sound, kernel):
    """
    Compute a new sound by convolving the given input sound with the given
    kernel.  Does not modify input sound.

    Args:
        sound: a dictionary representing the original mono sound
        kernel: list of numbers, the signal with which the sound should be
                convolved

    Returns:
        A new mono sound dictionary resulting from the convolution.
    """
    rate = sound["rate"]
    input_samples = sound["samples"]

    len_input = len(input_samples)
    len_kernel = len(kernel)
    len_output = len(input_samples) + len(kernel) - 1

    convolved_samples = [0] * len_output
    for i in range(len_input):
        for j in range(len_kernel):
            convolved_samples[i + j] += input_samples[i] * kernel[j]
    return {"rate": rate, "samples": convolved_samples}


def echo(sound, num_echoes, delay, scale):
    """
    Compute a new sound consisting of several scaled-down and delayed versions
    of the input sound. Does not modify input sound.

    Args:
        sound: a dictionary representing the original mono sound
        num_echoes: int, the number of additional copies of the sound to add
        delay: float, the amount of seconds each echo should be delayed
        scale: float, the amount by which each echo's samples should be scaled

    Returns:
        A new mono sound dictionary resulting from applying the echo effect.
    """
    sample_delay = round(delay * sound["rate"])
    input_sound = sound["samples"]
    len_sound = len(input_sound)
    extra_length = num_echoes * sample_delay
    echo_sound = input_sound[:] + [0] * extra_length
    for i in range(num_echoes):
        scale_factor = scale ** (i + 1)
        for j in range(len_sound):
            echo_sound[j + (i + 1) * sample_delay] += input_sound[j] * scale_factor
    return {"rate": sound["rate"], "samples": echo_sound}


def pan(sound):
    """
    Using a sound dictionary with stereo samples,
    Generate a left to right moving sound

    Args:
        sound (dict): sound dictionary with rate, left, and right keys

    Returns:
        _dict_: outputs the sound moving from left to right ear
    """
    rate = sound["rate"]
    left_samples = sound["left"]
    right_samples = sound["right"]
    len_samples = len(left_samples)
    pan_left = left_samples[:]
    pan_right = right_samples[:]
    for i in range(len_samples):
        scale = i / (len_samples - 1)
        pan_right[i] *= scale
        pan_left[i] *= 1 - scale
    return {"rate": rate, "left": pan_left, "right": pan_right}


def remove_vocals(sound):
    """
    Given a stereo sound dictionary,
    remove human vocals to retrieve instrumental track.

    Args:
        sound (dict): with keys rate, left, right

    Returns:
        dict: output sound with vocals removed
    """
    rate = sound["rate"]
    l_samples = sound["left"]
    r_samples = sound["right"]
    lr_diff = [left - right for left, right in zip(l_samples, r_samples)]
    return {"rate": rate, "samples": lr_diff}


def bass_boost_kernel(n_val, scale=0):
    """
    Construct a kernel that acts as a bass-boost filter.

    We start by making a low-pass filter, whose frequency response is given by
    (1/2 + 1/2cos(Omega)) ^ n_val

    Then we scale that piece up and add a copy of the original signal back in.
    """
    # make this a fake "sound" so that we can use the convolve function
    base = {"rate": 0, "samples": [0.25, 0.5, 0.25]}
    kernel = {"rate": 0, "samples": [0.25, 0.5, 0.25]}
    for i in range(n_val):
        kernel = convolve(kernel, base["samples"])
    kernel = kernel["samples"]

    # at this point, the kernel will be acting as a low-pass filter, so we
    # scale up the values by the given scale, and add in a value in the middle
    # to get a (delayed) copy of the original
    kernel = [i * scale for i in kernel]
    kernel[len(kernel) // 2] += 1

    return kernel


# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds


def load_wav(filename, stereo=False):
    """
    Given the filename of a WAV file, load the data from that file and return a
    Python dictionary representing that sound
    """
    file = wave.open(filename, "r")
    chan, bd, sr, count, _, _ = file.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    out = {"rate": sr}

    if stereo:
        left = []
        right = []
        for i in range(count):
            frame = file.readframes(1)
            if chan == 2:
                left.append(struct.unpack("<h", frame[:2])[0])
                right.append(struct.unpack("<h", frame[2:])[0])
            else:
                datum = struct.unpack("<h", frame)[0]
                left.append(datum)
                right.append(datum)

        out["left"] = [i / (2**15) for i in left]
        out["right"] = [i / (2**15) for i in right]
    else:
        samples = []
        for i in range(count):
            frame = file.readframes(1)
            if chan == 2:
                left = struct.unpack("<h", frame[:2])[0]
                right = struct.unpack("<h", frame[2:])[0]
                samples.append((left + right) / 2)
            else:
                datum = struct.unpack("<h", frame)[0]
                samples.append(datum)

        out["samples"] = [i / (2**15) for i in samples]

    return out


def write_wav(sound, filename):
    """
    Given a dictionary representing a sound, and a filename, convert the given
    sound into WAV format and save it as a file with the given filename (which
    can then be opened by most audio players)
    """
    outfile = wave.open(filename, "w")

    if "samples" in sound:
        # mono file
        outfile.setparams((1, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = [int(max(-1, min(1, v)) * (2**15 - 1)) for v in sound["samples"]]
    else:
        # stereo
        outfile.setparams((2, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = []
        for left, right in zip(sound["left"], sound["right"]):
            left = int(max(-1, min(1, left)) * (2**15 - 1))
            right = int(max(-1, min(1, right)) * (2**15 - 1))
            out.append(left)
            out.append(right)

    outfile.writeframes(b"".join(struct.pack("<h", frame) for frame in out))
    outfile.close()


if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place to put your
    # code for generating and saving sounds, or any other code you write for
    # testing, etc.

    # here is an example of loading a file (note that this is specified as
    # sounds/hello.wav, rather than just as hello.wav, to account for the
    # sound files being in a different directory than this file)
    hello = load_wav("sounds/hello.wav")

    # write_wav(backwards(hello), 'hello_reversed.wav')
