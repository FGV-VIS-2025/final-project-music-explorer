<script>
    import ArtistGraph from "$lib/components/graphs/artist-graph.svelte";
    import SearchArtist from "$lib/components/selectors/get-artist.svelte";

    let searchInput;
    let artistId;
</script>

<h1>Music explorer</h1>

<SearchArtist bind:artistId={artistId}/>
<ArtistGraph importArtist={artistId}/>
