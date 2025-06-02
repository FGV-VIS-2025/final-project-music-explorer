<script>
	//Output of the component - an id of a selected artist
	export let artistId;
	//Shared resource - lock when graph is expanding

	//To get what the user typed
	let userInput;
	//To manage search success
	let interacted = false;
	let searching = false;
	let successfulRequest = false;
	let successfulSearch = false;
	//To manage user choice on results
	let searchResults = [];
	// To manage visibility of search results
	let showResults = false;

	function searchArtists(evt) {
		evt.preventDefault();
		interacted = true;
		searching = true;
		showResults = true; // Show results when a new search is initiated
		let link = `https://musicbrainz.org/ws/2/artist?fmt=json&query=${userInput}`;
		fetch(link)
			.then((response) => response.json())
			.then((data) => {
				searching = false;
				successfulRequest = true;
				console.log(data);
				if (data.artists.length > 0) {
					console.log(data);
					successfulSearch = true;
					searchResults = data.artists;
				} else {
					successfulSearch = false;
					searchResults = [];
				}
			})
			.catch((error) => {
				console.error("Error while searching for places:", error);
				successfulRequest = false;
				successfulSearch = false;
				searchResults = [];
			});
	}

	function onResultClick(evt, index, name) {
		artistId = searchResults[index].id;
		userInput = name;
		showResults = false; // Hide results after an artist is selected
	}

	function toggleResultsVisibility() {
		showResults = !showResults;
	}
</script>

<div class="container">
	<form on:submit={searchArtists}>
		<div class="artistSearchBar">
			<input
				id="cityInput"
				type="text"
				bind:value={userInput}
				required
				placeholder="Busque um artista ou banda"
			/>
			<button type="submit">Buscar</button>
		</div>
	</form>

	{#if interacted === false}
		<!-- <p>Nenhuma busca foi feita.</p> -->
	{:else if searching === true}
		<!-- <p>Pesquisando artistas... Aguarde.</p> -->
	{:else if successfulRequest === false}
		<!-- <p class="erro">Erro na busca. Tente novamente.</p> -->
	{:else if successfulSearch === false}
		<!-- <p class="erro"> -->
		<!--     Busca sem resultados. Dê preferência por digitar nomes completos de -->
		<!--     artistas ao invés de apenas um pedaço do nome. -->
		<!-- </p> -->
	{:else if showResults}
		<div class="results">
			{#each searchResults as result, index}
				<button
					class="searchResult"
					on:click={(evt) => onResultClick(evt, index, result.name)}
				>
					{result.name}
					{#if result.disambiguation}
						<span class="disambiguation">({result.disambiguation})</span>
					{/if}
				</button>
			{/each}
		</div>
	{/if}

	<!-- {#if artistId} -->
	<!--     <p>Id do selecionado: {artistId}</p> -->
	<!-- {/if} -->
</div>

<style>
	.container {
		position: fixed;
		top: 40px;
		left: 50%;
		transform: translateX(-50%);
		z-index: 1000;

		width: 90%;
		max-width: 500px;
		box-sizing: border-box;
	}

	.artistSearchBar {
		display: flex;
		width: 100%;
		position: relative;
		box-shadow: 0px 0px 5px rgba(255, 255, 255, 0.6);


		border-radius: 4px;
	}

	.artistSearchBar input {
		flex-grow: 1;
		padding: 10px;
		border: none;
		padding-right: 80px;
		border-radius: 4px 0 0 4px;

		background-color: var(--accent-black);
	}

	.artistSearchBar input:focus {
		outline: #0056b3;
	}

	.artistSearchBar button[type="submit"] {
		padding: 0 15px;

		color: white;
		background-color: #007bff;

		border: none;
		border-radius: 0 4px 4px 0;
		
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.artistSearchBar button[type="submit"]:hover {
		background-color: #0056b3;
	}

	.results {
		overflow-y: auto;
		max-height: 200px;
		
		padding: 5px;
		margin-top: 10px;
		
		border: 1px solid #eee;
		border-radius: 4px;
		
		background-color: #f9f9f9;
		
	}

	.searchResult {
		display: block;
		width: 100%;
		padding: 10px;
		text-align: left;
		border: none;
		background: none;
		cursor: pointer;
		border-bottom: 1px solid #eee;
		font-size: 1rem;
		color: black;
	}

	.searchResult:last-child {
		border-bottom: none;
	}

	.searchResult:hover {
		background-color: #e9e9e9;
		border-radius: 4px;
	}

	.erro {
		color: #dc3545;
		margin-top: 10px;
	}

	.toggle-button {
		margin-top: 10px;
		padding: 8px 15px;
		background-color: #6c757d;
		color: white;
		border: none;
		border-radius: 4px;
		cursor: pointer;
	}

	.toggle-button:hover {
		background-color: #5a6268;
	}

	.disambiguation {
		font-size: 80%;
		color: gray;
	}
</style>
