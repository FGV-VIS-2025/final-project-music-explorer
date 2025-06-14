<script>
    import * as d3 from 'd3';
    export let data = [];
    export let name;

    let arcGenerator = d3.arc().innerRadius(0).outerRadius(50);
    let colors = d3.scaleOrdinal()
                .domain([0, 1, 2, 3])
                .range(["#BEAF81", "#669864", "#D99481", "#BA478F"]);
    let sliceGenerator = d3.pie().value(d => d[1]);
    let arcData;
    let arcs;
    let highlightArc;
    $: {
        arcData = sliceGenerator(data);
        arcs = arcData.map(d => arcGenerator(d));
    }

    let container;
    let rect
    let tooltipPos = { x: 0, y: 0 };
    $: console.log(highlightArc, tooltipPos);
    $: {
        if(container){
        }
    }
</script>

<div class="container" bind:this={container}>
    <svg viewBox = "-50 -50 100 100">
        {#each arcs as arc, index}
            <path d={arc}
                fill={colors(index)}
                on:mouseenter={(event, d) => {
                    highlightArc = index;
                    rect = container.getBoundingClientRect();
                    tooltipPos = { x: event.pageX - rect.left,
                                    y: event.pageY - rect.top };
                }}
                on:mouseleave={(event, d) => {highlightArc = null;}}
            />
        {/each}
    </svg>

    <div class="tooltip">
        {#if highlightArc != null}
            <div style="position: absolute; top: {tooltipPos.y}px; left: {tooltipPos.x}px; transform: translate(15px, -15px);">
                {#if data[highlightArc][0] == "im"}
                    {name} é/já foi membro de <strong>{data[highlightArc][1]}</strong> grupos.
                {:else if data[highlightArc][0] == "ms"}
                    <strong>{data[highlightArc][1]}</strong> artistas já foram/são membros de {name}.
                {:else if data[highlightArc][0] == "cs"}
                    {name} fez covers de <strong>{data[highlightArc][1]}</strong> artistas diferentes.
                {:else if data[highlightArc][0] == "gc"}
                    <strong>{data[highlightArc][1]}</strong> artistas regravaram músicas de {name}.
                {/if}
            </div>
        {/if}
    </div>

</div>

<style>
    svg {
        max-width: 15em;
        margin-block: 2em;

        overflow: visible;
        width: 50%;
        margin: auto;
    }

    svg:has(path:hover) path:not(:hover) {
        opacity: 50%;
    }

    .container{
        position: relative;
        display: flex;
        align-items: center;
        gap: 0.6em;
    }

    path:hover {
        opacity: 100% !important;
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


