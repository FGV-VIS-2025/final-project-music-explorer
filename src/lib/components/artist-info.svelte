<script>
    import * as d3 from "d3";
    import { onMount } from "svelte";
    import ReleaseTimeseries from "$lib/components/charts/release-timeseries.svelte";
    import PieChart from "$lib/components/charts/pie.svelte";
    import BarChart from "$lib/components/charts/bar.svelte";
    //input of the component - artist to display info
    export let artist;
    export let nodeMap;
    export let expanding;
    export let activeLegend;
    export let barHighlight;
    let node;


    $: console.log(nodeMap);

    let searching = false;
	let successfulRequest = false;
	let successfulSearch = false;

	let svgNode;
	let width = 630;
	let height = 360;

	// To manage visibility of search results
	let searchResult;
    function lookupArtist(id) {
		if(id){
            searching = true;
            let link = `https://musicbrainz.org/ws/2/artist/${id}?fmt=json&inc=works+genres+annotation`;
            fetch(link)
                .then((response) => response.json())
                .then((data) => {
                    console.log(data);
                    searchResult = data;
                    successfulRequest = true;
                    successfulSearch = true;
                    searching = false;
                })
                .catch((error) => {
                    console.error("Error while searching for artist info:", error);
                    searchResult = null;
                    successfulRequest = false;
                    successfulSearch = false;
                    searching = false;
                });
		}
    }

    async function browseWorks(id){
        if(id){
            searching = true;
            let link = `https://musicbrainz.org/ws/2/work?artist=${id}&inc=genres&fmt=json`;
            let offset = 0;
            try {
                let response = await fetch(link);
                if(!response.ok){
                    throw new Error(`Erro HTTP, status ${response.status}`);
                }
                let data = await response.json();
                console.log(data);
                searchResult = data.works;
                while (data["work-count"] > offset + 25){
                    offset += 25;
                    let response = await fetch(`${link}&offset=${offset}`);
                    if(!response.ok){
                        throw new Error(`Erro HTTP, status ${response.status}`);
                    }
                    data = await response.json();
                    console.log(data);
                    searchResult = [...searchResult, ...data.works];
                }
                console.log(searchResult);
                successfulSearch = true;
                successfulSearch = true;
            } catch (error) {
                console.error("Error while searching for artist work:", error);
                successfulRequest = false;
                successfulSearch = false;
                searchResult = [];
            }
        }
    }

    let pieData;
    $: {
        if(artist){
            console.log(nodeMap);
            pieData = [["im", activeLegend.im ? artist.im.length: 0],
                    ["ms", activeLegend.ms ? artist.ms.length : 0],
                    ["cs", activeLegend.gc ? Object.keys(artist.cs).length : 0],
                    ["gc", activeLegend.cs ? artist.gc.length : 0]]
            console.log("artist pie", pieData);
        }
    }

    let barData;
    let selectedMusic;
    $: {
        if(artist && !expanding){
            console.log(nodeMap);
            if(artist.gc.length != 0) {
                barData = {};
                for (let coverArtist of artist.gc){
                    if (!nodeMap.has(coverArtist)){
                        console.warn("edge points to inexistent artist")
                        continue //I dont expect it to never reach this case but im proofing myself and putting this in.
                    }
                    for (let covered of nodeMap.get(coverArtist).cs[artist.id][1]){
                        if (covered in barData){
                            barData[covered].push(coverArtist);
                        } else {
                            barData[covered] = [coverArtist];
                        }
                    }
                }
                console.log("artist bar", barData);
            } else {
                barData = null;
                barHighlight = null;
            }
        }
    }
    $: {
        if (selectedMusic){
            barHighlight = barData[selectedMusic];
        } else {
            barHighlight = null;
        }
    }

    let mounted = false;
    onMount(() => {
        if(artist){
            lookupArtist(artist.id).then(() => {
                mounted = true;
            })
        } else {
            mounted = true;
        }
    })

	let oldSelection = null;
    $: {
        if (artist && mounted && (artist.id !== oldSelection)) {
            lookupArtist(artist.id);
			oldSelection = artist.id;
        }
    }

    function checkDate(date){
        return date && date != "" && !date.startsWith("?");
    }

    function manageDate(dateString){
        if(dateString.length == 4){
            return dateString
        }
        //If it comes here means we have a month and so we want it
        if(dateString.length == 7){
            dateString = dateString + "-01"
        }
        const options = {year: "numeric", month: "short"};
        return new Date(dateString).toLocaleDateString("pt-BR", options);
    }

</script>

{#if searching}
    <p class = "loading">🛈 Carregando informações do artista... Aguarde</p>
{:else if !successfulSearch}
    <p class = "error">Houve um problema ao carregar as informações do artista.</p>
{:else if searchResult}
    <h1>{artist.n}</h1>
    {#if checkDate(searchResult["life-span"].begin) && checkDate(searchResult["life-span"].end)}
        <span class="headline">
            <i>Artista ativo de {manageDate(searchResult["life-span"].begin)}
            até {manageDate(searchResult["life-span"].end)}.</i>
        </span>
    {:else if checkDate(searchResult["life-span"].begin)}
        <span class="headline">
            <i>Artista ativo desde {manageDate(searchResult["life-span"].begin)}.</i>
        </span>
    {:else if checkDate(searchResult["life-span"].end)}
        <span class="headline">
            <i>Artista ativo até {manageDate(searchResult["life-span"].begin)}.</i>
        </span>
    {/if}
    {#if searchResult.genres.length > 0}
        <p>Principais gêneros musicais do artista: {searchResult.genres.map(d => d.name).join(", ")}</p>
    {/if}
    <h4>Histórico de lançamentos (álbuns, EPs e Singles)</h4>
    <ReleaseTimeseries bind:artistId={artist.id}/>
{/if}
{#if pieData}
    <h4>Proporção dos tipos de relação do artista</h4>
    <PieChart data={pieData} name={artist.n}/>
{/if}
{#if barData && !expanding}
    <h4>Músicas de {artist.n} mais regravadas</h4>
    <BarChart data={barData} bind:selectedMusic={selectedMusic}/>
{/if}

<style>
    h1 {
        margin: auto;
        text-align: center;
    }

    .headline {
        text-align: center;
        margin-bottom: 5px;
        margin: auto;
    }


    .loading{
        background-color: #4f8285;
        padding: 3px;
        border: solid 2px #76bbbc;
        border-radius: 5px;
        font-size: 100%
    }

    .error{
        background-color: #e43333;
        padding: 3px;
        border: solid 2px #ff4242;
        border-radius: 5px;
        font-size: 100%
    }
</style>
