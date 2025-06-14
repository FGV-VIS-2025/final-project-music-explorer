<script>
	import * as d3 from 'd3';

	export let data = {};
	export let barHeight = 25;
	export let selectedMusic;

    let dims = {
        width: 480,
        left: 30,
        bottom: 30,
        right: 10,
        top: 20,
    }

	let selectedIndex = -1;
	let hoveredIndex = -1;

	const MIN_LABEL_WIDTH = 200 + dims.left; //very high value since musics can have large names (a.k.a "frances farmer will have her revenge on seattle" by nirvana)

	let xScale;
	let flatData = [];
	$: {
		flatData = [];
		for(let key of Object.keys(data)){
			flatData.push([key, data[key].length]);
		}
		flatData.sort((d1, d2) => d1[1] < d2[1]);
		xScale = d3.scaleLinear()
			.domain([0, d3.max(flatData, d => d[1]) || 1])
			.range([0, dims.width - dims.left]);
	}
	$: selectedMusic = selectedIndex != -1 ? flatData[selectedIndex][0] : null

</script>

<svg viewBox="0 0 {dims.width} {barHeight * flatData.length}">
	{#each flatData as d, i}
		<rect
			class:selected={selectedIndex === i}
			class:hovered={hoveredIndex === i}
			x={dims.left}
			y={i * barHeight}
			width={xScale(d[1])}
			height={barHeight - 5}
			fill="white"
			on:click={() => selectedIndex = (selectedIndex === i ? -1 : i)}
			on:mouseenter={() => hoveredIndex = i}
			on:mouseleave={() => hoveredIndex = -1}
		/>
		<text
			class="label"
			x={(xScale(d[1]) > MIN_LABEL_WIDTH ? (xScale(d[1]) - 5) : (xScale(d[1]) + 5)) + dims.left}
			y={i * barHeight + ((barHeight) / 2)}
			font-weight={xScale(d[1]) > MIN_LABEL_WIDTH ? "bold" : null}
			text-anchor={xScale(d[1]) > MIN_LABEL_WIDTH ? "end" : "start"}
			fill={xScale(d[1]) > MIN_LABEL_WIDTH ? "black" : "white"}
		>
			{d[0]}: {d[1]}
		</text>
		<text
			class="rank"
			x={dims.left - 5}
			y={i * barHeight + ((barHeight) / 2)}
			fill="white"
			text-anchor="end"
		>
			{i}ª
		</text>
	{/each}
</svg>


<style>
	rect {
		transition: all 300ms ease;
		cursor: pointer;
	}

	rect.hovered {
		opacity: 1;
		stroke-width: 2;
	}

	svg:has(rect.hovered) rect:not(.hovered) {
		opacity: 0.3;
	}

	rect.selected {
		stroke-width: 2;
	}

	/* Dim others when selected */
	svg:has(rect.selected) rect:not(.selected) {
		opacity: 0.3;
	}

	/* Combined hover + select */
	rect.selected.hovered {
		/*stroke: black;*/
		stroke-width: 3;
		opacity: 1 !important;
	}

	.label {
		font-size: 0.75em;
		pointer-events: none;
		dominant-baseline: middle;
	}

	.rank {
		font-size: 0.9em;
	}

</style>
