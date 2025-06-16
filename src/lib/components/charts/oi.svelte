<script>
import * as d3 from 'd3';
import { tweened } from 'svelte/motion';
import { cubicOut } from 'svelte/easing';

// Props
export let data = [];
export let selectedKey = null;

// Dimensions for the chart
const width = 250;
const height = 180;
const radius = Math.min(width, height) / 2 * 0.7; // Reduce radius to make space for labels

// D3 Generators
const pieGenerator = d3.pie().value(d => d[1]).sort(null);
const arcGenerator = d3.arc().innerRadius(radius * 0.3).outerRadius(radius);
const outerArcGenerator = d3.arc().innerRadius(radius * 0.9).outerRadius(radius * 0.9);

// D3 Color Scale
const colors = d3.scaleOrdinal()
    .range(["#BEAF81", "#669864", "#D99481", "#BA478F", "#827E9C", "#5E8C8A"]);

// Reactive calculations
let chartData = [];

// Helper function to find the midpoint of a slice
function midAngle(d) {
    return d.startAngle + (d.endAngle - d.startAngle) / 2;
}

// Svelte's tweened store for smooth transitions
// We tween the entire dataset that drives the chart.
const tweenedData = tweened(undefined, {
    duration: 750,
    easing: cubicOut
});

$: {
    // When the `data` prop changes, update the color domain
    colors.domain(data.map(d => d[0]));

    // Generate the raw pie data for D3
    const pie = pieGenerator(data);

    // Instead of directly setting chartData, we update the tweened store.
    // Svelte will interpolate from the old `pie` state to the new one.
    $tweenedData = pie;
}

$: {
    // This reactive block will now run on every "frame" of the tween
    if ($tweenedData) {
        chartData = $tweenedData.map(d => {
            const angle = midAngle(d);
            const isRightSide = angle < Math.PI;

            // Calculate position for the label line
            const pos = outerArcGenerator.centroid(d);
            pos[0] = radius * 1.15 * (isRightSide ? 1 : -1);

            return {
                key: d.data[0], // Use the label as a key
                pathD: arcGenerator(d),
                color: colors(d.data[0]),
                // Points for the polyline connecting slice to label
                linePoints: [arcGenerator.centroid(d), outerArcGenerator.centroid(d), pos],
                labelText: d.data[0],
                // Position and anchor for the text label
                labelTransform: `translate(${pos})`,
                labelTextAnchor: isRightSide ? "start" : "end"
            };
        });
    }
}

</script>

<div class="container">
    <svg viewBox="-{width/2} -{height/2} {width} {height}">
        <!-- Group for the pie slices -->
        <g class="slices">
            {#each chartData as slice (slice.key)}
                <path
                    d={slice.pathD}
                    fill={slice.color}
                    class:selected={selectedKey === slice.key}
                    on:click={() => selectedKey = selectedKey === slice.key ? null : slice.key}
                />
            {/each}
        </g>

        <!-- Group for the lines connecting slices to labels -->
        <g class="lines">
            {#each chartData as slice (slice.key)}
                 <polyline
                    points={slice.linePoints}
                    class:selected={selectedKey === slice.key}
                 />
            {/each}
        </g>

        <!-- Group for the text labels -->
        <g class="labels">
            {#each chartData as slice (slice.key)}
                <text
                    transform={slice.labelTransform}
                    text-anchor={slice.labelTextAnchor}
                    dy="0.35em"
                    class:selected={selectedKey === slice.key}
                >
                    {slice.labelText}
                </text>
            {/each}
        </g>
    </svg>
</div>

<style>
    .container {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        font-family: sans-serif;
    }

    svg {
        max-width: 100%;
        width: 400px;
        overflow: visible; /* Important to see labels outside the main radius */
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
        stroke: #444;
        stroke-width: 1px;
        opacity: 0.5;
        transition: opacity 300ms ease-in-out;
    }


    /* --- Text Label Styles --- */
    text {
        font-size: 0.7rem;
        fill: #333;
        transition: opacity 300ms ease-in-out;
    }

    /* --- Selected State --- */
    .selected {
        font-weight: bold;
    }

</style>
