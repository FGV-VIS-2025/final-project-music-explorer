<script>
    import * as d3 from "d3";
    import { onMount } from "svelte";
    import ReleaseTimeseries from "$lib/components/charts/release-timeseries.svelte";
    import PieChart from "$lib/components/charts/pie.svelte"
    //input of the component - artist to display info
    export let artist;
    export let nodeMap;
    export let expanding;
    export let activeLegend;
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
            console.log(pieData);
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

    $: {
        if(artist && mounted){
            lookupArtist(artist.id);
        }
    }

</script>

{#if searching}
    <p>Carregando informações do artista... Aguarde</p>
{:else if !successfulSearch}
    <p>Houve um problema ao carregar as informações do artista.</p>
{:else if searchResult}
    <h1>{searchResult.name}</h1>
    {#if searchResult["life-span"].ended && searchResult["life-span"].begin && searchResult["life-span"].end}
        <i>Artista ativo de {searchResult["life-span"].begin} até {searchResult["life-span"].end}.</i>
    {:else if searchResult["life-span"].begin}
        <i>Artista ativo desde {searchResult["life-span"].begin}.</i>
    {/if}
    {#if searchResult.genres.length > 0}
        <p>Principais gêneros musicais do artista: {searchResult.genres.map(d => d.name).join(", ")}</p>
    {/if}
    <h4>Histórico de lançamentos (álbuns, EPs e Singles)</h4>
    <ReleaseTimeseries bind:artistId={artist.id}/>
{/if}
{#if pieData}
    <h4>Proporção dos tipos de relação do artista</h4>
    <PieChart data={pieData}/>
{/if}
