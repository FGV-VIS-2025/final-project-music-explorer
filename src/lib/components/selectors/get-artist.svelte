<script>
	//Output of the component - an id of a selected artist
	export let artistId;

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

	function onResultClick(evt, index) {
		artistId = searchResults[index].id;
		showResults = false; // Hide results after an artist is selected
	}

	function toggleResultsVisibility() {
		showResults = !showResults;
	}
</script>

<div class="container">
	<form on:submit={searchArtists}>
		<div class="artistSearchBar">
			<button type="submit">Buscar</button>
			<input
				id="cityInput"
				type="text"
				bind:value={userInput}
				required
				placeholder="Busque um artista ou banda"
			/>
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
					on:click={(evt) => onResultClick(evt, index)}
				>
					{result.name}
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
		/* background-color: white; */
		/* padding: 10px; */
		/* border-radius: 8px; */
		/* box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); */
		width: 90%;
		max-width: 500px;
		box-sizing: border-box;
	}

	.artistSearchBar {
		display: flex;
		width: 100%;
		position: relative;
	}

	.artistSearchBar input {
		flex-grow: 1;
		padding: 10px;
		border: 2px solid #ccc;
		border-radius: 4px;
		padding-right: 80px;
	}

	.artistSearchBar button[type="submit"] {
		display: none;
		position: absolute;
		right: 0;
		top: 0;
		bottom: 0;
		padding: 0 15px;
		background-color: #007bff;
		color: white;
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
		margin-top: 10px;
		border: 1px solid #eee;
		border-radius: 4px;
		max-height: 200px;
		overflow-y: auto;
		background-color: #f9f9f9;
		padding: 5px;
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
</style>
