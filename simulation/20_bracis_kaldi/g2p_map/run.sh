#!/bin/bash
#
# Grupo FalaBrasil (2020)
# Universidade Federal do Pará
#
# author: apr 2020
# cassio batista - https://cassota.gitlab.io/
# last edited: jul 2020

res_dir=res
tg_outdir=/tmp/nada/

figlet "these scripts               are deprecated" | lolcat

echo -e "\033[94m  ____                         \033[93m _____     _           \033[0m"
echo -e "\033[94m / ___| _ __ _   _ _ __   ___  \033[93m|  ___|_ _| | __ _     \033[0m"
echo -e "\033[94m| |  _ | '__| | | | '_ \ / _ \ \033[93m| |_ / _\` | |/ _\` |  \033[0m"
echo -e "\033[94m| |_| \| |  | |_| | |_) | (_) |\033[93m|  _| (_| | | (_| |    \033[0m"
echo -e "\033[94m \____||_|   \__,_| .__/ \___/ \033[93m|_|  \__,_|_|\__,_|    \033[0m"
echo -e "                  \033[94m|_|      \033[32m ____                _ _\033[0m\033[91m  _   _ _____ ____    _   \033[0m"
echo -e "                           \033[32m| __ ) _ __ __ _ ___(_) |\033[0m\033[91m| | | |  ___|  _ \  / \          \033[0m"
echo -e "                           \033[32m|  _ \| '_ / _\` / __| | |\033[0m\033[91m| | | | |_  | |_) |/ ∆ \        \033[0m"
echo -e "                           \033[32m| |_) | | | (_| \__ \ | |\033[0m\033[91m| |_| |  _| |  __// ___ \        \033[0m"
echo -e "                           \033[32m|____/|_|  \__,_|___/_|_|\033[0m\033[91m \___/|_|   |_|  /_/   \_\       \033[0m"
echo -e "                                     https://ufpafalabrasil.gitlab.io/"

for f in lolcat python3 ; do
    msg="$0: error: please install $f"
    type -t $f > /dev/null || { echo $msg && exit 1; }
done

for f in jnius termcolor ; do
    msg="$0 error: please install python module $f"
    python3 -c "import $f" 2> /dev/null || { echo $msg && exit 1; }
done

mkdir -pv $res_dir

echo "[$0] running tg2news.py" | lolcat
python3 tg2news.py $res_dir/{filelist_male.txt,ali.news} || exit 1

echo "[$0] running news2m2m.py" | lolcat
python3 news2m2m.py $res_dir/{ali.news,ali.m2m,ali.model} || exit 1

echo "[$0] running m2m2tg.py" | lolcat
python3 m2m2tg.py $res_dir/{filelist_male.txt,ali.m2m} $tg_outdir || exit 1

echo "[$0] done!" | lolcat
