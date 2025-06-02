<script>
    import * as d3 from "d3";
    import ReleaseTimeseries from "$lib/components/charts/release-timeseries.svelte";
    //input of the component - artist to display info
    export let artistId;

    let searching = false;
	let successfulRequest = false;
	let successfulSearch = false;

	let svgNode;
	let width = 630;
	let height = 360;

	// To manage visibility of search results
	let searchResult = [];
    function lookupArtist(id) {
		if(id){
            searching = true;
            let link = `https://musicbrainz.org/ws/2/artist/${id}?fmt=json&inc=works`;
            fetch(link)
                .then((response) => response.json())
                .then((data) => {
                    successfulRequest = true;
                    successfulSearch = true;
                    searching = false;
                    console.log(data);
                    searchResult = data;
                })
                .catch((error) => {
                    console.error("Error while searching for artist info:", error);
                    successfulRequest = false;
                    successfulSearch = false;
                    searchResult = null;
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

</script>

<h>{artistId}</h>
<ReleaseTimeseries bind:artistId={artistId}/>
