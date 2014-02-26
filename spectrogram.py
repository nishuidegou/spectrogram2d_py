#!/usr/bin/env python3
import sys
import numpy
import argparse
import itertools
import collections
from PIL import Image
import scipy.io.wavfile as wavfile

# main

const = lambda _, a: a

def readwav(wav_file):
    return wavfile.read(wav_file)[1]

def make_spectrogram(stream, stride, offset):
    '''sequence num -> num -> num -> sequence (sequence num)
    
    Make a spectrogram of the things in the stream. Take elements by stride. Start each stride one offset further.
    
    '''
    if stride < offset:
        print('WARNING: Stride is less than offset, which will cause data to be skipped.', file=sys.stderr)
    starts = range(0, len(stream) - stride, offset)
    chunks = (stream[n:n + stride] for n in starts)
    # compute ffts and abs their results
    raw_ffts = numpy.abs(numpy.array(
        [ const( print( '\r%d/%d fft, %d%%\t\t\t'
                      % (n, len(starts), n / len(starts) * 100), end='', file=sys.stderr)
               , numpy.fft.rfft(c)
               )
          for n, c in zip(itertools.count(), chunks)
        ]))
    print(file=sys.stderr)
    if len(raw_ffts.shape) != 2:
        raise ValueError('Result was not rectangular: %s' % raw_ffts.shape)
    print('Shape is', raw_ffts.shape, file=sys.stderr)
    # mask values LE 0, scale to 10*log10, fill in masked values as minimum value
    masked_ffts = numpy.ma.masked_array(raw_ffts, mask=raw_ffts<1)
    del raw_ffts
    scaled_ffts = 10 * numpy.log10(masked_ffts)
    del masked_ffts
    filled_ffts = scaled_ffts.filled(scaled_ffts.min())
    del scaled_ffts
    return filled_ffts 

def normalize(ar):
    '''Shift and scale the array onto the range 0..1'''
    sh = ar - ar.min()
    return sh / sh.max()

def save_image(ar, filename):
    '''Save an image from a 2D brightness array on the range 0..1'''
    pixels = (ar * 255).round().astype('int8')
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
    sg = make_spectrogram(readwav(args.wav_file), args.stride, args.offset)
    emphasized = normalize(sg ** args.power)
    print('Saving to "%s"' % args.image_file)
    return save_image(emphasized, args.image_file)

if __name__ == '__main__':
    DEF_STRIDE = 512
    DEF_OFFSET = 44100//100
    DEF_POWER = 4
    ap = argparse.ArgumentParser(description="Generate a spectrogram from a wav file.")
    ap.add_argument('wav_file', help='A path to the wav file to generate a spectrogram of.')
    ap.add_argument('-f', '--image_file', help='An output path to write the image. Default uses other arguments.')
    ap.add_argument('-s', '--stride', metavar='int', help='Default: %d. Use this many samples in each time slice of the spectrogram. Bigger increases frequency range (bigger image y resolution).' % DEF_STRIDE, type=int, default=DEF_STRIDE)
    ap.add_argument('-o', '--offset', metavar='int', help='Default: %d. Offset successive chunks by this many samples. You\'ll have one vertical row of information per offset. Bigger skips more time between slices in the spectrogram (smaller x resolution).' % DEF_OFFSET, type=int, default=DEF_OFFSET)
    ap.add_argument('-p', '--power', metavar='int', help='Default: %d. Filter out noise by raising the whole spectrogram to this power. Bigger emphasizes the loud noises more (darker image).' % DEF_POWER, type=int, default=DEF_POWER)
    exit(main(ap.parse_args()))

Args = collections.namedtuple('Args', [
        'wav_file',
        'slices',
        'overlap',
        'power',
    ])

# eof
