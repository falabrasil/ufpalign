# UFPAlign: Alinhamento Fonético Forçado :brazil:

O UFPAlign é uma ferramenta de código aberto para alinhamento fonético
automático do Português Brasileiro utilizando o pacote de ferramentas 
[Kaldi](http://kaldi-asr.org/). O UFPAlign é disponibilizado como um plugin 
para o [Praat](https://www.fon.hum.uva.nl/praat/), sendo acessível diretamente 
do menu do Praat e executando o alinhamento a partir de um arquivo de áudio e 
sua transcrição ortográfica com algumas poucas etapas manuais. O resultado é um
TextGrid multi-nível contendo fonemas, sílabas, palavras, transcrições
fonéticas e ortográficas conforme a figura abaixo.

:warning: A rotina que gera o tier de sílabas foi descontinuada.

![](doc/textgrid.png)

:uk: [Check the documentation in English](README.en.md)

## Dependências

:warning: Atualmente, o UFPAlign funciona em sistemas operacionais Linux.

Aqui, assume-se uma instalação em um sistema operacional
baseado no Debian, então o gerenciador de pacotes padrão será o `apt`.

<details>
<summary>Kaldi</summary>

Primeiro, clona a versão mais atual do Kaldi do GitHub digitando no
terminal:

```bash
$ git clone https://github.com/kaldi-asr/kaldi
```

O próximo passo é a instalação do `tools` do Kaldi. No diretório 
`kaldi/tools/`, verifica se algum pré-requisito do Kaldi ainda precisa ser
instalado:

```bash
$ cd kaldi/tools
$ extras/check_dependencies.sh
```

Se houver algum requisito faltando, o comando deve te informar o passo para
instalá-lo. O passo seguinte é a compilação dos requisitos com o `make`:

```bash
$ make
```

Se tiveres várias CPUs e quiseres acelerar as coisas, podes rodar o passo
anterior paralelamente usando o parâmetro `-j`. Por exemplo, para usar 4 CPUs:

```bash
$ make -j 4
```

O último pacote a ser instalado é a OpenBLAS, uma biblioteca open-source de
álgebra linear que pode ser utilizada no lugar da Intel MKL. Cuidado que isso
irá utilizar todos os cores da tua máquina, até mesmo as hyperthreads caso o
processador as suporte.

```bash
$ extras/install_openblas.sh
```

Finalmente, podes intalar o Kaldi `src`.

```bash
$ cd kaldi/src
$ ./configure --shared
$ make depend -j 4
$ make -j 4
```

Para testar se a instalação do Kaldi foi bem-sucedida, podes executar os
scripts do corpus `yes/no`. A execução é rápida, pois o conjunto de dados é
muito pequeno e o pipeline apenas treina e decodifica um modelo baseado em
monofones.

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

Em ambientes Linux, podes instalar o Praat usando o `apt-get` rodando o comando:

```bash
$ sudo apt-get install praat
```

Ou podes baixar o executável 64-bit na página de [download do
Praat](https://www.fon.hum.uva.nl/praat/praat6141_linux64.tar.gz). Depois de
baixá-lo, deves descompactar dentro de uma pasta. Pronto, apenas clica no
executável para usar o Praat. O `*.tar.gz` pode ser deletado.
</details>

<details>
<summary>Dependencias do Python</summary>
Outras dependencias podem ser instaladas com o `pip`:

```bash
$ pip install requirements.txt
```
</details>


## Instruções de Uso

### Plugin do Praat (GUI)

Para usar o plugin, abre o menu `New` e clique na opção `UFPAlign`, a seguinte
janela inicial será exibido. Clica nos botões `Choose...` para selecionar o
caminho para o diretório raiz do Kaldi, um arquivo de áudio e
sua correspondente transcrição ortográfica. Podes também escolher a
arquitetura do modelo acústico que será usado para realizar o alinhamento.
Após selecioná-los, clica no botão `Alinhar`. Isso deve demorar um pouco.

![](doc/praat_menu.png)

Quando o alinhamento é concluído com sucesso, o alinhador oferece a opção de
exibir imediatamente o TextGrid resultante na interface do Praat ou prosseguir
para alinhar um novo arquivo de áudio.

A figura no início desse documento mostra o editor de TextGrid do Praat 
exibindo uma forma de onda do arquivo de áudio seguida por seu espectrograma 
e o TextGrid multicamadas resultante de alinhamento contendo cinco camadas: 
fonemas, sílabas, palavras, transcrição fonética e transcrição ortográfica, 
respectivamente.

O próprio editor TextGrid do Praat plota a forma de onda e o espectrograma do
arquivo de áudio, esta informação não é conteúdo do arquivo TextGrid. O Kaldi
fornece os traços azuis verticais, que correspondem às marcas de tempo,
enquanto a biblioteca de NLP do FalaBrasil fornece as transcrições fonéticas e
silábicas. Decidindo abrir imediatamente o TextGrid resultante na
interface Praat ou não, o arquivo TextGrid será salvo dentro de um diretório
chamado textgrid no diretório inicial com o mesmo nome do arquivo de áudio
que escolheste alinhar.

### Linha de Comando (CLI)

Basicamente tens de executar o arquivo `ufpalign.sh`. Sem nenhum argumento, ele
printa uma mensagem de ajuda. O comando abaixo funciona perfeitamente
utilizando o modelo monofone:

```bash
$ KALDI_ROOT=$HOME/kaldi bash ufpalign.sh demo/ex.wav demo/ex.txt mono
```

O arquivo [`demo/M-001.log`](demo/M-001.log) contém um exemplo de saída
completa do comando funcionando.

### Docker :whale:

Mais detalhes no diretório `docker/execution`.


## Simulação e Resultados

Com o intuito de prover um nível mínimo de reproducibilidade dos resultados,
o diretório `simulation` foi criado com scripts para executar o MFA e outros
alinhadores mais antigos baseados no HTK sobre a mesma base de teste, a fim de
avaliar a "acurácia" do UFPAlign por comparação.

Recomenda-se o uso da imagem docker em `docker/simulation`.


## Citação

Se utilizares qualquer recurso disponível nesse repositório, por favor nos cite
com a seguinte referência:

### [EURASIP 2022](https://asp-eurasipjournals.springeropen.com/articles/10.1186/s13634-022-00844-9)

> Batista, C., Dias, A.L. & Neto, N.
> Free resources for forced phonetic alignment in Brazilian Portuguese based on Kaldi toolkit.
> EURASIP J. Adv. Signal Process. 2022, 11 (2022).
> https://doi.org/10.1186/s13634-022-00844-9

```bibtex
@article{Batista22a,
    author     = {Batista, Cassio and Dias, Ana Larissa and Neto, Nelson},
    title      = {Free resources for forced phonetic alignment in Brazilian Portuguese based on Kaldi toolkit},
    journal    = {EURASIP Journal on Advances in Signal Processing},
    year       = {2022},
    month      = {Feb},
    day        = {19},
    volume     = {2022},
    number     = {1},
    pages      = {11},
    issn       = {1687-6180},
    doi        = {10.1186/s13634-022-00844-9},
    url        = {https://doi.org/10.1186/s13634-022-00844-9}
}
```

Verifica também o
[repositório do FalaBrasil para treino de modelos acústicos com o Kaldi](https://github.com/falabrasil/kaldi-br).


[![FalaBrasil](https://gitlab.com/falabrasil/avatars/-/raw/main/logo_fb_git_footer.png)](https://ufpafalabrasil.gitlab.io/ "Visite o site do Grupo FalaBrasil") [![UFPA](https://gitlab.com/falabrasil/avatars/-/raw/main/logo_ufpa_git_footer.png)](https://portal.ufpa.br/ "Visite o site da UFPA")

__Grupo FalaBrasil (2024)__ - https://ufpafalabrasil.gitlab.io/      
__Universidade Federal do Pará (UFPA)__ - https://portal.ufpa.br/     
Cassio Batista - https://cassiotbatista.github.io    
Larissa Dias   - larissa.engcomp@gmail.com     
