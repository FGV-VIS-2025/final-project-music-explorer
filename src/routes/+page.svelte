<script>
    import ArtistGraph from "$lib/components/graphs/artist-graph.svelte";
    import SearchArtist from "$lib/components/selectors/get-artist.svelte";
    import ExpandedStack from "$lib/components/selectors/expanded-stack.svelte";
    import ArtistInfo from "$lib/components/artist-info.svelte";

    //Search variables
    let searchArtist;

    //Expansion control variables
    let expandedNodes = [];
    let removeNode;
    let expanding = false;


    let displayInfo = true;
    let infoArtist;
    $: console.log("info:", infoArtist);
</script>

<!-- <h1>Music explorer</h1> -->

<SearchArtist bind:artistId={searchArtist}/>
<ExpandedStack bind:expandedNodes
               bind:removeNode
               bind:expanding/>
<ArtistGraph importArtist={searchArtist}
             removeArtist={removeNode}
             bind:expandedNodes
             bind:expanding
             bind:selectedNodeId={infoArtist}/>
{#if displayInfo}
<div id="artist-info">
    <ArtistInfo artistId={infoArtist}/>
</div>
{/if}


<style>
#artist-info {
    position: fixed;
    bottom: 5%;
    right: 5%;
    z-index: 999;

    background-color: var(--accent-black);
    border-radius: 8px;
    border: 3px solid #FF0000;

    padding: 10px;
    box-shadow: 0 2px 10px rgba(256, 256, 256, 0.25);
    height: 90%;
    max-width: 500px;
    box-sizing: border-box;
}
</style>
