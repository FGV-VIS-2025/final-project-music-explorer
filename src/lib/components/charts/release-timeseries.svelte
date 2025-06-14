<script>
    import * as d3 from "d3";
    import { onMount } from "svelte";
    export let artistId;

    let dims = {
        width: 480,
        height: 270,
        left: 40,
        bottom: 30,
        right: 10,
        top: 20,
    }

    let svgNode = null;
    let mounted = false;

    //State variables
    let searching = false;
    let successfulSearch = false;

    let searchResults = [];

    let dateGroup;
    let dateRange = [];
    let minDate;
    let maxDate;

    function processDates(results){
        dateGroup = d3.group(results, r => {
            try {
                const date = new Date(r["first-release-date"]);
                const year = date.getFullYear()
                const quarter = String(
                    Math.floor((date.getMonth() + 1)/ 3) * 3
                ).padStart(2, "0");
                return `${year}-${quarter}`;
            } catch (error) {
                return "na";
            }
        });
        console.log(dateGroup);
        [minDate, maxDate] = d3.extent(dateGroup, d => d[0] != "NaN-NaN" ? new Date(`${d[0]}-01`) : null)
        maxDate = new Date();

        let current = new Date(`${minDate.getFullYear()-1}-12-01`);
        dateRange = [];
        // Loop enquanto o ano/mês corrente for menor ou igual ao ano/mês da data máxima
        while (current.getFullYear() < maxDate.getFullYear() ||
            (current.getFullYear() === maxDate.getFullYear() &&
            current.getMonth() <= maxDate.getMonth())){

            dateRange.push(current.toISOString().slice(0, 7));

            // Avança para o próximo mês
            current.setMonth(current.getMonth() + 3);
        }
        dateRange = [...dateRange];
        console.log(dateRange);
    }

    function getDate(date){
        if(dateGroup.get(date)){
            return dateGroup.get(date);
        } else {
            return [];
        }
    }

    async function browseReleaseGroups(id){
        if(!searching){
            searching = true;
            let link = `https://musicbrainz.org/ws/2/release-group?artist=${id}&type=album|single|ep&fmt=json`;
            let offset = 0;
            try {
                let response = await fetch(link);
                if(!response.ok){
                    throw new Error(`Erro HTTP, status ${response.status}`);
                }
                let data = await response.json();
                searchResults = data["release-groups"];
                console.log("contagem de relrease group:", data["release-group-count"])
                while (data["release-group-count"] > offset + 25){
                    offset += 25;
                    response = await fetch(`${link}&offset=${offset}`);
                    if(!response.ok){
                        throw new Error(`Erro HTTP, status ${response.status}`);
                    }
                    data = await response.json();
                    searchResults = [...searchResults, ...data["release-groups"]];
                }
                console.log(searchResults);
                processDates(searchResults);
                successfulSearch = true;
                searching = false;
            } catch (error) {
                console.error("Error while searching for artist work:", error);
                searchResults = [];
                successfulSearch = false;
                searching = false
            }
        }
    }

    let queried = true;
    onMount(() => {
        mounted = true;
    })

    $: {
        if(artistId && mounted){
            browseReleaseGroups(artistId);
        }
    }

    let xScale, yScale;
	let xScaleZoomed;
    let xAxis, yAxis;

	$: {
		if (dateGroup && minDate && maxDate) {
            const startYear = new Date(minDate);
            const maxCount = d3.max(dateRange, d => getDate(d).length) || 1;

            startYear.setFullYear(startYear.getFullYear());

            xScale = d3.scaleTime()
							.domain([startYear, maxDate])
							.range([dims.left, dims.width - dims.right]);

            yScale = d3.scaleLinear()
						.domain([0, maxCount + 1])
						.range([dims.height - dims.bottom, dims.top]);

            if (!xScaleZoomed) {
                xScaleZoomed = xScale;
            }

			d3.select(xAxis).call(d3.axisBottom(xScaleZoomed).ticks(8).tickFormat(d3.timeFormat("%Y")));
            d3.select(yAxis).call(d3.axisLeft(yScale).ticks(Math.min(maxCount, 8)).tickFormat(d3.format('d')));

			setupZoom();
        }
    }

	function setupZoom() {
        if (!svgNode) return;

        const zoom = d3.zoom()
            .scaleExtent([1, 10])
            // .translateExtent([[dims.left, 0], [dims.width - dims.right, dims.height]])
            .on('zoom', zoomed);

        d3.select(svgNode).call(zoom);
    }

	function zoomed(event) {
        xScaleZoomed = event.transform.rescaleX(xScale);
    }

</script>

{#if searching}
    <p>Carregando informações de lançamentos...</p>
{:else if !successfulSearch}
    <div>Houve um problema ao carregar as informações de lançamentos do artista.
        <button on:click={evt => browseReleaseGroups(artistId)}>Tentar novamente</button>
    </div>
{:else if searchResults && xScaleZoomed}
    <svg bind:this={svgNode} width={dims.width} height={dims.height} viewbox="0 0 {dims.width} {dims.height}">

        <g transform = "translate(0, {dims.height - dims.bottom})" bind:this={xAxis}>
        <text x={dims.width/2 + dims.left}
              y={dims.bottom - 3}
              fill="currentcolor"
              text-anchor="end">Trimestre</text>
        </g>
        <g transform = "translate({dims.left}, 0)" bind:this={yAxis}>
        <text x={-dims.left}
              y="10"
              fill="currentcolor"
              text-anchor="start">
              Quantidade de lançamentos
              </text>
        </g>
        <!-- {#if pathDefinition}
            <path
                d={pathDefinition}
                fill="none"
                stroke="steelblue"
                stroke-width="1.5"
                stroke-linejoin="round"
                stroke-linecap="round"
            />
        {/if} -->
        <g clip-path="url(#clip)">
        {#each dateRange as dateString}
            {@const count = getDate(dateString).length}
            {#if count > 0}
                {@const x = xScaleZoomed(new Date(dateString))}
                <line
                    x1={x}
                    x2={x}
                    y1={yScale(0)}
                    y2={yScale(count)}
                    stroke-width="1"
                    fill="white"
                    stroke="white"
                />
                <circle
                    cx={x}
                    cy={yScale(count)}
                    r="3"
                    fill="white"
                    stroke="white"
                />
            {/if}
        {/each}
		</g>

		<defs>
            <clipPath id="clip">
                <rect
					x={dims.left}
					y={dims.top}
					width={dims.width - dims.left - dims.right}
					height={dims.height - dims.top - dims.bottom}
				/>
            </clipPath>
        </defs>
    </svg>
    <i>Inclui relançamentos e edições especiais.</i>
{/if}

<style>
button {
    border: 2px solid white;
    border-radius: 5px;
    margin: 0.5ch;
    margin-top: 1ch;
    padding: 4px;
    font-size: 85%;
    cursor: pointer;
}
</style>
