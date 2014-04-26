#!/usr/bin/env python3
import sys
import math
import numpy
import argparse
import itertools
import collections
from PIL import Image
import scipy.io.wavfile as wavfile

# main

const = lambda _, a: a

def make_spectrogram(stream, stride, offset):
    '''sequence num -> num -> num -> sequence (sequence num)
    
    Make a spectrogram of the things in the stream. Take elements by stride. Start each stride one offset further.
    
    '''
    if stride < offset:
        print('WARNING: Stride is less than offset, which will cause data to be skipped.', file=sys.stderr)
    # determine where each chunk of audio starts
    starts = range(0, len(stream) - stride, offset)
    # split the stream into stride-long chunks whose beginnings increase by offset
    chunks = (stream[n:n + stride] for n in starts)
    # smooth the ends of each chunk to silence
    windowed = map(window, chunks)
    # compute ffts and abs their results
    ffts = numpy.abs(numpy.array(
        [ const( print( '\r%d/%d fft, %d%%\t\t\t'
                      % (n, len(starts), n / len(starts) * 100), end='', file=sys.stderr)
               , numpy.fft.rfft(wwav)
               )
          for n, wwav in zip(itertools.count(), windowed)
        ]))
    print(file=sys.stderr)
    if len(ffts.shape) != 2:
        raise ValueError('Result was not rectangular: {}'.format(ffts.shape))
    print('Shape is', ffts.shape, file=sys.stderr)
    # make 1 the minimum value
    ffts[ffts < 1] = 1
    # scale to something like dB
    return 10 * numpy.log10(ffts ** 2)

def window(chunk):
    ct = len(chunk)
    return [hamming(n, ct) * samp for n, samp in enumerate(chunk)]

def hamming(n, ct):
    '''Int, Int -> Float'''
    a = 0.53836
    b = 0.46164
    rat = n / ct
    return a - b * math.cos(2 * math.pi * rat)

def save_image(ar, filename):
    '''Save an image from a 2D brightness array'''
    ar -= ar.min() # shifted to 0..max
    ar *= 255 / ar.max() # scaled to 0..255
    pixels = ar.round().astype('int8')
    im = Image.fromarray(numpy.fliplr(pixels).transpose(), mode='L')
    try:
        im.save(filename)
    except KeyError:
        print('ERROR: Couldn\'t save. Unknown image format specified by file extension.', file=sys.stderr)

def main(args):
    if args.image_file is None:
        args.image_file = '%s-s%d-o%d-p%d.png' % (args.wav_file, args.stride, args.offset, args.power)
    print('Stride: %d' % args.stride, file=sys.stderr)
    print('Offset: %d' % args.offset, file=sys.stderr)
    print('Power: %d' % args.power, file=sys.stderr)
    rate, data = wavfile.read(args.wav_file, mmap=args.mmap)
    print('Wav sample rate: %d' % rate, file=sys.stderr)
    print('Wav stream shape: {}'.format(data.shape), file=sys.stderr)
    if len(data.shape) == 2:
        data = (data[:,0] + data[:,1]) / 2
    elif len(data.shape) > 2:
        raise ValueError('Multichannel')
    print('Wav stream shape: {}'.format(data.shape), file=sys.stderr)
    sg = make_spectrogram(data, args.stride, args.offset)
    sg **= args.power # squish smaller values down
    print('Saving to "%s"' % args.image_file)
    return save_image(sg, args.image_file)

if __name__ == '__main__':
    DEF_STRIDE = 512
    DEF_OFFSET = 44100//100
    DEF_POWER = 4
    DEF_MMAP = False
    ap = argparse.ArgumentParser(description="Generate a spectrogram from a wav file.")
    ap.add_argument('wav_file', help='A path to the wav file to generate a spectrogram of.')
    ap.add_argument('-f', '--image_file', metavar='path', help='An output path to write the image. Default uses the name of the wav file and the settings used to generate the spectrogram.')
    ap.add_argument('-s', '--stride', metavar='int', help='Default: %d. Use this many samples in each time slice of the spectrogram. Bigger increases frequency range (bigger image y resolution).' % DEF_STRIDE, type=int, default=DEF_STRIDE)
    ap.add_argument('-o', '--offset', metavar='int', help='Default: %d. Offset successive chunks by this many samples. You\'ll have one vertical row of information per offset. Bigger skips more time between slices in the spectrogram (smaller x resolution).' % DEF_OFFSET, type=int, default=DEF_OFFSET)
    ap.add_argument('-p', '--power', metavar='int', help='Default: %d. Filter out noise by raising the whole spectrogram to this power. Bigger emphasizes the loud noises more (darker image).' % DEF_POWER, type=int, default=DEF_POWER)
    ap.add_argument('-m', '--mmap', help='Default: %s. Memory-map the wav file? This might help loading of large files.' % DEF_MMAP, default=DEF_MMAP, action='store_true')
    exit(main(ap.parse_args()))

Args = collections.namedtuple('Args', [
        'wav_file',
        'slices',
        'overlap',
        'power',
        'mmap',
    ])

# eof
