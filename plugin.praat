#msg$ = "Choose Kaldi directory"
#kaldiDir$ = ""
#kaldiSanityFile$ = "/coxinha/de/frango"
#while not fileReadable: kaldiSanityFile$
#    beginPause: "Choose Kaldi ROOT directory"
#        text: msg$, kaldiDir$ 
#        comment: "Choose M2M Aligner directory (later)"
#        comment: "Chose input audio file (later)"
#        comment: "Chose input text file (later)"
#    clicked = endPause: "Choose Kaldi directory...", 1
#    kaldiDir$ = chooseDirectory$: "Choose Kaldi root dir"
#    kaldiSanityFile$ = kaldiDir$ + "/src/featbin/add-deltas"
#    msg$ = "Wrong directory! Please choose Kaldi directory again"
#endwhile
#
#msg$ = "Choose M2M Aligner directory"
#m2mDir$ = ""
#m2mSanityFile$ = "/coxinha/de/frango"
#while not fileReadable: m2mSanityFile$
#    beginPause: "Choose M2M ROOT directory"
#        comment: "Kaldi ROOT dir (path is valid, just checked it):" + newline$ + kaldiDir$ + newline$ + "."
#        text: msg$, m2mDir$ 
#        comment: "Chose input audio file (later)"
#        comment: "Chose input text file (later)"
#    clicked = endPause: "Choose M2M directory...", 1
#    m2mDir$ = chooseDirectory$: "Choose m2m root dir"
#    m2mSanityFile$ = m2mDir$ + "/m2m-aligner"
#    msg$ = "Wrong directory! Please choose M2M Aligner directory again"
#endwhile
#
#msg$ = "Choose input audio file"
#wavFile$ = "/coxinha/de/frango.vsf"
##ext$ = right$: wavFile$, 4
#while not fileReadable: wavFile$
#    wavFile$ = ""
#    beginPause: "Choose WAV file"
#        comment: "Kaldi ROOT dir (path is valid, just checked it):" + newline$ + kaldiDir$ + newline$ + "."
#        comment: "M2M ROOT dir (path is valid, just checked it):" + newline$ + m2mDir$ + newline$ + "."
#        text: msg$, wavFile$ 
#        comment: "Chose input text file (later)"
#    clicked = endPause: "Choose WAV file...", 1
#    wavFile$ = chooseReadFile$: "Choose input audio WAV file"
#    #ext$ = right$: wavFile$, 4
#    msg$ = "Wrong WAV file! Please choose input audio again"
#endwhile
#
#msg$ = "Choose input text file"
#txtFile$ = "/coxinha/de/frango.vsf"
##ext$ = right$: txtFile$, 4
#while not fileReadable: txtFile$
#    txtFile$ = ""
#    beginPause: "Choose TXT file"
#        comment: "Kaldi ROOT dir (path is valid, just checked it):" + newline$ + kaldiDir$ + newline$ + "."
#        comment: "M2M ROOT dir (path is valid, just checked it):" + newline$ + m2mDir$ + newline$ + "."
#        comment: "Audio path (path is valid, just checked it):" + newline$ + wavFile$ + newline$ + "."
#        text: msg$, txtFile$ 
#    clicked = endPause: "Choose TXT file...", 1
#    txtFile$ = chooseReadFile$: "Choose input audio TXT file"
#    #ext$ = right$: txtFile$, 4
#    msg$ = "Wrong TXT file! Please choose input text again"
#endwhile
#
#beginPause: "All set!"
#    comment: "Kaldi ROOT dir (path is valid, just checked it):" + newline$ + kaldiDir$ + newline$ + "."
#    comment: "M2M ROOT dir (path is valid, just checked it):" + newline$ + m2mDir$ + newline$ + "."
#    comment: "Audio path (path is valid, just checked it):" + newline$ + wavFile$ + newline$ + "."
#    comment: "Text path (path is valid, just checked it):" + newline$ + txtFile$ + newline$ + "."
#    choice: "Choose an acoustic model", 1
#        option: "mono"
#        option: "tri1"
#        option: "tri2b"
#        option: "tri3b"
#        option: "tdnn"
#clicked = endPause: "Continue...", 1
#
#if choose_an_acoustic_model == 1
#    amTag$ = "mono"
#elif choose_an_acoustic_model == 2
#    amTag$ = "tri1"
#elif choose_an_acoustic_model == 3
#    amTag$ = "tri2b"
#elif choose_an_acoustic_model == 4
#    amTag$ = "tri3b"
#elif choose_an_acoustic_model == 5
#    amTag$ = "tdnn"
#endif

kaldiDir$ = "/home/ctbatista/work/tools/kaldi-asr/kaldi"
m2mDir$ = "/home/ctbatista/work/tools/letter-to-phoneme/m2m-aligner"
wavFile$ = "/home/ctbatista/work/tools/letter-to-phoneme/coxinha.wav"
txtFile$ = "/home/ctbatista/work/tools/letter-to-phoneme/coxinha.txt"
amTag$ = "mono"

clearinfo
cmd$ = "KALDI_ROOT=" + kaldiDir$
    ... + " "
    ... + "M2M_ROOT=" + m2mDir$
    ... + " "
    ... + "bash ufpalign.sh"
    ... + " "
    ... + wavFile$
    ... + " "
    ... + txtFile$
    ... + " "
    ... + amTag$
    ... + " "
appendInfoLine: cmd$
#system(cmd$)
system("pwd")
