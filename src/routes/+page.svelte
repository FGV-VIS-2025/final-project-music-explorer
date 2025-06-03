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

    let nodeMap = new Map();

    let displayInfo = true;
    let infoArtist;
    $: console.log("info:", infoArtist);
</script>

<!-- <h1>Music explorer</h1> -->

<SearchArtist bind:artistId={searchArtist} bind:searching={expanding}/>
<ExpandedStack bind:expandedNodes
               bind:removeNode
               bind:expanding/>
<ArtistGraph importArtist={searchArtist}
             removeArtist={removeNode}
             bind:expandedNodes
             bind:expanding
             bind:nodeMap
             bind:selectedNode={infoArtist}/>
{#if displayInfo}
<div id="artist-info">
    <ArtistInfo artist={infoArtist}/>
</div>
{/if}


<style>
    #artist-info {
        position: fixed;
        top: 120px;
        bottom: 40px;
        right: 40px;
        z-index: 999;

        background-color: var(--accent-black);
        border-radius: 8px;
        border: 2px solid rgba(100, 100, 100, 0.6);

        padding: 10px;
        box-shadow: 0 0px 5px rgba(256, 256, 256, 0.25);
        /* height: 90%; */
        max-width: 500px;
        box-sizing: border-box;

        overflow-y: scroll;
        overflow-x: hidden;
    }
</style>
