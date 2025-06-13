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

Os arquivos JSON resultantes desses dois scripts estarão disponíveis na pasta
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

A API pública do site é livre, não exigindo autenticação ou compra de planos para
seu uso. Apesar dessa liberdade, o acesso é restringido por alguns
[limites de uso](https://musicbrainz.org/doc/MusicBrainz_API/Rate_Limiting), que
são incompatíveis com o acesso de dados necessário para este trabalho.

Notavelmente, a construção do grafo de artistas usado na visualização é feita
usando a informação cruzada de várias entidades diferentes, como artistas,
gravações, trabalhos e lançamentos. Isso é necessário pois as
[relações padrão](https://musicbrainz.org/relationships) do site, que são retornadas
pela API para uma entidade, não são o suficiente para construir as relações desejadas
em um nó de nosso grafo. Logo, usar a API para gerar o grafo dinamicamente seria
um processo lento e incompatível com a responsabilidade desejada da página, pois
seriam necessárias diversas requisições à API do site.

Por isso, utilizamos uma abordagem que envolve fazer o download dos dumps do site
e processá-los usando Python, construindo arquivos JSON legíveis para o JavaScript
que executa em nossa página e que contém apenas as informações desejadas do grafo.
Os arquivos do dump são disponibilizados em arquivos `.tar.xz`, com tamanhos
compacatados que variam entre poucos megas até 16GB, e tamanhos descompactados
que podem exceder 200GB. Este diretório contém scripts Python capazes de processar
esses arquivos (ainda compactados) e gerar os arquivos JSON usados pelo site.

Além de arquivos focados no tratamento dos dumps da base de dados do MusicBrainz,
este diretório também contém scripts de webscrapping para realizar o download de
informações que não estão presentes nem nos dumps e nem na API, mas que são
usadas no site, como informações de gêneros.

(TODO: LISTAR INFORMAÇÕES DOS SCRIPTS E FUNCIONAMENTO BÁSICO)
