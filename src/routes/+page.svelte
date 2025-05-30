<script>
    import * as d3 from "d3";

    import { onMount } from "svelte";

    let width = 1280;
    let height = 720;
    let svgNode;

    let searchInput = "";
    $: console.log(searchInput);

    let cache = {}; //Where to hold raw data fetched by file
    let nodes = []; //Where node objects are saved
    let edges = []; //Where the edges are saved
    let nodeMap = new Map(); //Map to easen getting a node object by its id
    let relations = ["ms", "im", "cs"]; //Type of relations between nodes
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
        let letter = id.slice(0, 2);
        //I assume the cache exists since this function will not be called if the node isnt in the graph in the first place.
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
                }
            }
        }
        nodeMap.get(id).expanded = true;
        edges = [...edges];
        console.log(`Adicionei arestas de ${id}`);
    }

    function nodeClick(event, node){
        if (node.expanded){
            console.log("node already expanded will do nothing");
        } else {
            addNodeRelations(node.id).then(() => {
                updateGraph();
            });
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
    let simulation;
    let svgEdges;
    let svgNodes;
    function updateGraph() {
        const svg = d3.select(svgNode);
        const zoomGroup = d3.select("#zoom-group");

        if (!simulation) {
            //Create simulation and initial classes if they didnt exist before
            simulation = d3.forceSimulation(nodes)
                .force("link", d3.forceLink(edges).id((d) => d.id).distance(100))
                .force("charge", d3.forceManyBody().strength(-300))
                .force("center", d3.forceCenter(width / 2, height / 2));

            svgEdges = zoomGroup.append("g").attr("stroke", "#999").attr("stroke-opacity", 0.6);
            svgNodes = zoomGroup.append("g").attr("stroke", "#fff").attr("stroke-width", 1.5);

            simulation.on("tick", () => {
                svgEdges.selectAll("line")
                    .attr("x1", (d) => d.source.x)
                    .attr("y1", (d) => d.source.y)
                    .attr("x2", (d) => d.target.x)
                    .attr("y2", (d) => d.target.y);
                svgNodes.selectAll("g")
                    .attr("transform", (d) => `translate(${d.x},${d.y})`);
            });

            const zoomBehavior = d3.zoom()
                .extent([[0, 0], [width, height]])
                .scaleExtent([0.1, 10])
                .on("zoom", (event) => {
                    zoomGroup.attr("transform", event.transform);
                });
            svg.call(zoomBehavior);
        }

        //Update simulation internal node and edge lists with possible new nodes and edges
        simulation.nodes(nodes);
        simulation.force("link").links(edges);
        //Start a new animation with the updated data
        simulation.alpha(1).restart();

        //Apply updates to all nodes and edges, existing or new
        svgEdges.selectAll("line")
            .data(edges, d => `${d.source.id}-${d.target.id}-${d.type}`)
            .join(enter => enter.append("line")
                                .attr("class", d => `edge ${d.type}`),
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
                        .attr("fill", "#FF0000");
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
            );
    }

    onMount(() => {
        console.log("mounted");
        const id = "a6c6897a-7415-4f8d-b5a5-3a5e05f3be67";
        addNode(id).then(() => {
            addNodeRelations(id).then(() => {
                nodes = [...nodes];
                updateGraph();
                // const svg = d3.select(svgNode);
                // svgEdges = svg.select(".edges");
                // svgNodes = svg.select(".nodes");
                // console.log(svgNodes, svgEdges);
                //
                // simulation = d3.forcesimulation(nodes)
                //     .force("link", d3.forceLink(edges).id((d) => d.id).distance(150)) // Força de ligação (atração)
                //     .force("charge", d3.forceManyBody().strength(-300)) // Força de carga (repulsão entre os nós)
                //     .force("center", d3.forceCenter(width / 2, height / 2)); // Força para centralizar o grafo
                // simulation.on("tick", () => {
                //     console.log("ticking");
                //     //Não é o ideal mas pro momento é o que há
                //     nodes = [...nodes];
                //     edges = [...edges];
                // });
            });
        });
        console.log("catatau");

    });


</script>

<h1>Music explorer</h1>
<p>Hello world</p>

<div id="search-wrapper">
    <input type="text"
           id="search-input"
           placeholder="Search Genre..."
           autocomplete="off"
           bind:value={searchInput}>
    <div id="suggestions-list"></div>
</div>

<svg id="genre-graph"
     width="{width}" height="{height}"
     viewBox="[0, 0, {width}, {height}]"
     bind:this={svgNode}>
     <g id="zoom-group"></g>
    <!--<g stroke="#999" stroke-width="1.5" class="edges">
    {#each edges as edge}
        <line class="edge {edge.type}"
              x1={edge.source.x} y1={edge.source.y}
              x2={edge.target.x} y2={edge.target.y}/>
    {/each}
    </g>
    <g class="nodes">
    {#each nodes as node}
        <g transform="translate({node.x},{node.y})" on:click={() => {addNodeRelations(node.id); simulation.nodes(nodes); simulation.force("link").links(edges); simulation.alpha(1).restart();}}>
            <circle r="20" fill="#FF0000"/>
        </g>
    {/each}
    </g>-->
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
