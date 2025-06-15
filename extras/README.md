# Processamento de dados

## Uso dos scripts

Os scripts devem ser todos executados do diretório `extras`, que contém
este readme.

Para gerar o grafo de gêneros, basta executar o script scrapper:

```bash
$ python musicbrainz-scrapper.py
```

Para gerar o grafo de artistas, antes de tudo, é necessário ter os seguintes
arquivos de dump baixados e colocados no diretório `tarxz`: `artist.tar.xz`,
`recording.tar.xz`, `release.tar.xz` e `work.tar.xz`. Após estarem devidamente
colocados no diretório, basta usar o script:

```bash
$ python process-artists.py
```

Para gerar as estatísticas de gêneros por ano, é necessário ter o seguinte dump
na devida pasta: `"release-group.tar.xz"`. O comando que deve ser executado é:

```bash
$ python process-genres.py
```

Os arquivos JSON resultantes desses três scripts estarão disponíveis na pasta
`outputs`.

Para dividir o arquivo dos grafos em arquivos menores, prontos para serem
carregados pelo site, é necessário executar:

```bash
$ python split-artists.py
```

## Sobre

Os dados do site MusicBrainz estão disponíveis para acesso de duas maneiras:

- Por meio de uma API pública, para a qual se fazem requisições HTTP para obter
os dados referentes à uma das entidades do site
(detalhadas [na documentação oficial](https://musicbrainz.org/doc/MusicBrainz_Database)).

- Por meio de [dumps do banco de dados do site](https://metabrainz.org/datasets/download),
que, como o nome sugere, são arquivos compactados contendo **todas** as informações
do site, divididas por entidade.

A API pública do site é livre, não exigindo autenticação ou compra de planos
para seu uso. Apesar dessa liberdade, o acesso é restringido por alguns
[limites de uso](https://musicbrainz.org/doc/MusicBrainz_API/Rate_Limiting), que
são incompatíveis com o acesso de dados necessário para este trabalho.

Notavelmente, a construção do grafo de artistas usado na visualização é feita
usando a informação cruzada de várias entidades diferentes, como artistas,
gravações, trabalhos e lançamentos. Isso é necessário pois as
[relações padrão](https://musicbrainz.org/relationships) do site, que são
retornadas pela API para uma entidade, não são o suficiente para construir as
relações desejadas em um nó de nosso grafo. Logo, usar a API para gerar o grafo
dinamicamente seria um processo lento e incompatível com a responsabilidade
desejada da página, pois seriam necessárias diversas requisições à API do site.

Por isso, utilizamos uma abordagem que envolve fazer o download dos dumps do
site e processá-los usando Python, construindo arquivos JSON legíveis para o
JavaScript que executa em nossa página e que contém apenas as informações
desejadas do grafo. Os arquivos do dump são disponibilizados em arquivos
`.tar.xz`, com tamanhos compacatados que variam entre poucos MiB até 16GiB, e
tamanhos descompactados que podem exceder 200GiB. Este diretório contém scripts
Python capazes de processar esses arquivos (ainda compactados) e gerar os
arquivos JSON usados pelo site.

Além de arquivos focados no tratamento dos dumps da base de dados do MusicBrainz,
este diretório também contém scripts de webscrapping para realizar o download de
informações que não estão presentes nem nos dumps e nem na API, mas que são
usadas no site, como informações de gêneros.

Abaixo está uma explicação de cada pré processamento usado.

### Grafo de gêneros

O grafo de gêneros é feito por meio de um webscrapping. Como os gêneros não são
uma entidade própriamente dita no esquema da base de dados MusicBrainz, não há
uma forma de modelá-los utilizando os dumps de dados ou a API. O webscrapping
inicia da página com a [lista de gêneros do site](https://musicbrainz.org/genres)
e a partir dela vai acessando as páginas de gêneros.

Dentro das páginas, as informações de interesse são as listas de relações entre
o gênero e os demais. O scrapper reconhece essas listas e acrescenta em uma
estrutura de dados própria, que no final do processo é salva no formato JSON.

Tanto a estrutura deste grafo quanto do grafo dos artistas é feita usando um
esquema de chaves e conjuntos. Cada gênero tem sua chave no dicionário, e o valor
é um outro dicionário que contém diferentes conjuntos, um para cada tipo de
relação, além de outras chaves para armazenar informações como nomes. Cada
conjunto contém as chaves para acessar as informações dos outros nós, agindo como
uma lista de adjacências.

Essa estrutura se difere da que é usada por bibliotecas como o D3.js para processar
grafos, já que não consiste em um conjunto de nós e um separado de arestas. A
escolha desse formato se deu pela conveniência para construir os grafos e pela
maior eficiência para acessar arestas, já que não é necessário percorrer um
conjunto de arestas em busca daquelas que tem como uma das pontas um nó específico.

### Grafo de artistas

O grafo de artistas é feito por meio da navegação do dump de dados. Existem duas
motivações para pré-processar o grafo:

- Processar os dumps em tempo real é inviável, dado a natureza dos dados
compactados. Para navegar nos dumps é necessário ler linha a linha até encontrar
o objeto desejado;
- Nem todas as relações presentes no grafo estão disponíveis facilmente neles.
As relações relacionadas com cover dependem de um abusca e lógica mais extensas
para serem inferidas.

Para processar o grafo, são usadas três entidades do MusicBrainz: "artists", que
representa um artista, seja solo ou grupo; "works", que representam músicas; e
"releases", que representam lançamentos de mídia física ou digital de uma música
ou álbum.

O processo exato para realizar as inferências é extenso e não será mostrado em
formato de algorítmo, e sim em resumos das principais etapas. Toda referência
a uma entidade nesse processo é feita por meio do ID dele no MusicBrainz.

1. Criação de um mapeamento de artistas. Usando um dicionário python, a base de
artistas é percorrida completamente e uma estrutura de dicionário é criada para
cada artista. Ela contém conjuntos para os diferentes tipos de relação, que
começam vazios, além de um contador de músicas autorais dos artistas. Nessa etapa
também já feito mapeamento das relações de participantes de grupos, já que essa
relação é presente nos dados.

2. Criação de um mapeamento auxiliar de works. Esse mapeamento, embora não faça
parte do grafo de artistas final, auxilia na próxima etapa. O dicionário de
cada work guarda seu nome e um conjunto de artistas que, em algum momento, já
gravaram aquele work (ou seja, performaram aquela música). Para isso, toda a base
de works é percorrida.

3. Inferência da autoria de works. No MusicBrainz, um work é associado às pessoas
que o compuseram, e não à um nome de grupo pelo qual foi feito o lançamento.
Consideramos mais intuitivo ter a autoria dada para grupos, já que um usuário
procura os seus grupos preferidos, e não membros desses grupos. Por isso, uma
estratégia própria é empregada para conseguir a autoria.

Essa estratégia consiste em averiguar todos os recordings da base (que incluem
recordings soltos e recordings associados à releases) e fazer contagens de quantas
vezes um determinado grupo ou artista solo foi associado a um recording (exceto
em casos onde é marcado que o recording é um cover). Os recordings, ao contrário
das works, tem a informação de qual nome o lançamento foi associado.

Após fazer essas contagens, é passado um filtro, e um artista é determinado como
autor caso represente mais de 25% de todas as associações vistas na etapa anterior.
Quando um artista é oficialmente dado como autor de uma música, seu contador de
músicas autorais também aumenta.

4. Inferência das relações de cover. Com as autorias definidas, os recordings
são percorridos novamente, e dessa vez os marcados como cover são averiguados.
Para cara recording marcado como cover, é construida uma aresta no grafo ligando
o artista associado ao recording com os autores inferidos do work que está sendo
referenciado no recording. Nessa etapa também são armazenados os anos em que os
covers foram feitos, baseado nas datas dos recordings.

Se o artista que fez o cover não tem nenhuma música dada como de sua autoria no
grafo, então uma aresta não é adicionada e o artista é completamente removido do
grafo. Essa foi uma escolha tomada para reduzir o tamanho total do grafo e remover
artistas que teriam baixa probabilidade de serem pesquisados, por não terem
músicas autorais.

o arquivo do grafo é salvo em JSON. Devido ao tamanho do arquivo estar por volta
de 150MiB, esse arquivo é separado em diversos arquivos menores, baseados no
inicio do ID dos artistas. Isso permite com que o site carregue dinamicamente
os arquivos durante a execução e sob demanda, evitando com que o usuário tenha
que esperar um logno período de tempo para começar a explorar.

### Estatísticas de gêneros

As estatísticas de gêneros são computadas utilizando os dumps de dados.
Conceitualmente, elas consistem em uma matriz que relaciona anos e gêneros, com
suas entradas sendo quantos "release groups" foram lançados com um gênero em um
ano específico. Os "release groups" são entidades do MusicBrainz que representam
álbuns músicais, singles, EPs (extended plays) e outros tipos de lançamentos
de música relacionados. Ou seja, na prática o que é calculado é quantas músicas/
albuns com aquele determinado gênero foram lançadas naquele determinado ano.

Na prática, esses dados são armazenados no formado JSON, e o processo para
calculá-los é bem simples:
- Percorra a base de "release groups" um a um. Para cada release group:
    - Salve sua data de lançamento, caso haja.
    - Para cada gênero associado ao release group atual:
        - Some 1 na base para entrada correspondente ao gênero e ao ano.

