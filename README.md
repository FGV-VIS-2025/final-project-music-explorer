# Link para o vídeo da entrega final

https://drive.google.com/drive/folders/18VkuCk7kAVLHZSQ55fXizphtAgaclS4O?usp=drive_link

# create-svelte

Everything you need to build a Svelte project, powered by [`create-svelte`](https://github.com/sveltejs/kit/tree/master/packages/create-svelte).

## Creating a project

If you're seeing this, you've probably already done this step. Congrats!

```bash
# create a new project in the current directory
npm create svelte@latest

# create a new project in my-app
npm create svelte@latest my-app
```

## Developing

Once you've created a project and installed dependencies with `npm install` (or `pnpm install` or `yarn`), start a development server:

```bash
npm run dev

# or start the server and open the app in a new browser tab
npm run dev -- --open
```

## Building

To create a production version of your app:

```bash
npm run build
```

You can preview the production build with `npm run preview`.

> To deploy your app, you may need to install an [adapter](https://kit.svelte.dev/docs/adapters) for your target environment.

# Pôster

## Introdução

Música é um tema muito vasto e presente diariamente em nossas vidas. São inúmeras
as pessoas que dedicam parte de seu tempo para ouvir música, e igualmente massivo
é o número de pessoas que produzem novas músicas, desde pequenos artistas
independentes até grandes nomes que produzem e lançam _hits_ anualmente.

Quando se observa a industria músical atualmente, percebe-se que existem muitas
relações entre as pessoas e grupos que a compõe. Indo desde artistas que colaboram
para a produção de uma música até artistas que se juntam em um grupo para fazer
novas composições, as relações são incontáveis.

Este trabalho tem como objetivo fornecer uma ferramenta que utilize conceitos da
área de visualização de dados e permita ao usuário explorar melhor essas relações,
empoderando-o para que ele possa descobrir interações entre artistas específicos
e entender como um artista se posiciona nesse universo em relação aos demais.

## Dados

Os dados utilizados para desenvolver o trabalho são provenientes da base de dados
MusicBrainz. Esta é uma base de acesso livre e gratuito que visa ser referência
de acesso à metadados da industria músical. São disponibilizados dados de artistas,
músicas, gravações, lançamentos e outros tipos de entidades, e o acesso é feito
tanto via API REST quanto via download de uma cópia da base de dados.

## Métodologia

O processamento inicial dos dados brutos da base de dados do site foi feito com
a linguagem de programação _Python_. Foi feito um programa que percorre as
informações de artistas, músicas e gravações para tanto mapear as relações já
presentes nos dados quanto inferir outras.

Com as relações e outros metadados de artistas tratados, o passo seguinte foi o
desenvolvimento da página web que contém as visualizações. Para desenvolvê-la
foram utilizadas tecnologias web com o auxilio do framework _Svelte_. As
visualizações foram feitas utilizando a biblioteca _D3.js_.

## Visualizações

A principal forma de visualização das relações mapeadas entre artistas é um grafo
interativo. Cada nó do grafo representa um artista (pessoa individual ou banda)
e as arestas representam artistas que tem algum tipo de relação direta. São
oferecidas as operações de expansão, foco e remoção de nós/artistas do grafo,
de forma que o usuário possa navegar enquanto mantém os artistas de seu interesse
sendo exibidos. As cores dos nós codificam os diferentes tipos de relação que
existem entre os artistas.

Com o auxílio dos dados de API, também está disponível uma barra de pesquisa
para encontrar artistas específicos e uma sidebar com informações extras sobre
o artista selecionado, como por exemplo histórico de lançamentos, gêneros das
músicas, proporção dos tipos de relação, etc.

Também há uma visualização secundária em forma de dendrograma para visualizar
relações entre gêneros. Visualizar os diferentes tipos de gêneros permite que
um usuário entenda melhor como um artista se posiciona no mundo da música e quais
gêneros possívelmente influenciam suas produções.
