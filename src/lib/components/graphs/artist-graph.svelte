<script>
    import * as d3 from "d3";

    import { onMount } from "svelte";

    export let width = 1280;
    export let height = 720;
    export let importArtist = null; //Input of the component, it will receive an id, focus on it and them set it to null
    let svgNode;

    let searchInput = "";
    $: console.log(searchInput);

    let cache = {}; //Where to hold raw data fetched by file
    let nodes = []; //Where node objects are saved
    let edges = []; //Where the edges are saved
    let nodeMap = new Map(); //Map to easen getting a node object by its id

    let relations = ["ms", "im", "cs"]; //Type of relations between nodes
    let relationColors = {
        "ms": "#d200d2",
        "im": "#909090",
        "cs": "#2a17f9",
        "gc": "#fbff06"
    }
    // let relations = ["cs"]; //Type of relations between nodes
    $: console.log(nodes);
    $: console.log(edges);
    $: console.log(relations);

    //Gets a id and add a node object to the nodes array
    async function addNode(id){
        let letter = id.slice(0, 2);
        if(!(letter in cache)) {
            console.log(`Pedindo dados de grafo para a letra ${letter}`);
            try {
                const response = await fetch(`graph/${letter}.json`);
                if (!response.ok){
                    throw new Error(`Não foi possível solicitar os dados de grafo para a letra ${letter}`)
                }
                const graphData = await response.json();
                cache[letter] = graphData;
            } catch (error) {
                console.error("Erro ao popular cache:", error);
                return;
            }
            console.log("Dados obtidos corretamente");
        }
        let node = { id: id, n: cache[letter][id].n, expanded: false};
        nodeMap.set(id, node);
        nodes.push(node);
    }

    //Add edges of an node to other nodes in the graph. Adds the other nodes if necessary
    async function addNodeRelations(id){
        if(simulation){
            simulation.stop().alpha(0);
        }
        let letter = id.slice(0, 2);
        //I assume the cache exists since this function will not be called if the node isnt in the graph in the first place
        const nodeInfo = cache[letter][id];
        for(let relation of relations){
            if(Array.isArray(nodeInfo[relation])){
                for(let endId of nodeInfo[relation]){
                    if (!nodeMap.has(endId)){
                        await addNode(endId);
                    }
                    edges.push({
                        source: nodeMap.get(id),
                        target: nodeMap.get(endId),
                        type: relation,
                    });
                    updateGraph(null);
                }
            } else {
                for (const [endId, musics] of Object.entries(nodeInfo[relation])){
                    if (!nodeMap.has(endId)){
                        await addNode(endId);
                    }
                    edges.push({
                        source: nodeMap.get(id),
                        target: nodeMap.get(endId),
                        type: relation,
                    });
                    updateGraph(null);
                }
            }
        }
        nodeMap.get(id).expanded = true;
        edges = [...edges];
        console.log(`Adicionei arestas de ${id}`);
    }

    //Handle external sent artist focusing event
    let expanding = false;
    $: console.log("expandindo: ", expanding);
    $: {
        if(importArtist && !expanding){
            expanding = true;
            if (!nodeMap.has(importArtist)){
                addNode(importArtist).then(() => {
                    addNodeRelations(importArtist).then(() => {
                        console.log("adicionei e expandi artista", importArtist);
                        updateGraph(importArtist);
                        importArtist = null;
                        expanding = false;
                    });
                });
            } else if (!nodeMap.get(importArtist).expanded){
                addNodeRelations(importArtist).then(() => {
                    console.log("expandi artista ", importArtist);
                    updateGraph(importArtist);
                    importArtist = null;
                    expanding = false;
                });
            } else {
                console.log("artista já estava expandido");
                importArtist = null;
                expanding = false;
            }
        }
    }

    //Handle artist click event
    function nodeClick(event, node){
        if(!expanding){
            expanding = true;
            if (node.expanded){
                console.log("nó já estava expandido");
                expanding = false;
            } else {
                addNodeRelations(node.id).then(() => {
                    updateGraph(node.id);
                    expanding = false;
                });
            }
        }
    }

    //Functions to handle node dragging
    function nodeDrag(graphSim) {
        function dragstarted(event, d) {
            if (!event.active) graphSim.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }

        function dragended(event, d) {
            if (!event.active) graphSim.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
        return d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended);
    }

    //It is necessary to manage the svg and graph with d3 because of the animation and
    //update of things. Doing it with svelte is inneficient since we would need to reasign
    //the graph arrays everytime... An operation that can be expensive :( (yeah I would
    //love to handle this with svelte but the life is a cold and indifferent place)

    //Variables to save D3 components
    let simulation;
    let svgEdges;
    let svgNodes;
    //Variables to aid zooming
    let zoomBehavior;
    let tickCount = 0;
    let alreadyZoomed = false;
    let focusNode; //It is set based on the input to the function and set to null when the focus was applied

    let highlightNode; //Variable to hold a node that is highlighted (mouse hover)
    function updateGraph(focusId) {
        const svg = d3.select(svgNode);
        const zoomGroup = d3.select("#zoom-group");
        let ref = d3.select("#ref");
        if (!simulation) {
            //Create simulation and initial classes if they didnt exist before
            simulation = d3.forceSimulation(nodes)
                .force("link", d3.forceLink(edges).id((d) => d.id).distance(100))
                .force("charge", d3.forceManyBody().strength(-300))
                .force("center", d3.forceCenter(0, 0));

            svgEdges = zoomGroup.append("g").attr("stroke", "#999").attr("stroke-opacity", 0.6);
            svgNodes = zoomGroup.append("g").attr("stroke", "#fff").attr("stroke-width", 1.5);

            simulation.on("end", () => {
                //After the animation, reset variables and focus
                tickCount = 0;
                alreadyZoomed = false;
                focusNode = null;
                console.log("Animation ended");
            })

            simulation.on("tick", () => {
                svgEdges.selectAll("line")
                    .attr("x1", (d) => d.source.x)
                    .attr("y1", (d) => d.source.y)
                    .attr("x2", (d) => d.target.x)
                    .attr("y2", (d) => d.target.y);
                svgNodes.selectAll("g")
                    .attr("transform", (d) => `translate(${d.x},${d.y})`);

                //If this animation should have focus, then focus after some ticks to get a stable focusing
                tickCount++;
                console.log(tickCount);
                if(tickCount > 60 && !alreadyZoomed && focusNode){
                    console.log("zooming");
                    alreadyZoomed = true;
                    const translateX = (width / 2) - (focusNode.x);
                    const translateY = (height / 2) - (focusNode.y);
                    const newTransform = d3.zoomIdentity
                        .translate(translateX, translateY)
                        .scale(1);
                    svg.transition() //Pan in with animation
                        .duration(500)
                        .call(zoomBehavior.transform, newTransform);
                    // zoomBehavior.transform(svg, newTransform); //Without animation
                }
            });


            zoomBehavior = d3.zoom()
                .extent([[0, 0], [width, height]])
                .scaleExtent([0.1, 10])
                .on("zoom", (event) => {
                    zoomGroup.attr("transform", event.transform);
                    ref.attr("transform", event.transform);
                    // console.log("changed to", event.transform);
                });
            svg.call(zoomBehavior);
        }


        //Update simulation internal node and edge lists with possible new nodes and edges
        simulation.nodes(nodes);
        simulation.force("link").links(edges);

        //Set variable to be acessed in tick updates
        if(focusId){
            focusNode = nodeMap.get(focusId);
        }

        //Start a new animation with the updated data
        tickCount = 0;
        alreadyZoomed = false;
        simulation.alpha(1).restart();
        console.log("Animation started");


        //Apply updates to all nodes and edges, existing or new
        svgEdges.selectAll("line")
            .data(edges, d => `${d.source.id}-${d.target.id}-${d.type}`)
            .join(enter => enter.append("line")
                                .attr("class", d => `edge relation-${d.type}`)
                                .attr("stroke", d => relationColors[d.type]),
                                // .attr("marker-end", d => `url(#arrowhead-${d.type})`),
                  update => update,
                  exit => exit.remove()
            );

        svgNodes.selectAll("g")
            .data(nodes, d => d.id)
            .join(enter => {
                    const g = enter.append("g")
                        .call(nodeDrag(simulation))
                        .on("click", nodeClick);
                    g.append("circle")
                        .attr("r", 20)
                    g.append("text")
                        .attr("dx", 0)
                        .attr("dy", "0.35em")
                        .attr("text-anchor", "middle")
                        .attr("fill", "white")
                        .attr("font-size", "10px")
                        .text(d => d.n);
                    return g;
                  },
                  update => update,
                  exit => exit.remove()
            ).select("circle")
            .attr("fill", d => d.expanded? "#0000FF" : "#FF0000")
            .on("mouseenter", (event, d) => {highlightNode = d})
            .on("mouseleave", (event, d) => {highlightNode = null});
    }

    $: console.log(highlightNode);

    onMount(() => {
        console.log("mounted");
        const id = "a6c6897a-7415-4f8d-b5a5-3a5e05f3be67";
        addNode(id).then(() => {
            addNodeRelations(id).then(() => {
                nodes = [...nodes];
                updateGraph(id);
                // });
            });
        });
        console.log("catatau");

    });


</script>

<svg id="genre-graph"
     width="{width}" height="{height}"
     viewBox="[0, 0, {width}, {height}]"
     bind:this={svgNode}>
     <g id="zoom-group"></g>
     <circle id="ref" r="15" opacity="0.5" color="blue" cx={width/2} cy={height/2}>
</svg>

<div class="tooltip"></div>

<style>
    svg {
        border-style: solid;
        border-width: 3px;
        border-color: green;
    }

    .node-circle {
        stroke: white;
        stroke-width: 1.5px;
    }

    .node-text {
        fill: white;
        font-size: 10px;
        text-anchor: middle;
        dominant-baseline: middle;
        pointer-events: none;
    }


</style>
