# spectrogram2d_py

generate a spectrogram image from a wav file

## Examples and usage

#### Sine at 1250hz and 650hz sampled at 10kHz for 1 second

```bash
$ ./spectrogram.py examples/mel.wav
Stride: 512
Offset: 441
Power: 4
98/99 fft, 98%
Shape is (99, 257)
Saving to "examples/mel.wav-s512-o441-p4.png"
```

[mel.wav](https://raw.github.com/plredmond/spectrogrampy/master/examples/mel.wav)  
![mel spectrogram](https://raw.github.com/plredmond/spectrogrampy/master/examples/mel.wav-s512-o441-p4.png)

#### Bird call (source: Wikipedia)

```bash
$ ./spectrogram.py bird.wav -o 220 -s 2048 -p 8
Stride: 2048
Offset: 220
Power: 8
1131/1132 fft, 99%
Shape is (1132, 1025)
Saving to "bird.wav-s2048-o220-p8.png"
```

[Parus major 15mars2011 [wikipedia]](http://en.wikipedia.org/wiki/File:Parus_major_15mars2011.ogg)  
![bird spectrogram](https://raw.github.com/plredmond/spectrogrampy/master/examples/bird.wav-s2048-o220-p8.png)

Enjoy!

-- [PLR](http://f06mote.com)

---

At least *Python 3.3.3 - 3.4*
