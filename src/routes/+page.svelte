<script>
	import ArtistGraph from "$lib/components/graphs/artist-graph.svelte";
	import SearchArtist from "$lib/components/selectors/get-artist.svelte";
	import ExpandedStack from "$lib/components/selectors/expanded-stack.svelte";
	import ArtistInfo from "$lib/components/artist-info.svelte";

	import CollapsibleTree from "$lib/components/graphs/genres-tree.svelte";
	import rawData from "$lib/data/genres.json";
	import { getHighlightedPathForGenreTree } from "$lib/utils/genreTreeUtils";

	import { image } from "d3";
	import { onMount } from 'svelte';

	import Histogram from "$lib/components/charts/histogram.svelte";
	import genreYearData from "$lib/data/genres_map.json";

	//Search variables
	let searchArtist;
	let failedFinding;

	//Expansion control variables
	let expandedNodes = [];
	let removeNode;
	let expanding = false;
	let activeLegendItems;

	//artist info sidebar related variables
	let nodeMap = new Map();
	let displayInfo = true;
	let infoArtist;
	let forceHighlight;

	$: console.log("info:", infoArtist);

	$: infoDisplay = displayInfo ? "block" : "none";

	function showInfo() {
		displayInfo = !displayInfo;
	}

	let searchTerm = "";
	let hierarchicalData;
	let highlightedNodeNames = new Set();

	$: {
		const {
			hierarchicalData: newHierarchy,
			highlightedNames: newHighlightedNames,
		} = getHighlightedPathForGenreTree(rawData, searchTerm);

		hierarchicalData = newHierarchy;
		highlightedNodeNames = newHighlightedNames;
	}

	function handleSubmit(event) {
		event.preventDefault();
	}

	let clickedGenre = "";
	let treeClickedGenre = "";
	let histogramGenre = "";
	let genreOptions = [];
	let genreSearch = [];

	$: genreOptions = Object.keys(genreYearData);

	$: if (clickedGenre) {
		searchTerm = clickedGenre;
		histogramGenre = clickedGenre;
	};

	$: {
		console.log(treeClickedGenre);
		if (treeClickedGenre){
			histogramGenre = treeClickedGenre;
		}
	}

	$: {
		if(searchTerm != ""){
			if(genreOptions.includes(searchTerm)){
				histogramGenre = searchTerm;
				genreSearch = [];
			} else {
				genreSearch = genreOptions.filter(key => key.includes(searchTerm));
				if(genreSearch.length == 1){
					histogramGenre = genreSearch[0]
				}
			}
		} else {
			genreSearch = [];
		}
	}

	const defaultTargetId = 'info';

	// onMount(() => {
	// 	window.location.hash = defaultTargetId;
	// 	const targetElement = document.getElementById(defaultTargetId);
	// 	if (targetElement) {
	// 		targetElement.scrollIntoView({ behavior: 'smooth' });
	// 	}
	// });
</script>

