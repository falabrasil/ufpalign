# UFPAlign: Alinhamento Fonético Forçado :brazil:

O UFPAlign é uma ferramenta de código aberto para alinhamento fonético
automático do Português Brasileiro utilizando o pacote de ferramentas 
[Kaldi](http://kaldi-asr.org/). O UFPAlign é disponibilizado como um plugin 
para o [Praat](https://www.fon.hum.uva.nl/praat/), sendo acessível diretamente 
do menu do Praat e performa o alinhamento a partir de um arquivo de áudio e sua
transcrição ortográfica com algumas poucas etapas manuais. O resultado é um
TextGrid multi-nível contendo fonemas, sílabas, palavras, transcrições
fonéticas e ortográficas conforme a figura abaixo.

![](doc/textgrid.png)

:uk: [Check the documentation in English](README.md)

## Dependências

:warning: Atualmente, o UFPAlign funciona em sistemas operacionais Linux.

Esta documentação irá guiá-lo na instalação dos requisitos e do UFPAlign em si.
Se você encontrar algum problema, abra uma nova issue neste repositório para 
que possamos ajudá-lo. Aqui, assume-se uma instalação em um sistema operacional
baseado no Debian, então o gerenciador de pacotes padrão será o `apt`.

<details>
<summary>Kaldi</summary>

Primeiro, clone a versão mais atual do Kaldi do GitHub digitando em seu terminal:

```bash
$ git clone https://github.com/kaldi-asr/kaldi
```

O próximo passo é a instalação do `tools` do Kaldi. Vá para kaldi/tools/ e
primeiramente verifique se algum pré-requisitos do Kaldi ainda precisa ser
instalado:

```bash
$ cd kaldi/tools
$ extras/check_dependencies.sh
```

Verifique cuidadosamente a saída do comando acima e instale todos os
pré-requisitos necessários se houver algum faltando. Depois rode o comando:

```bash
$ make
```

Se você tiver várias CPUs e quiser acelerar as coisas, pode rodar o passo
anterior paralelamente usando o parâmetro `-j`. Por exemplo, para usar 4 CPUs
execute:

```bash
$ make -j 4
```

O último pacote a ser instalado é a OpenBLAS, uma biblioteca open-source de
álgebra linear que pode ser utilizada no lugar da Intel MKL. Cuidado que isso
irá utilizar todos os cores da máquina, até mesmo as hyperthreads caso o
processador suporte.

```bash
$ extras/install_openblas.sh
```

Finalmente, instale o Kaldi `src`.

```bash
$ cd kaldi/src
$ ./configure --shared
$ make depend -j 4
$ make -j 4
```

Para testar se a instalação do Kaldi foi bem-sucedida, execute os scripts do
corpus yes/no. A execução é rápida, pois o conjunto de dados é muito pequeno e
o pipeline apenas treina e decodifica um modelo baseado em monofones.

```bash
$ cd kaldi/egs/yesno/s5
$ bash run.sh
```

A última linha da execução deverá printar a taxa de erro por palavra (WER): 

```text
%WER 0.00 [ 0 / 232, 0 ins, 0 del, 0 sub ] exp/mono0a/decode_test_yesno/wer_10_0.0
```
</details>

<details>
<summary>Praat</summary>

Em ambientes Linux, você pode instalar o Praat usando o `apt-get` rodando o comando:

```bash
$ sudo apt-get install praat
```

Ou você baixar o executável 64-bit na página de [download do
Praat](https://www.fon.hum.uva.nl/praat/praat6141_linux64.tar.gz). Depois de
baixá-lo, descompacte dentro da pasta de sua escolha. Pronto, apenas clique no
executável para usar o Praat. O .tar.gz pode ser deletado.
</details>

<details>
<summary>NLP-generator</summary>

Primeiro, clone o repositório NLP-generator do Gitlab dentro do seu diretório
home (:warning: O NLP-generator precisa ser clonado dentro da sua home para que
o UFPAlign funcione corretamente).

```bash
$ git clone https://gitlab.com/fb-nlp/nlp-generator.git
```

O NLP-generator foi desenvolvido em Java, mas recentemente foi atualizado para
também funcionar em Python graças ao módulo
[PyJNIus](https://github.com/kivy/pyjnius), o qual permite que os metódos em
Java sejam  importados pelo Python. Portanto, para instalar os requisitos de
NLP, precisamos baixar e instalar o [Anaconda] (https://www.anaconda.com/) para
Python 3. Em seu navegador, baixe o instalador Anaconda para Linux diretamente
do site do Anaconda. Em seguida, rode para instalar:

```bash
$ bash Anaconda3-2020.11-Linux-x86_64.sh 
```

Agora você pode instalar os requisitos restantes usando `conda`:

```bash
$ conda install cython
$ sudo conda install -c conda-forge pyjnius
$ sudo conda install -c anaconda openjdk
$ pip3 install PyICU
```

Certifique-se de que todos os requisitos sejam atendidos digitando no terminal:

```bash
$ pip3 list | grep -iE 'jni|cython|pyicu'
```

O último comando deve imprimir a saída:

```bash
$ pip3 list | egrep -i 'jni|cython|pyicu'
Cython                             0.29.21
PyICU                              2.6
pyjnius                            1.2.1
```

Finalmente, certifique-se de que sua variável de ambiente `JAVA_HOME` aponta
para Java 8 (ou versão mais recente) do Anaconda como o exemplo abaixo:

```bash
$ echo $JAVA_HOME 
/home/anaconda3
```
</details>


## Instalação

Primeiro, certifique-se de que todos os pré-requisitos do UFPAlign estejam
instalados. Então, você apenas precisa baixar o arquivo
`plugin_ufpalign.tar.gz` e descompacta-lo no diretório de preferências do Praat
(`~/.praat_dir`). O diretório de preferências do Praat é onde o Praat salva o
arquivo de preferências, arquivo de botões e onde você pode instalar plugins.
Se o diretório de preferências não existir, ele será criado automaticamente em
seu diretório home assim que você iniciar o Praat pela primeira vez.

```bash
$ tar -xzf  plugin_ufpalign.tar.gz -C ~/.praat_dir
```

Uma vez que a pasta do plugin é descompactada na diretório de preferências do
Praat, iniciar o Praat irá adicionar automaticamente as funções incluídas no
UFPAlign ao menu `New` da janela de objetos do Praat conforme a imagem abaixo.

![](doc/praat_menu.png)

Como parte do uso do UFPAlign em nossa própria pesquisa acadêmica, treinamos
modelos acústicos de diferentes arquiteturas: modelos baseados em monofone,
trifone e DNN (nnet3) (Verifique o 
[repositório de treinamento de modelos acústicos Kaldi do FalaBrasil](https://github.com/falabrasil/kaldi-br),
se quiser saber mais sobre o script de treinamento de modelos acústicos). Um
total de cinco modelos pré-treinados compatíveis com Kaldi estão incluídos como
parte do UFPAlign. Portanto, você precisa baixar os modelos acústicos
pré-treinados que estão disponíveis para realizar o alinhamento fonético.
Primeiro, mude para diretório `~/.praat_dir` e então execute o script
`download_models.sh`. Os modelos serão baixados para o diretório
`~/.praat-dir/plugin_ufpalign/pretrained_models`.

```bash
$ cd ~/.praat-dir/plugin_ufpalign
$ ./download_models.sh 
```

## Como usar

Para usar o plugin, abra o menu `New` e clique na opção `UFPAlign`, a seguinte
janela inicial será exibido. Clique nos botões `Choose...` para selecionar o
caminho para o diretório raiz do Kaldi, um arquivo de áudio (:warning: O
arquivo de áudio deve ser amostrado em uma frequência de 16 Khz com 1 canal) e
sua correspondente transcrição ortográfica. Você também pode escolher a
arquitetura do modelo acústico ques será usado para realizar o alinhamento.
Após selecioná-los, clique no botão `Alinhar`. Em seguida, aguarde enquanto o
arquivo é alinhado. Isso pode demorar um pouco.

Quando o alinhamento é concluído com sucesso, o alinhador oferece a opção de
exibir imediatamente o TextGrid resultante na interface do Praat ou prosseguir
para alinhar um novo arquivo de áudio.

A figura abaixo mostra o editor de TextGrid do Praat exibindo uma forma de onda
do arquivo de áudio seguida por seu espectrograma e o TextGrid multicamadas
resultante de alinhamento contendo cinco camadas: fonemas, sílabas, palavras,
transcrição fonética e transcrição ortográfica, respectivamente.

O próprio editor TextGrid do Praat plota a forma de onda e o espectrograma do
arquivo de áudio, está informação não é conteúdo do arquivo TextGrid. O Kaldi
fornece os traços azuis verticais, que correspondem às marcas de tempo,
enquanto a biblioteca de NLP do FalaBrasil fornece as transcrições fonéticas e
silábicas. Quer você decida abrir imediatamente o TextGrid resultante na
interface Praat ou não, o arquivo TextGrid será salvo dentro de um diretório
chamado textgrid em seu diretório inicial com o mesmo nome do arquivo de áudio
que você escolheu alinhar.


## Citação

Se utilizares qualquer recurso disponível nesse repositório, por favor nos cite
com as seguintes referências:

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

:warning: Este artigo usa as receitas `nnet2` desatualizadas, porém este
repositório foi atualizado para a receita dos chain models por meio de scripts
`nnet3`. O `nnet2` scripts, podem ser encontrados na tag `nnet2` no
[repositório do FalaBrasil com os scripts de treinamento de modelos acústicos usando o Kaldi](https://github.com/falabrasil/kaldi-br).

[![FalaBrasil](https://gitlab.com/falabrasil/avatars/-/raw/main/logo_fb_git_footer.png)](https://ufpafalabrasil.gitlab.io/ "Visite o site do Grupo FalaBrasil") [![UFPA](https://gitlab.com/falabrasil/avatars/-/raw/main/logo_ufpa_git_footer.png)](https://portal.ufpa.br/ "Visite o site da UFPA")

__Grupo FalaBrasil (2022)__ - https://ufpafalabrasil.gitlab.io/      
__Universidade Federal do Pará (UFPA)__ - https://portal.ufpa.br/     
Cassio Batista - https://cassota.gitlab.io/    
Larissa Dias   - larissa.engcomp@gmail.com     
