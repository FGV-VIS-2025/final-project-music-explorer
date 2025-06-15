<script>
import * as d3 from 'd3';

// --- Variables ---
// Props
export let data = [];
export let selectedKey = null;
export let name = 'twenty one pilots';

let highlightArc;
let container;
let rect;
let tooltipPos = { x: 0, y: 0};

// Dimensions for the chart
const width = 250;
const height = 250;
const radius = Math.min(width, height) / 2 * 0.7; // Reduce radius to make space for labels

// D3 Generators
const pieGenerator = d3.pie().value(d => d[1]).sort(null);
const arcGenerator = d3.arc().innerRadius(0).outerRadius(radius);
const outerArcGenerator = d3.arc().innerRadius(radius * 0.9).outerRadius(radius * 0.9);

// D3 Color Scale
// export let colorPallete = {};
export let colorPallete = [
    "#EB743B",
    "#BA478F",
    "#669864",
    "#BEAF81",
    "#D99481",
];
let colors = {
    "cs": colorPallete[1],
    "ms": colorPallete[2],
    "im": colorPallete[3],
    "gc": colorPallete[4],
}
let labels = {
    "gc": "foi regravado",
    "cs": "fez cover",
    "im": "é membro",
    "ms": "membros"
}

// Reactive calculations
let chartData = [];

// Helper function to find the midpoint of a slice
function midAngle(d) {
    return d.startAngle + (d.endAngle - d.startAngle) / 2;
}

$: {
    let preFilterData = data
    
    // Swap 'cs' with 'gc' for mirroring the logic in the legend
    preFilterData = preFilterData.map(([k, v]) => {
        if (k === 'cs') return ['gc', v];
        if (k === 'gc') return ['cs', v];
        return [k, v];
    });

    const filteredData = preFilterData.filter(d => d[1] > 0)
    
    // Generate the raw pie filteredData for D3
    const pie = pieGenerator(filteredData);

    chartData = pie.map(d => {
        const angle = midAngle(d);
        const isRightSide = angle < Math.PI;

        // Calculate position for the label line
        const pos = outerArcGenerator.centroid(d);
        pos[0] = radius * 1.15 * (isRightSide ? 1 : -1);

        return {
            key: d.data[0], // Use the label as a key
            pathD: arcGenerator(d),
            color: colors[d.data[0]],
            // Points for the polyline connecting slice to label
            linePoints: [arcGenerator.centroid(d), outerArcGenerator.centroid(d), pos],
            labelText: d.data[0],
            // Position and anchor for the text label
            labelTransform: `translate(${pos})`,
            labelTextAnchor: isRightSide ? "start" : "end"
        };
    });
}

$: if(highlightArc){console.log("highlight arc", data.find(([k]) => k === highlightArc.key)?.[1])}
// $: console.log("highlight arc", data.find(([k]) => k[0] === highlightArc.key)?.[1])
</script>

<div class="container" bind:this={container}>
    <svg viewBox = "-{width/2} -{height/2} {width} {height}">
        <!-- Pie slices -->
        <g class="slices">
            {#each chartData as slice (slice.key)}
                <path
                    d={slice.pathD}
                    fill={slice.color}
                    class:selected={selectedKey === slice.key}
                    on:click={() => selectedKey = selectedKey === slice.key ? null : slice.key}
                    on:mouseenter={(event,d) => {
                        highlightArc = slice
                        rect = container.getBoundingClientRect()
                        tooltipPos = {
                            x: event.pageX - rect.left,
                            y: event.pageY - rect.top
                        }
                    }}
                    on:mouseleave={(event, d) => {highlightArc = null}}
                />
            {/each}
        </g>

        <!-- Lines connecting slices to labels -->
        <g class="lines">
            {#each chartData as slice (slice.key)}
                 <polyline
                    points={slice.linePoints}
                    class:selected={selectedKey === slice.key}
                 />
            {/each}
        </g>

        <!-- Text labels -->
        <g class="labels">
            {#each chartData as slice (slice.key)}
                <text
                    transform={slice.labelTransform}
                    text-anchor={slice.labelTextAnchor}
                    dy="0.35em"
                    class:selected={selectedKey === slice.key}
                >
                    {labels[slice.labelText]}
                </text>
            {/each}
        </g>
        
    </svg>
    <div class="tooltip">
        {#if highlightArc != null}
            <div style="position: absolute; top: {tooltipPos.y}px; left: {tooltipPos.x}px; transform: translate(15px, -15px);">
                {#if highlightArc.key == "im"}
                    {name} é/já foi membro de<strong>{data.find(([k]) => k === highlightArc.key)?.[1]}</strong> grupos.
                {:else if highlightArc.key == "ms"}
                    <strong>{data.find(([k]) => k === highlightArc.key)?.[1]}</strong> artistas já foram/são membros de {name}.
                {:else if highlightArc.key == "cs"}
                    {name} fez covers de <strong>{data.find(([k]) => k === highlightArc.key)?.[1]}</strong> artistas diferentes.
                {:else if highlightArc.key == "gc"}
                    <strong>{data.find(([k]) => k === highlightArc.key)?.[1]}</strong> artistas regravaram músicas de {name}.
                {/if}
            </div>
        {/if}
    </div>
</div>

<style>
    svg {
        max-width: 15em;
        margin-block: 2em;
        /* Do not clip shapes outside the viewBox */
        overflow: visible;
        width: 100%;
        margin: auto;

        overflow: visible;
    }

    .container {
        position: relative;
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        font-family: sans-serif;
    }

    /* --- Path/Slice Styles --- */
    path {
        transition: opacity 300ms ease-in-out;
        cursor: pointer;
        stroke: white;
        stroke-width: 1px;
    }

    path:hover {
        opacity: 1 !important;
    }

    /* When a slice is hovered, fade out the others */
    g.slices:has(path:hover) path:not(:hover) {
        opacity: 0.4;
    }

    /* When a slice is selected, fade out unselected slices, lines, and labels */
    .container:has(.selected) .slices path:not(.selected) {
        opacity: 0.3;
    }
    .container:has(.selected) .lines polyline:not(.selected) {
        opacity: 0.2;
    }
    .container:has(.selected) .labels text:not(.selected) {
        opacity: 0.4;
    }


    /* --- Polyline Styles --- */
    polyline {
        fill: none;
        stroke: #f0f0f0;
        stroke-width: 1px;
        opacity: 0.5;
        transition: opacity 300ms ease-in-out;
    }


    /* --- Text Label Styles --- */
    text {
        font-size: 1rem;
        fill: #fff;
        transition: opacity 300ms ease-in-out;
    }

    /* --- Selected State --- */
    .selected {
        font-weight: bold;
    }

    .tooltip div {
        max-width: 20ch;

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
</style>