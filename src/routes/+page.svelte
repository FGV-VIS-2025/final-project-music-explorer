<script>
    import ArtistGraph from "$lib/components/graphs/artist-graph.svelte";
    import SearchArtist from "$lib/components/selectors/get-artist.svelte";
    import ExpandedStack from "$lib/components/selectors/expanded-stack.svelte";

    let searchInput;
    let artistId;
    let expandedNodes = [];
    let removeNode;
    let expanding = false;

    $: console.log(removeNode);
</script>

<!-- <h1>Music explorer</h1> -->

<SearchArtist bind:artistId={artistId}/>
<ExpandedStack bind:expandedNodes bind:removeNode bind:expanding/>
<ArtistGraph importArtist={artistId} removeArtist={removeNode} bind:expandedNodes bind:expanding/>
