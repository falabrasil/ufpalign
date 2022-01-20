#!/usr/bin/env bash
#
# author: dec 2020
# cassio batista - https://cassota.gitlab.io


if test $# -ne 2 ; then
  echo "usage: $0 <kaldi-egs-dir> <filelist>"
  exit 1
fi

proj_dir=$1
filelist=$(readlink -f $2)

mkdir -p $proj_dir/data/alignme || exit 1
cd $proj_dir

rm -f data/alignme/{text,utt2spk,wav.scp,corpus.txt,spk2gender,spk2utt}
i=1
n=$(wc -l < $filelist)
while read line ; do
    echo -ne "\r[$0] $i / $n "
    spk_id=$(sed 's/\// /g' <<< $line | awk '{print $(NF-1)}')  # dataset's folder name
    utt_id="${spk_id}_$(basename $line)"
    gender=${spk_id:0:1}  # first char: m | f

    # c.) text (utt_id = spk_id + audio filename with no extension .wav)
    # <utterance_id> <text_transcription>
    #  dad_4_4_2     four four two
    #  july_1_2_5    one two five
    #  july_6_8_3    six eight three
    echo "$utt_id $(cat $line.txt)" >> data/alignme/text

    # d.) utt2spk (utt_id = spk_id + audio filename with no extension .wav)
    # <utterance_id> <speaker_id>
    #  dad_4_4_2     dad
    #  july_1_2_5    july
    #  july_6_8_3    july
    echo "$utt_id $spk_id" >> data/alignme/utt2spk

    # b.) wav.scp (utt_id = spk_id + audio filename with no extension .wav)
    # <utterance_id> <full_path_to_audio_file>
    #  dad_4_4_2     ${HOME}/kaldi/egs/digits/corpus/train/dad/4_4_2.wav
    #  july_1_2_5    ${HOME}/kaldi/egs/digits/corpus/train/july/1_2_5.wav
    #  july_6_8_3    ${HOME}/kaldi/egs/digits/corpus/train/july/6_8_3.wav
    # NOTE: CB - beware: no symlinks anymore
    echo "$utt_id $line.wav" >> data/alignme/wav.scp

    # a.) spk2gender (spk_id = folder name) XXX: SORTED!
    # <speaker_id> <gender>
    #  cristine    f
    #  dad         m
    #  josh        m
    #  july        f
    echo "$spk_id $gender" >> data/alignme/spk2gender.tmp

    # e.) corpus.txt 
    # <text_transcription>
    #  one two five
    #  six eight three
    #  four four two
    cat $line.txt | grep -avE '^$' >> data/alignme/corpus.txt
    i=$((i+1))
done < $filelist
echo

sort data/alignme/spk2gender.tmp | uniq > data/alignme/spk2gender || exit 1 # XXX: SORTED!
utils/utt2spk_to_spk2utt.pl data/alignme/utt2spk > data/alignme/spk2utt || exit 1
utils/fix_data_dir.sh data/alignme || exit 1
cd - > /dev/null
