#!/usr/bin/env python
#
# author: dec 2020
# cassio batista - https://cassota.gitlab.io

import sys
import os
import glob

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("usage: %s <phoneids.ctm> <txt-list> <dict> <pts-out-dir>" % sys.argv[0])
        sys.exit(1)

    phoneids_file = sys.argv[1]
    txt_list_file = sys.argv[2]
    dict_file = sys.argv[3]
    pts_dir = sys.argv[4]

    # sanity check
    if not os.path.isfile(phoneids_file):
        print("[%s] error: phoneids.ctm file '%s' does not exist" % \
              (sys.argv[0], phoneids_file))
        sys.exit(1)
    if not os.path.isfile(txt_list_file):
        print("[%s] error: list of txt file '%s' does not exist" % \
              (sys.argv[0], txt_list_file))
        sys.exit(1)
    if not os.path.isfile(dict_file):
        print("[%s] error: dict file '%s' does not exist" % \
              (sys.argv[0], dict_file))
        sys.exit(1)
    if not os.path.isdir(pts_dir):
        print("[%s] error: pts out dir '%s' does not exist" % \
              (sys.argv[0], pts_dir))
        sys.exit(1)

    print("[%s] mapping dict from '%s'" % (sys.argv[0], dict_file))
    with open(dict_file) as f:
        g2p = f.readlines()
    dictionary = {}
    for line in g2p:
        grapheme, phonemes = line.split("\t")
        dictionary[grapheme] = phonemes  # Dict[str, str]

    print("[%s] loading transcripts from '%s'" % (sys.argv[0], txt_list_file))
    with open(txt_list_file) as f:
        txt_list = f.read().split()
    transcriptions = {}
    for txt_file in txt_list:
        with open(txt_file) as f:
            txt = f.read().strip()  # str
        key, value = os.path.basename(txt_file.replace(".txt", "")), txt
        transcriptions[key] = value  # 'M-001': 'a questão foi retomada ...'

    print("[%s] loading phoneids from '%s'" % (sys.argv[0], phoneids_file))
    with open(phoneids_file) as f:
        phoneids = f.readlines()

    print("[%s] generating g2p mapping per transcription file" % sys.argv[0])
    phonemes = {}
    for uttline in phoneids:
        uttid, ch, start, dur, phoneid = uttline.split()
        if uttid not in phonemes.keys():
            phonemes[uttid] = []
            for word in transcriptions[uttid].split():
                phonemes[uttid] += dictionary[word].split()

    # if popping from phonemes' list does not raise IndexError, this itself
    # should be proof of the correctness of the phoneids-dictionary mapping
    # - Cassio :)
    while len(phoneids):
        pts = []
        uttid, ch, start, dur, phoneid = phoneids.pop(0).split()
        if phoneid == "1":  # skip sil
            continue
        phone, timestamp = phonemes[uttid].pop(0), float(start) + float(dur)
        pts.append("%s\t%.3f" % (phone, timestamp))
        while len(phoneids):
            uttid2, ch, start, dur, phoneid = phoneids.pop(0).split()
            if phoneid == "1":  # skip sil
                continue
            if uttid2 != uttid:
                uttline = "%s %s %s %s %s" % (uttid2, ch, start, dur, phoneid)
                phoneids.insert(0, uttline)
                break
            phone, timestamp = phonemes[uttid].pop(0), float(start) + float(dur)
            pts.append("%s\t%.3f" % (phone, timestamp))
        pts_file = os.path.join(pts_dir, "%s.pts" % uttid)
        print("\r[%s] writing file '%s'" % (sys.argv[0], pts_file),
              end=" ", flush=True)
        with open(pts_file, "w") as f:
            for item in pts:
                f.write(item.expandtabs(8) + "\n")
    print()
