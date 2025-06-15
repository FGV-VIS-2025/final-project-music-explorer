<script>
    import ArtistGraph from "$lib/components/graphs/artist-graph.svelte";
    import SearchArtist from "$lib/components/selectors/get-artist.svelte";
    import ExpandedStack from "$lib/components/selectors/expanded-stack.svelte";
    import ArtistInfo from "$lib/components/artist-info.svelte";
    import { image } from "d3";

    //Search variables
    let searchArtist;

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
</script>

<!-- <h1>Music explorer</h1> -->

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

<button on:click={showInfo} id="display-button" style="border: none;">
    {#if displayInfo}
        <img src={`icons/close.svg`} height="20rem" alt="close">
    {:else}
        <img src={`icons/chevron_left.svg`} height="20rem" alt="show">
    {/if}
</button>
             
<div id="artist-info" style="display: {infoDisplay};">
    <ArtistInfo artist={infoArtist}
                activeLegend={activeLegendItems}
                nodeMap={nodeMap}
                expanding={expanding}
                bind:barHighlight={forceHighlight}
    />
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
	#chart-selector {
		position: fixed;
		top : 120px;
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

	#chart-selector input[type="radio"]:checked+label {
		background-color: yellow;
	}
	
    #display-button {
        position: fixed;
        top: 130px;
        right: 45px;
        z-index: 1000;
		cursor: pointer;
		display: flex;
    }
    
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
        width: 500px;
        box-sizing: border-box;

        overflow-y: scroll;
        overflow-x: hidden;
    }
</style>
