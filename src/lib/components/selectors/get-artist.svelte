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
    let selectedResult;

    function searchArtists(evt) {
        evt.preventDefault();
        interacted = true;
        searching = true;
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
                    selectedResult = 0;
                } else {
                    successfulSearch = false;
                    searchResults = [];
                    selectedResults = -1;
                }
            })
            .catch((error) => {
                console.error("Error while searching for places:", error);
                successfulRequest = false;
                successfulSearch = false;
                searchResults = [];
                selectedResult = -1;
            });
    }

    function onResultClick(evt, index) {
        selectedResult = index;
    }

    $: {
        if (searchResults.length > 0) {
            artistId = searchResults[selectedResult].id;
        } else {
            artistId = null;
        }
    }
</script>

<div class="container">
    <h3>Busque por um artista.</h3>
    <form on:submit={searchArtists}>
        <label for="cityInput">
            Escreva o nome de um artista ou banda e aperte em buscar.
        </label>
        <div class="searchBar">
            <input id="cityInput" type="text" bind:value={userInput} required />
            <button type="submit">Buscar</button>
        </div>
    </form>

    {#if interacted == false}
        <p>Nenhuma busca foi feita.</p>
    {:else if searching == true}
        <p>Pesquisando artistas... Aguarde.</p>
    {:else if successfulRequest == false}
        <p class="erro">Erro na busca. Tente novamente.</p>
    {:else if successfulSearch == false}
        <p class="erro">
            Busca sem resultados. Dê preferência por digitar nomes completos de
            artistas ao invés de apenas um pedaço do nome.
        </p>
    {:else}
        <div class="results">
            {#each searchResults as result, index}
                {#if selectedResult == index}
                    <button
                        class="searchResult selected"
                        on:click={(evt) => onResultClick(evt, index)}
                    >
                        {result.name}
                    </button>
                {:else}
                    <button
                        class="searchResult"
                        on:click={(evt) => onResultClick(evt, index)}
                    >
                        {result.name}
                    </button>
                {/if}
            {/each}
        </div>
    {/if}
    {#if successfulSearch}
        <p>Id do selecionado: {artistId}</p>
    {/if}
</div>

<!--<style>
    /*Coloquei borda aqui pra não me perder na estilização dos outros componentes.  Depois é só tirar*/
    .container {
        border-style: solid;
        border-radius: 6px;
        border-width: 2px;

        margin-bottom: 20px;

        padding: 2ch;
        position: relative;
    }

    h3 {
        margin: auto;
        text-align: justify;
    }

    .searchBar {
        margin: 5px 0;

        display: grid;
        grid-template-columns: auto 7ch;
        gap: 1ch;
    }

    .erro {
        color: #ff4c4c;
    }

    .results {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
    }

    .searchResult {
        max-width: 20ch;

        margin: 4px;

        border-style: solid;
        border-color: #777777;
        border-width: 2px;
        border-radius: 4px;

        padding: 6px;

        font-size: 75%;
        color: #e6e6e6;
        text-transform: uppercase;
        font-weight: bold;
    }

    .selected {
        border-color: #2f05d9b6;
        background-color: #2f05d93a;
    }

    .highlight {
		background-color: #f1f1f1;
		color: #000;
		display: inline-block;
		margin: 3px 0;
		padding: 3px;
		font-weight: bold;
		cursor: default;
	}

    .tip {
		color: gray;
		border-bottom: 2px dashed #aaa;
	}
</style>-->
