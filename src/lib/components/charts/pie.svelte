<script>
import * as d3 from 'd3';
import { tweened } from 'svelte/motion';
import { cubicOut } from 'svelte/easing';

// --- Variables ---
// Props
export let data = [];
export let selectedKey = null;

// Dimensions for the chart
const width = 250;
const height = 180;
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

// Reactive calculations
let chartData = [];

/**
 * Disable all console logs except those inside this file's scope.
 * This overrides the global console.log, but allows logs from this file.
 */
const originalConsoleLog = console.log;
console.log = function (...args) {
    // Only log if the call stack includes this file's path
    if (new Error().stack.includes('pie.svelte')) {
        originalConsoleLog.apply(console, args);
    }
};

$: console.log("data", data)
// $: console.log("chartData", chartData)

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
    const filteredData = data.filter(d => d[1] > 0)
    
    // // When the `data` prop changes, filter it and update the color domain
    // colors.domain(filteredData.map(d => d[0]));

    // Generate the raw pie filteredData for D3
    const pie = pieGenerator(filteredData);

    // Instead of directly setting chartData, we update the tweened store.
    // Svelte will interpolate from the old `pie` state to the new one.
    $tweenedData = pie;
}

$: {
    // Reactive block that runs on every "frame" of the tween for smooth 
    // transition
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
}
</script>

<div class="container">
    <svg viewBox = "-{width/2} -{height/2} {width} {height}">
        <!-- Pie slices -->
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
                    {slice.labelText}
                </text>
            {/each}
        </g>
        
        <!-- {#each arcs as arc, index}
            <path d={arc} fill={colors(index)}
            class:selected={selectedIndex === index}
            on:click={e => selectedIndex = selectedIndex === index ? -1 : index} />
        {/each} -->
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

        overflow: visible;
    }

    .container {
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
        font-size: 0.7rem;
        fill: #fff;
        transition: opacity 300ms ease-in-out;
    }

    /* --- Selected State --- */
    .selected {
        font-weight: bold;
    }

    /* svg:has(path:hover) path:not(:hover) {
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

    path:hover {
        opacity: 100% !important;
    } */
</style>