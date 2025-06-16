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
    let activeLegendItems;

    //artist info sidebar related variables
    let nodeMap = new Map();
    let displayInfo = true; // Sidebar starts as visible
    let infoArtist;
    let forceHighlight;

    $: console.log("info:", infoArtist);

    function showInfo() {
        displayInfo = !displayInfo;
    }
</script>

<div class="app-container">
    <div class="main-content">
        <SearchArtist bind:artistId={searchArtist} bind:searching={expanding}/>
        <ExpandedStack bind:expandedNodes
                       bind:removeNode
                       bind:expanding
                       bind:selectedNode={infoArtist}/>
        <ArtistGraph importArtist={searchArtist}
                     removeArtist={removeNode}
                     bind:expandedNodes
                     bind:expanding
                     bind:nodeMap
                     bind:selectedNode={infoArtist}
                     bind:activeLegendItems={activeLegendItems}
                     forceHighlight={forceHighlight}
                     selectedNodeId={infoArtist ? infoArtist.id : null}/>
    </div>

    <div id="artist-info-container" class:closed={!displayInfo}>
        <button on:click={showInfo} id="display-button">
            {#if displayInfo}
                <img src={`icons/close.svg`} height="20rem" alt="close">
            {:else}
                <img src={`icons/chevron_left.svg`} height="20rem" alt="show">
            {/if}
        </button>

        <div class="artist-info-content">
            <ArtistInfo artist={infoArtist}
                        activeLegend={activeLegendItems}
                        nodeMap={nodeMap}
                        expanding={expanding}
                        bind:barHighlight={forceHighlight}
            />
        </div>
    </div>
</div>


<style>
    :global(body) {
        margin: 0;
        /* We no longer need overflow-x here, it's better on the container */
    }

    .app-container {
        /* This is now the positioning context for the sidebar */
        position: relative;
        width: 100vw;
        height: 100vh;
        /* This prevents a scrollbar if any weirdness happens */
        overflow: hidden;
    }

    .main-content {
        /* This now takes up the full space, all the time */
        width: 100%;
        height: 100%;
        position: relative;
    }
    
    #artist-info-container {
        /* === This is the core of the new logic === */
        position: absolute;
        top: 0;
        right: 0;
        height: 100%;
        z-index: 10; /* Make sure it renders ON TOP of the main content */

        width: 510px;
        margin-top: 100px;
        background-color: #2a2a2a;
        
        /* We go back to animating transform, which is perfect for overlays */
        transform: translateX(0);
        transition: transform 0.35s ease-in-out;
    }

    /* When closed, we move it 100% of its own width to the right */
    #artist-info-container.closed {
        transform: translateX(100%);
    }

    .artist-info-content {
        padding: 1rem;
        height: 100%;
        overflow-y: auto;
    }

    #display-button {
        position: absolute;
        top: 10px;
        left: -45px;
        z-index: 10;
        border: none;
        background-color: #333;
        padding: 8px 5px;
        border-radius: 5px 0 0 5px;
        cursor: pointer;
    }
</style>