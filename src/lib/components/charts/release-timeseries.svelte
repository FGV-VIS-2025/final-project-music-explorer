<script>
    import * as d3 from "d3";
    import { onMount } from "svelte";
    import { computePosition, autoPlacement, offset, } from '@floating-ui/dom';

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
                const year = date.getUTCFullYear()
                // const quarter = String(
                //     Math.floor((date.getMonth() + 1)/ 3) * 3
                // ).padStart(2, "0");
                // return `${year}-${quarter}`;
                return `${year}`
            } catch (error) {
                return "na";
            }
        });
        console.log(dateGroup);
        [minDate, maxDate] = d3.extent(dateGroup, d => d[0] != "NaN-NaN" ? new Date(`${d[0]}-01-01`) : null)
        maxDate = new Date();

        // let current = new Date(`${minDate.getFullYear()-1}-12-01`);
        // dateRange = [];
        // // Loop enquanto o ano/mês corrente for menor ou igual ao ano/mês da data máxima
        // while (current.getFullYear() < maxDate.getFullYear() ||
        //     (current.getFullYear() === maxDate.getFullYear() &&
        //     current.getMonth() <= maxDate.getMonth())){
        //
        //     dateRange.push(current.toISOString().slice(0, 7));
        //
        //     // Avança para o próximo mês
        //     current.setMonth(current.getMonth() + 6);
        // }
        // dateRange = [...dateRange];
        // console.log(dateRange);
        let current = minDate.getUTCFullYear() - 2;
        while (current <= maxDate.getUTCFullYear()){
            dateRange.push(`${current}`);
            current += 1;
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

    function getVisibleMaxCount(xScaleZoomed) {
        if (!dateRange || !dateGroup) return 1;
        
        const [domainStart, domainEnd] = xScaleZoomed.domain();
        
        const visibleData = dateRange.filter(dateString => {
            const date = new Date(dateString);
            return date >= domainStart && date <= domainEnd;
        });
        
        const maxCount = d3.max(visibleData, d => getDate(d).length) || 1;
        return Math.max(maxCount, 1);
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
    let highZoom = false;
	$: {
		if (dateGroup && minDate && maxDate) {
            const startYear = new Date(minDate);
            const maxCount = (d3.max(dateRange, d => getDate(d).length) + 1 )|| 1;

            startYear.setFullYear(startYear.getFullYear() - 1);

            xScale = d3.scaleTime()
							.domain([startYear, maxDate])
							.range([dims.left, dims.width - dims.right]);

            yScale = d3.scaleLinear()
						.domain([0, maxCount + 1])
						.range([dims.height - dims.bottom, dims.top]);

            if (!xScaleZoomed) {
                xScaleZoomed = xScale;
            }

			d3.select(xAxis).call(d3.axisBottom(xScaleZoomed).ticks(highZoom ? 4 : 8).tickFormat(d3.timeFormat("%Y")));
            d3.select(yAxis).call(d3.axisLeft(yScale).ticks(Math.min(maxCount, 8)).tickFormat(d3.format('d')));

			setupZoom();
        }
    }

	function setupZoom() {
        if (!svgNode) return;

        const zoom = d3.zoom()
            .scaleExtent([1, 10])
            .on('zoom', zoomed);

        d3.select(svgNode).call(zoom);
    }

	function zoomed(event) {
		xScaleZoomed = event.transform.rescaleX(xScale);
		const visibleMaxCount = getVisibleMaxCount(xScaleZoomed);

		// Atualizar a escala Y global
		yScale = d3.scaleLinear()
			.domain([0, visibleMaxCount + 1])
			.range([dims.height - dims.bottom, dims.top]);

		d3.select(yAxis)
			.transition()
			.duration(300)
			.ease(d3.easeQuadOut)
			.call(d3.axisLeft(yScale).ticks(Math.min(visibleMaxCount + 1, 8)).tickFormat(d3.format('d')));

        const svg = d3.select(svgNode);
        
        svg.selectAll('.chart-line')
            .transition()
            .duration(300)
            .ease(d3.easeQuadOut)
            .attr('y1', yScale(0))
            .attr('y2', function() {
                const dateString = d3.select(this).attr('data-date-string');
                const count = getDate(dateString).length;
                return yScale(count);
            });
        
        svg.selectAll('.chart-circle')
            .transition()
            .duration(300)
            .ease(d3.easeQuadOut)
            .attr('cy', function() {
                const dateString = d3.select(this).attr('data-date-string');
                const count = getDate(dateString).length;
                return yScale(count);
			});

        const [startDate, endDate] = xScaleZoomed.domain();
        const visibleDuration = endDate.getTime() - startDate.getTime();
        const ONE_YEAR_IN_MS = 365 * 24 * 60 * 60 * 1000;
        const THREE_MONTHS_IN_MS = ONE_YEAR_IN_MS / 4;
        if(visibleDuration < ONE_YEAR_IN_MS * 3.3) {
            highZoom = true;
        } else {
            highZoom = false;
        }
	}

    let highlightPoint;
    let container;
    let rect
    let tooltipPos = { x: 0, y: 0 };
    let tooltip;
    async function dotInteraction (index, evt) {
        let hoveredElement = evt.target;
        if (evt.type === "mouseenter") {
            highlightPoint = index;
            //cursor = {x: evt.x, y: evt.y};
            tooltipPos = await computePosition(hoveredElement, tooltip, {
                strategy: "absolute", // because we use position: fixed
                middleware: [
                    offset(5), // spacing from tooltip to dot
                    autoPlacement() // see https://floating-ui.com/docs/autoplacement
                ],
            });        }
        else if (evt.type === "mouseleave") {
            highlightPoint = null
        }
    }


</script>

<div class="container" bind:this={container}>
    {#if searching}
        <p class = "loading">🛈 Carregando informações de lançamentos...</p>
    {:else if !successfulSearch}
        <div class = "error">Houve um problema ao carregar as informações de lançamentos do artista.
            <button on:click={evt => browseReleaseGroups(artistId)}>Tentar novamente</button>
        </div>
    {:else if searchResults && xScaleZoomed}
        <svg bind:this={svgNode} width={dims.width} height={dims.height} viewbox="0 0 {dims.width} {dims.height}">
            <g transform = "translate(0, {dims.height - dims.bottom})" bind:this={xAxis}>
            <text x={dims.width/2 + dims.left}
                y={dims.bottom - 3}
                fill="currentcolor"
                text-anchor="end">Ano</text>
            </g>
            <g transform = "translate({dims.left}, 0)" bind:this={yAxis}>
            <text x={-dims.left}
                y="10"
                fill="currentcolor"
                text-anchor="start">
                Quantidade de lançamentos
                </text>
            </g>

            <g clip-path="url(#clip)">
            {#each dateRange as dateString, index}
                {@const count = getDate(dateString).length}
                {#if count > 0}
                    {@const x = xScaleZoomed(new Date(dateString))}
                    <line
                        class="chart-line"
                        data-date-string={dateString}
                        x1={x}
                        x2={x}
                        y1={yScale(0)}
                        y2={yScale(count)}
                        stroke-width="1"
                        fill="white"
                        stroke="white"
                    />
                    <circle
                        class="chart-circle"
                        data-date-string={dateString}
                        cx={x}
                        cy={yScale(count)}
                        r="3"
                        fill="white"
                        stroke="white"
                        on:mouseenter={(event, d) => dotInteraction(index, event)}
                        on:mouseleave={(event, d) => dotInteraction(index, event)}
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
        <i style="font-size: 90%;">
            Inclui relançamentos e edições especiais. Experimente usar o scroll
            do mouse, arrastar e passar o mouse em pontos específicos.
        </i>

        <div class="tooltip"
             class:hidden={highlightPoint == null}
             bind:this={tooltip}
             style="top:{tooltipPos.y}px; left:{tooltipPos.x}px ">
        {#if highlightPoint != null}
            {getDate(dateRange[highlightPoint]).length} lançamentos
            {#each getDate(dateRange[highlightPoint]).slice(0, 5) as release}
                <br>
                <strong>{release["primary-type"]}</strong> - {release.title} <span class="date">- {release["first-release-date"]}</span>
            {/each}
            {#if getDate(dateRange[highlightPoint]).length > 5}
                <br>Entre outros...
            {/if}
        {/if}
    </div>
    {/if}
</div>

<style>
    .container{
        position: relative;
        align-items: center;
        gap: 0.6em;
    }

    .hidden {
        display: none !important;
    }

    .tooltip {
        position: absolute;
        max-width: 40ch;

        font-size: 80%;
        color: white;

        background-color: #393939e0;
		box-shadow: 1px 1px 2px 2px #60606050;

        padding: 5px;
        border: 1px solid #ccc;
        border-radius: 5px;

        z-index: 1000;

        transition-duration: 300ms;
        transition-property: opacity, visibility;
        &[hidden]:not(:hover, :focus-within) {
            opacity: 0;
            visibility: hidden;
        }
    }

    .tooltip div,
    .tooltip strong{
        fill: white;
        color: white;
    }

    .date {
        color: #d0caca
    }

    button {
        border: 2px solid white;
        border-radius: 5px;
        margin: 0.5ch;
        margin-top: 1ch;
        padding: 4px;
        font-size: 90%;
        cursor: pointer;
        background-color: #ffffff3c
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
        font-size: 100%;
        margin: auto;
    }
</style>
