# FalaBrasil Forced Phonetic Aligner for Brazilian Portuguese Using Kaldi Tools :br:

The UFPAlign is an open-source automatic phonetic alignment tool for Brazilian Portuguese that uses the Kaldi toolkit (http://kaldi-asr.org/) for performing forced alignment of speech datasets. The UFPAlign is distributed as a plugin for Praat (https://www.fon.hum.uva.nl/praat/), a popular free software package for speech analysis in phonetics. The plugin is directly accessible from the Praat menus and it allows to align speech from an audio file and its orthographic transcription with a few minor manual steps. The result is a multi-level annotation TextGrid containing 
phonemes, syllables, words, phonetic and orthographic information as below. 

![](doc/textgrid.png)

:br: [Acesse a documentação em Português Brasileiro](README.br.md)

:fox_face: [Check the original development repository on GitLab](https://gitlab.com/fb-align/kaldi-ali)

## Requirements

Currently, the UFPAlign works under Linux environments. The following is a list of the packages and tools you need in order to install the UFPAlign:

- [Kaldi](https://kaldi-asr.org/)
- [Praat](http://www.fon.hum.uva.nl/praat/)
- [Python 3](https://www.python.org/)
- [FalaBrasil NLP-generator](https://gitlab.com/fb-nlp/nlp-generator) 
<!--{::comment}  [Openjdk](https://openjdk.java.net/)
[//]: # "Comment"- [Cython](https://cython.org/)
[//]: # "Comment"- [PyJNIus](https://github.com/kivy/pyjnius)
[//]: # "Comment"- [PyICU](https://pypi.org/project/PyICU/){:/comment}-->

This documentation will guide you 
through the requirements and UFPAlign installation and usage. 
If you run into any issues, please open a new issue at this repository so we can help you.

### Requirements installation instructions
<details>
<summary>Click to expand</summary>

#### Kaldi installation


<details>
<summary>Click to expand</summary>


First, clone the most current version of Kaldi from GitHub by typing into a shell:

```bash
$ git clone https://github.com/kaldi-asr/kaldi
```

Then, to install Kaldi `tools` go to kaldi/tools/ and first check the prerequisites for Kaldi and see if there are any system-level installations you need to do:

```bash
$ cd kaldi/tools
$ extras/check_dependencies.sh
```
Check the output carefully and install any prerequisites missing. Then run:

```bash
$ make
```

If you have multiple CPUs and want to speed things up, you can do a parallel
build by supplying the "-j" option to make, e.g. to use 4 CPUs:

```bash
$ make -j 4
```

Finally, install Kaldi `src`.

```bash
$ cd kaldi/src
$ ./configure --shared
$ make depend -j 4
$ make -j 4
```

To guarantee Kaldi installation was successful, run the scripts on the yes/no
dataset. It doesn't take long to finish since the dataset is pretty small and
the pipeline only trains and decodes a monophone-bases model.

```bash
$ cd kaldi/egs/yesno/s5
$ bash run.sh
```

The last line should print the word error rate:

```text
%WER 0.00 [ 0 / 232, 0 ins, 0 del, 0 sub ] exp/mono0a/decode_test_yesno/wer_10_0.0
```

</details>

#### Praat installation


<details>
<summary>Click to expand</summary>
To install the Linux version of Praat, you can either use `apt-get` by typing into a shell:

```bash
$ sudo apt-get install praat
```

Or you can download a 64-bit binary executable on the [Praat download page](https://www.fon.hum.uva.nl/praat/praat6141_linux64.tar.gz). Then, unpack it, creating the executable file praat. You can remove the tar file.
</details>

#### NLP-generator installation


<details>
<summary>Click to expand</summary>

First, clone the NLP-generator from Gitlab into your home directory (:warning: It must be cloned to your home directory) by typing into a shell:

```bash
$ git clone git clone https://gitlab.com/fb-nlp/nlp-generator.git
```

The NLP-generator, originally developed in Java, has recently been adapted to 
Python thanks to the [PyJNIus](https://github.com/kivy/pyjnius) module, which
allows you to load Java methods into Python. So, to install the NLP requiriments, we need to download and install [Anaconda](https://www.anaconda.com/) for Python 3. In your browser, download the Anaconda installer for Linux from the Anaconda website. Then, enter the following to install:

```bash
$ bash Anaconda3-2020.11-Linux-x86_64.sh 
```

Now you can install the remaining requiriments using conda:

```bash
$ conda install cython
$ sudo conda install -c conda-forge pyjnius
$ sudo conda install -c anaconda openjdk
$ pip3 install PyICU
```
Make sure that all requirements are meet by typing into a shell:
```bash
$ pip3 list | grep -iE 'jni|cython|pyicu'
```
The last command should print the output:
```bash
$ pip3 list | egrep -i 'jni|cython|pyicu'
Cython                             0.29.21
PyICU                              2.6
pyjnius                            1.2.1
```

Finally, make sure that your environment variable
`JAVA_HOME` points to Java 8 (or newer version) from Anaconda as the example below:
```bash
$ echo $JAVA_HOME 
/home/anaconda3
```
</details>
</details>

## UFPAlign installation instructions

<details>
<summary>Click to expand</summary>
First, make sure that all prerequisites for UFPAlign are installed. Then, you only need to download the `plugin_ufpalign.tar.gz` file and extract
it in your Praat's preference directory (`~/.praat_dir`). The Praat preferences directory is where Praat saves the preferences file and the buttons file, and where you can install plug-ins. If the preferences directory does not exist, it will automatically be created in your home directory when you start Praat. 

```bash
$ tar -xzf plugin_ufpalign.tar.gz -C ~/.praat_dir
```
Once the plugin folder is placed in Praat's preference folder, starting Praat will automatically add the functions included in the UFPAlign to the `new` menu of Praat's objects window as the screenshot below.

![](doc/praat_menu.png)

As part of using the UFPAlign in our own academic research, we have trained acoustic models of different architectures: monophone-, triphone-, and DNN-based (nnet3) models (Check the [FalaBrasil's Kaldi acoustic models training repository](https://gitlab.com/fb-asr/fb-am-tutorial/kaldi-am-train/-/tree/master/train_vosk), if you want to know more about the acoustic models training script). A total of five pre-trained, Kaldi-compatible models are included as part of UFPAlign. So, you need to download the pretrained acoustic models that are available to perform phonetic alignment. First, change to `~/.praat_dir` and then run the script `download_models.sh`. The models will be downloaded to the `~/.praat-dir/plugin_ufpalign/pretrained_models` directory.

```bash
$ cd ~/.praat-dir/plugin_ufpalign
$ ./download_models.sh 
```

</details>

## UFPAlign usage instructions
<details>
<summary>Click to expand</summary>

UFPAlign works fine under Linux environments via command line, but also provides a graphical interface as a plugin to Praat. In order to use the plugin, open the `New` menu and click on the `UFPAlign` option, the following initial window will be
displayed. Click on the `Choose...` buttons to select the path to Kaldi's root directory, an audio file (:warning: The audio file must be sampled at a frequency of 16 Khz
with 1 channel) and the corresponding orthographic transcription. You can also choose an acoustic model, that will be used to perform the alignment, among the five architecture available as option.
After selecting them, click on `Align` button. Then, wait while the file is aligned. This may take a while.

![](doc/ufpalign_window1.png)

When the alignment is successful finished, the aligner offers the option to promptly display the current resulting 
TextGrid in the Praat interface or to proceed 
to align a new audio file. 

![](doc/ufpalign_window3.png)

The figure below shows the Praat's
TextGrid editor displaying an audio file waveform followed by its 
spectrogram and its aligner's resulting multi-tier TextGrid containing five tiers: 
phonemes, syllables, words, phonetic transcription and orthographic transcription,
respectively. 

![](doc/textgrid.png)

Praat's TextGrid editor itself plots the waveform and spectrogram from the audio file, it is not content of the TextGrid file. 
Kaldi provides the vertical blue dashes, which correspond to the time marks, while FalaBrasil's NLP library provides the phonetic and syllabic transcriptions. Whether you decide to immediately open the result TextGrid in Praat interface or not, the TextGrid file will be saved inside a directory named textgrid at your home directory with the same name as the audio file you choose to align.

### UFPAlign usage via command line instructions 

But if you would like to use the UFPAlign via command line, you only need to untar the `UFPAlign.tar.gz` file inside the `path-to-/kaldi/egs/` directory (The `UFPAlign.tar.gz` is shipped inside the `plugin_ufpalign.tar.gz`). :warning: Remember to change the path inside the symbols <> according to the path to Kaldi directory in your system.

```bash
$ tar -xzf UFPAlign.tar.gz -C <path-to-/kaldi/egs/>
$ cd <path-to-/kaldi/egs/UFPAlign>
```

Once the UFPAlign is inside the directory `egs/` of Kaldi, you only need to pass some parameters for the `fb_kaldialign.sh` script. 
```
 ./fb_kaldialign.sh <path-to-kaldi> <path-to-kaldi-UFPAlign-directory> <path-to-audio-file> <path-to-txt-file> <AM-type-tag>
```

There are five acoustic models available to perform the phonetic alignment. They are identify by the tags: mono, tri1, tri2, tri3, tdnn. Below a example of the UFPAlign usage via command line.

```bash
$ ./fb_kaldialign.sh /home/larissa/kaldi /home/larissa/kaldi/egs/UFPAlign /home/larissa/fb-audio-corpora/M-002.wav /home/larissa/fb-audio-corpora/M-002.txt tdnn
```

As soon as the alignment process is finished, you can find the result TextGrid file inside a directory named textgrid at your home directory with the same name as the audio file you choose to align.

</details>


## Citation

If you use any of the resources provided on this repository, please cite us
as the following:

### [BRACIS 2020](https://link.springer.com/chapter/10.1007/978-3-030-61377-8_44)

> Dias A.L., Batista C., Santana D., Neto N. (2020)
> Towards a Free, Forced Phonetic Aligner for Brazilian Portuguese Using Kaldi Tools.
> In: Cerri R., Prati R.C. (eds) Intelligent Systems. BRACIS 2020.
> Lecture Notes in Computer Science, vol 12319. Springer, Cham.
> https://doi.org/10.1007/978-3-030-61377-8_44

```bibtex
@InProceedings{Dias20,
    author     = {Dias, Ana Larissa and Batista, Cassio and Santana, Daniel and Neto, Nelson},
    editor     = {Cerri, Ricardo and Prati, Ronaldo C.},
    title      = {Towards a Free, Forced Phonetic Aligner for Brazilian Portuguese Using Kaldi Tools},
    booktitle  = {Intelligent Systems},
    year       = {2020},
    publisher  = {Springer International Publishing},
    address    = {Cham},
    pages      = {621--635},
    isbn       = {978-3-030-61377-8}
}
```
:warning: This paper uses the outdated nnet2 recipes, while this repo has been
updated to the chain models' recipe via nnet3 scripts. The nnet2
scripts, can be found on tag `nnet2` in the [FalaBrasil's Kaldi acoustic models training repository](https://gitlab.com/fb-asr/fb-am-tutorial/kaldi-am-train).

[![FalaBrasil](doc/logo_fb_github_footer.png)](https://ufpafalabrasil.gitlab.io/ "Visite o site do Grupo FalaBrasil") [![UFPA](doc/logo_ufpa_github_footer.png)](https://portal.ufpa.br/ "Visite o site da UFPA")

__Grupo FalaBrasil (2021)__ - https://ufpafalabrasil.gitlab.io/      
__Universidade Federal do Pará (UFPA)__ - https://portal.ufpa.br/     
Cassio Batista - https://cassota.gitlab.io/    
Larissa Dias   - larissa.engcomp@gmail.com     
Daniel Santana - daniel.santana.1661@gmail.com     
