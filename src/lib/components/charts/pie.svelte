<script>
import * as d3 from 'd3';

let arcGenerator = d3.arc().innerRadius(0).outerRadius(50);

export let data = [];
let colors = d3.scaleOrdinal()
            .domain([0, 1, 2, 3])
            .range(["#BEAF81", "#669864", "#D99481", "#BA478F"]);
let sliceGenerator = d3.pie().value(d => d[1]);
let arcData;
let arcs;

    $: {
        // Reactively calculate arcData and arcs the same way we did before with sliceGenerator and arcGenerator
        arcData = sliceGenerator(data);
        arcs = arcData.map(d => arcGenerator(d));
    }
export let selectedIndex = -1
</script>

<div class="container">
<svg viewBox = "-50 -50 100 100">
    {#each arcs as arc, index}
        <path d={arc} fill={colors(index)}
          class:selected={selectedIndex === index}
          on:click={e => selectedIndex = selectedIndex === index ? -1 : index} />
    {/each}
</svg>

</div>

<style>
svg {
	max-width: 15em;
	margin-block: 2em;

    /* Do not clip shapes outside the viewBox */
    overflow: visible;
    width: 50%;
    margin: auto;
}

svg:has(path:hover) path:not(:hover) {
	opacity: 50%;
}

path {
	transition: 300ms;
	cursor: pointer;
}

.container{
    display: flex;
    align-items: center;
    gap: 0.6em;
}

.legend{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(8em, 1fr));
    border: 1px solid black;
    padding: 1em;
    margin: 1em;
    flex: 1;
}

.legend li{
    display:flex;
    align-items: center;
    gap: 0.6em;
}

.swatch{
    display: inline-block;
    background-color: var(--color);
    width: 1em;
    height: 1em;
}

/* When a path is selected, make all non-selected paths 50% opacity */
svg:has(.selected) path:not(.selected) {
   opacity: 50%;
}

.selected {
	--color: oklch(60% 45% 0) !important;

	&:is(path) {
		fill: var(--color) !important;
	}

	&:is(li) {
		color: var(--color);
	}
}

ul:has(.selected) li:not(.selected) {
	color: gray;
}

path:hover {
	opacity: 100% !important;
}




</style>


