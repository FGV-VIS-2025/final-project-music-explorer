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

        let current = new Date(minDate.toISOString());
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

    onMount(() => {
        if(artistId){
            browseReleaseGroups(artistId).then(() => {
                mounted = true;
            })
        } else {
            mounted = true;
        }
    })

    $: {
        if(artistId && mounted){
            browseReleaseGroups(artistId);
        }
    }

    let xScale, yScale;
    let xAxis, yAxis;
    $: {
        if(dateGroup && minDate && maxDate){
            xScale = d3.scaleTime().domain([minDate, maxDate]).range([dims.left, dims.width - dims.right]);
            yScale = d3.scaleLinear().domain(d3.extent(dateRange, d => getDate(d).length)).range([dims.height - dims.bottom, dims.top]);
            d3.select(xAxis).call(d3.axisBottom(xScale).ticks(8).tickFormat(d3.timeFormat("%Y")));
            d3.select(yAxis).call(d3.axisLeft(yScale));
        }
    }

    let lineGenerator, pathDefinition;
    $: lineGenerator = d3.line()
    .x(d => xScale(new Date(`${d}-01`)))
    .y(d => yScale(getDate(d).length));

    $: pathDefinition = (dateGroup && dateRange.length > 0 && lineGenerator) ? lineGenerator(dateRange) : "";

</script>

{#if searching}
    <p>Carregando informações de lançamentos...</p>
{:else if !successfulSearch}
    <p>Houve um problema ao carregar as informações de lançamentos do artista.</p>
{:else if searchResults}
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
        {#if pathDefinition}
            <path
                d={pathDefinition}
                fill="none"
                stroke="steelblue"
                stroke-width="1.5"
                stroke-linejoin="round"
                stroke-linecap="round"
            />
        {/if}
    </svg>
{/if}