<div id="start">
	<div id="info">
		<div id="intro-text">
			<div class="subitem">
				<div>
					<h1>Music Explorer</h1>
				</div>
				<div>
					<p>
						A <a target="_blank" href="https://pt.wikipedia.org/wiki/M%C3%BAsica">
						música</a> é um tema muito vasto e presente diariamente no cotidiano da
						população. São inúmeras as pessoas que dedicam parte de seu tempo
						para ouvir música, e igualmente massivo é o número de pessoas que
						produzem novas músicas, desde pequenos artistas independentes até
						grandes nomes que produzem e lançam hits anualmente.
					</p>
					<p>
						Quando se observa a industria músical atualmente, percebe-se que existem
						muitas relações entre as pessoas e grupos que a compõe. Indo desde artistas
						que colaboram para a produção de uma música até artistas que se juntam
						em um grupo para fazer novas composições, as relações são incontáveis.
					</p>
					<p>
						Este site tem como objetivo fornecer uma ferramenta fundamentada
						em princípios da visualização de dados para exibir essas relações
						e outras informações pertinentes sobre o tema. Por meio de um grafo
						interativo, é possível obter diversos <i>insights</i> sobre o
						mundo da música e sobre como diferentes artistas se relacionam.
					</p>
					<p>
						O grafo inicia com um artista e suas relações. Para explorar algum artista
						visível, aperte nele. Para explorar um artista que não está
						sendo exibido, busque na barra de pesquisa (e tenha em mente
						que artistas sem relações ou de tributo não aparecem no grafo).
						Experimente interagir com a legenda e com as tags que ficam
						na barra laterial para descobrir mais interações!
					</p>
					<p><i style="font-size: 90%">As primeiras interações serão mais lentas
					devido ao carregamento dos artistas. Depois de algumas explorações,
					a experiência se tornará mais fluida.</i>
					</p>

					<a href="#graph1" class="explore"> Explorar! </a>
				</div>
			</div>
			<div class="subitem">
				<div>
					<h2 style="margin-top: auto;">Sobre a página</h2>
				</div>
				<div>
					<p>
						Essa página foi desenvolvida como entrega para o projeto final da disciplina
						de Visualização de Dados, matéria da graduação em Ciência de Dados e Inteligência
						Artifical da FGV-EMAp.
					</p>
						<div id = "external-resources">
							<a href="https://github.com/FGV-VIS-2025/final-project-music-explorer" target="_blank" class="resource"> GitHub do projeto </a>
							<a href="https://github.com/FGV-VIS-2025/final-project-music-explorer" target="_blank" class="resource"> Paper </a>
							<a href="https://github.com/FGV-VIS-2025/final-project-music-explorer" target="_blank" class="resource"> Vídeo de demonstração </a>
						</div>
					<div id="authors">
					<h2>Autores</h2>
						<ul>
							<li>
								<a href="https://github.com/ddanieldma" target="_blank">
									<span class="link-text">Daniel Miranda</span>
									<img src="github-mark.svg" alt="github">
								</a>
							</li>
							<li>
								<a href="https://github.com/pedrotokar" target="_blank">
									<span class="link-text">Pedro Tokar</span>
									<img src="github-mark.svg" alt="github">
								</a>
							</li>
							<li>
								<a href="https://github.com/vitor-n" target="_blank">
									<span class="link-text">Vitor do Nascimento</span>
									<img src="github-mark.svg" alt="github">
								</a>
							</li>
						</ul>
					</div>
				</div>
			</div>
		</div>
		<a href="#graph1" class="arrow-down-dummy">
			<img src="icons/arrow_down.svg" alt="" />
		</a>
	</div>

	<div id="graph1">
		<a href="#info" class="arrow-up">
			<img src="icons/arrow_up.svg" alt="" />
		</a>
		<a href="#graph2" class="arrow-down">
			<img src="icons/arrow_down.svg" alt="" />
		</a>
		<div id="search-bar">
			<SearchArtist
				bind:artistId={searchArtist}
				bind:searching={expanding}
				bind:failedFinding
			/>
		</div>
		<div id="expanded-stack">
			<ExpandedStack
				bind:expandedNodes
				bind:removeNode
				bind:expanding
				bind:selectedNode={infoArtist}
			/>
		</div>
		<ArtistGraph
			importArtist={searchArtist}
			removeArtist={removeNode}
			bind:expandedNodes
			bind:expanding
			bind:nodeMap
			bind:selectedNode={infoArtist}
			bind:activeLegendItems
			{forceHighlight}
			bind:failedFinding
			selectedNodeId={infoArtist ? infoArtist.id : null}
		/>

		<button on:click={showInfo} id="display-button" style="border: none;">
			{#if displayInfo}
				<img src={`icons/close.svg`} height="20rem" alt="close" />
			{:else}
				<img src={`icons/chevron_left.svg`} height="20rem" alt="show" />
			{/if}
		</button>

		<div id="artist-info" style="display: {infoDisplay};">
			<ArtistInfo
				artist={infoArtist}
				activeLegend={activeLegendItems}
				{nodeMap}
				{expanding}
				bind:barHighlight={forceHighlight}
				bind:clickedGenre={clickedGenre}
			/>
		</div>
	</div>

	<div id="graph2">
		<a href="#graph1" class="arrow-up">
			<img src="icons/arrow_up.svg" alt="" />
		</a>
		<a href="#info" class="arrow-down">
			<img src="icons/home.svg" alt="" />
		</a>

		<div class="container">
			<form on:submit={handleSubmit} autocomplete="off">
				<div class="artistSearchBar">
					<input
						id="cityInput"
						type="text"
						bind:value={searchTerm}
						required
						placeholder="Busque por um gênero"
					/>
				</div>
			</form>
			{#if genreSearch.length > 1}
				<div class="results">
				{#each genreSearch as result, index}
					<button
						class="searchResult"
						on:click={(evt) => {searchTerm = result;}}
					>
						{result}
					</button>
				{/each}
				</div>
			{/if}
		</div>

		<main>
			{#if hierarchicalData}
				<CollapsibleTree
					data={hierarchicalData}
					highlightedNames={highlightedNodeNames}
					bind:clickedGenre={treeClickedGenre}
				/>
			{:else}
				<p>Carregando ou nenhum dado de gênero disponível.</p>
			{/if}
		</main>

		<div style="position: fixed; top: 50vh;transform: translateY(-50%); right: 40px;">
			{#if histogramGenre && genreYearData[histogramGenre]}
				<h4>Histograma de lançamentos com o gênero {histogramGenre}.</h4>
				<Histogram data={genreYearData[histogramGenre]} /><br>
				<i style="text-size: 90%; text-align: right">
					Explore a árvore clicando em seus nós.
				</i>
			{:else if histogramGenre}
				<h4>Sem informações de lançamento para o gênero {histogramGenre}</h4>
			{:else}
				<p style = "max-width: 60ch; text-align: center;">
					Experimente clicar em um gênero das informações de um artista do
					grafo ou fazer uma busca na barra acima. Você também pode explorar
					a árvore clicando em seus nós!
				</p>
			{/if}
		</div>
	</div>
</div>

<!---->
<!-- <div id="chart-selector"> -->
<!-- 	<ul> -->
<!-- 		<li> -->
<!-- 			<input type="radio" name="chart" id="chart1"> -->
<!-- 			<label for="chart1">chart1</label> -->
<!-- 		</li> -->
<!-- 		<li> -->
<!-- 			<input type="radio" name="chart" id="chart2"> -->
<!-- 			<label for="chart2">chart2</label> -->
<!-- 		</li> -->
<!-- 		<li> -->
<!-- 			<input type="radio" name="chart" id="chart3"> -->
<!-- 			<label for="chart3">chart3</label> -->
<!-- 		</li> -->
<!-- 		<li> -->
<!-- 			<input type="radio" name="chart" id="chart4"> -->
<!-- 			<label for="chart4">chart4</label> -->
<!-- 		</li> -->
<!---->
<!-- 	</ul> -->
<!-- </div> -->
<!---->
<style>
	#start {
		height: 100vh;
		overflow-y: hidden;
		scroll-behavior: smooth;
	}

	#info {
		padding: 5% 10% 5% 10%;
	}

	#info h1 {
		color: #ffffe3;
		font-family: "Neco", sans-serif;
		font-size: 82pt;
		margin: 0 0;
	}

	#info .explore {
		background-color: white;
		padding: 5px;
		border-radius: 2px;
		color: black;
		font-weight: bolder;
		text-decoration: none;
	}

	#info:not(:target) .arrow-down-dummy {
		display: none;
	}


	#intro-text{
		display: grid;
		grid-template-columns: 65% 35%;
		align-items: baseline;
	}

	#intro-text div {
		padding-right: 5%;
	}

	.subitem {
		display: grid;
		grid-template-columns: subgrid;
	}

	#authors a {
		text-decoration: none;
		display: inline-flex;
		align-items: center;
		gap: 6px;
	}
	#external-resources {
		display: flex;
        flex-wrap: wrap;
	}

	a.resource {
		/* color: var(--accent-black); */
		background-color: #444;
		text-decoration: none;
		font-size: 100%;
		border-radius: 4px;
		padding: 4px;
		margin: 0 1ch 0 0;
/* 		font-weight: bold; */
	}

	li {
		margin: 1em 0;
	}
	li img {
		height: 1em;
		filter: invert(1);
	}

	.link-text {
		text-decoration: underline;
	}

	.arrow-down-dummy {
		filter: invert(1);
		z-index: 999 !important;
	}

	.arrow-up {
		background-color: var(--accent-black);
		border-radius: 0 0 6px 6px;
		position: absolute;
		left: 50%;
		transform: translateX(-50%);
	}

	.arrow-down-dummy,
	.arrow-down {
		background-color: var(--accent-black);
		border-radius: 6px 6px 0 0;
		position: absolute;
		bottom: 0;
		left: 50%;
		transform: translateX(-50%);
	}

	.arrow-down-dummy img,
	.arrow-down img,
	.arrow-up img {
		display: block;
	}

	.arrow-down:hover,
	.arrow-up:hover {
		filter: invert(1);
		z-index: 999;
	}

	#graph1,
	#graph2 {
		display: block;
		position: relative;
		box-sizing: border-box;
		filter: blur(9px);
		pointer-events: none;
		transition: filter cubic-bezier(0.25, 0.46, 0.45, 0.94) 0.5s;
	}

	#graph1:target,
	#graph2:target {
		filter: none;
		pointer-events: all;
	}

	#graph2 {
		box-sizing: border-box;
		background-color: var(--accent-black);
	}

	#chart-selector {
		position: fixed;
		top: 120px;
		right: 40px;
		display: flex;
		align-items: center;
		border: 1px solid antiquewhite;
		border-radius: 4px;
		width: 500px;
		height: 40px;
	}

	#chart-selector ul {
		list-style-type: none;
		padding: 0;
		margin: 0;
		display: flex;
		width: 90%;
		height: 100%;
		justify-content: space-around;
		align-items: center;
	}

	#chart-selector li {
		height: 100%;
		float: left;
		flex-grow: 1;
		text-align: center;
		display: flex;
		justify-content: center;
		align-items: center;

		background-color: blue;
	}

	#chart-selector label {
		cursor: pointer;
		height: 100%;
		display: flex;
		text-align: center;
		justify-content: center;
	}

	#chart-selector input[type="radio"] {
		appearance: none;
	}

	#chart-selector input[type="radio"]:checked + label {
		background-color: yellow;
	}

	#display-button {
		position: absolute;
		top: 130px;
		right: 45px;
		z-index: 1000;
		cursor: pointer;
		display: flex;
	}

	#search-bar {
		position: absolute;
		top: 40px;
		right: 40px;
		width: 500px;
	}

	#artist-info {
		position: absolute;
		top: 120px;
		bottom: 40px;
		right: 40px;
		z-index: 900;

		background-color: var(--accent-black);
		border-radius: 8px;
		border: 2px solid rgba(100, 100, 100, 0.6);

		padding: 10px;
		box-shadow: 0 0px 5px rgba(256, 256, 256, 0.25);
		/* height: 90%; */
		width: 500px;
		box-sizing: border-box;

		overflow-y: scroll;
		overflow-x: hidden;
	}

	#expanded-stack {
		position: absolute;
		left: 40px;
		bottom: 40px;
	}

	.container {
		position: fixed;
		top: 40px;
		right: 40px;
		z-index: 1000;

		width: 90%;
		max-width: 500px;
		box-sizing: border-box;
	}

	.artistSearchBar {
		display: flex;
		width: 100%;
		position: relative;
		background-color: rgba(100, 100, 100, 0.6);
		box-shadow: 0px 0px 5px rgba(100, 100, 100, 0.6);
		border-radius: 8px;
		overflow: hidden;
	}

	.artistSearchBar input {
		flex-grow: 1;
		padding: 12px 15px;
		border: none;
		border-radius: 6px 0 0 6px;
		background-color: var(--accent-black);
		color: white;
		font-size: 1rem;
		position: relative;
		z-index: 1;
	}

	.artistSearchBar input:focus {
		outline: #0056b3;
	}

	.artistSearchBar button[type="submit"] {
		padding: 0 18px;
		color: white;
		background-color: #007bff;
		border: none;
		border-radius: 0 6px 6px 0;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 1rem;
		font-weight: bold;
		position: relative;
		z-index: 1;
		transition: background-color 0.2s ease;
	}

	.artistSearchBar button[type="submit"]:hover {
		background-color: #0056b3;
	}

	    .results {
		position: relative;
        overflow-y: auto;
        max-height: 200px;
        padding: 5px;
        margin-top: 10px;
        border-radius: 6px;
        background-color: #f9f9f9;
        z-index: 1000;
    }

    .searchResult {
        display: block;
        width: 100%;
        padding: 12px 15px;
        text-align: left;
        border: none;
        background: none;
        cursor: pointer;
        border-bottom: 1px solid #eee;
        font-size: 0.95rem;
        color: #333;
        transition: background-color 0.15s ease;
        z-index: 1000;
    }

	.searchResult:last-child {
		border-bottom: none;
	}

    .searchResult:hover,
	.searchResult:focus {
		background-color: #e9e9e9;
		border-radius: 4px;
	}

	/* main { */
	/* 	background-color: var(--accent-black); */
	/* } */
</style>
