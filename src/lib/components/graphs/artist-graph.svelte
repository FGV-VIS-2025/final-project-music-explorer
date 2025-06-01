<script>
    import * as d3 from "d3";
    import { onMount } from "svelte";

    export let width = 1280;
    export let height = 720;
    export let importArtist = null; //Input of the component, it will receive an id, focus on it and them set it to null
    let svgNode;

    // let searchInput = ""; // Removed: Unused variable

    let cache = {}; //Where to hold raw data fetched by file
    let nodes = []; //Where node objects are saved
    let edges = []; //Where the edges are saved
    let nodeMap = new Map(); //Map to easen getting a node object by its id

    let relations = ["ms", "im", "cs", "gc"]; //Type of relations between nodes
    let colorPallete = [
        "#EB743B",
        "#BA478F",
        "#669864",
        "#BEAF81",
        "#D99481",
    ];

    // --- Logic for getting the color of each node ---
    let selectedNodeId = null;
    // $: console.log("selectedNodeId", selectedNodeId); // Retained for potential debugging, uncomment if needed
    // $: console.log("selectedNodeData", nodeMap.get(selectedNodeId)); // Retained for potential debugging, uncomment if needed

    function getNodeColor(d) {
        if (!selectedNodeId) {
            // Default color
            return "#a0a0a0";
        }

        const selectedNodeData = nodeMap.get(selectedNodeId);

        if (!selectedNodeData){
            return "#a0a0a0";
        }

        if (d.id === selectedNodeId) {
            return colorPallete[0];
        }

        // Removed specific Elvis Presley console logs as they were likely for debugging a specific case
        // console.log("d", d); // Debug log removed

        // 2. If the related node has made a cover of him ("cs") - RED
        if (d.cs && Object.keys(d.cs).includes(selectedNodeId)) {
            return colorPallete[4];
        }

        // 3. If the related node is a member ("ms") - PURPLE
        if (selectedNodeData.ms && selectedNodeData.ms.includes(d.id)) {
            return colorPallete[2];
        }

        // 4. If the related node is a band the expanded node is in ("im") - GRAY
        if (selectedNodeData.im && selectedNodeData.im.includes(d.id)) {
            return colorPallete[3];
        }

        // 5. If the related node is an artist the expanded node covered ("gc") - YELLOW
        if (selectedNodeData && d.gc && d.gc.includes(selectedNodeId)) { // Added check for d.gc
            return colorPallete[1];
        }

        // Default color for other nodes
        return "gray";
    }

    //Gets a id and add a node object to the nodes array
    async function addNode(id){
        let letter = id.slice(0, 2);
        if(!(letter in cache)) {
            try {
                const response = await fetch(`graph/${letter}.json`);
                if (!response.ok){
                    throw new Error(`Não foi possível solicitar os dados de grafo para a letra ${letter}`);
                }
                const graphData = await response.json();
                cache[letter] = graphData;
            } catch (error) {
                console.error("Erro ao popular cache:", error);
                return;
            }
        }
        if (cache[letter] && cache[letter][id]) {
            let nodeData = cache[letter][id];
            let node = {
                id: id,
                n: nodeData.n,
                expanded: false,
                ms: nodeData.ms || [],
                im: nodeData.im || [],
                cs: nodeData.cs || {},
                gc: nodeData.gc || []
            };
            nodeMap.set(id, node);
            nodes.push(node);
            return node;
        }
        console.warn(`Artist ID ${id} not found in fetched data.`);
        return null;
    }

    //Add edges of an node to other nodes in the graph. Adds the other nodes if necessary
    async function addNodeRelations(id){
        if(simulation){
            simulation.stop().alpha(0);
        }
        let letter = id.slice(0, 2);
        const nodeInfo = cache[letter][id];

        for(let relation of relations){
            const relationData = nodeInfo[relation];

            if (!relationData) {
                // If relationData is undefined or null, skip this relation type for this node
                // console.warn(`No relation data for type "${relation}" on node ${id}`);
                continue; // Changed from return to continue to process other relations
            }
            
            let relatedIds = [];
            
            if(Array.isArray(relationData)){
                relatedIds = relationData;
                 // Process edges for array type relations
                for (let endId of relatedIds) {
                    if (!nodeMap.has(endId)) {
                        const newNode = await addNode(endId);
                        if (!newNode) continue;
                    }
                    let sourceNode = nodeMap.get(id);
                    let targetNode = nodeMap.get(endId);
                    
                    // Avoid adding duplicate edges
                    const edgeExists = edges.some(e => 
                        e.source.id === sourceNode.id && e.target.id === targetNode.id && e.type === relation ||
                        e.source.id === targetNode.id && e.target.id === sourceNode.id && e.type === relation // Consider directionality if needed
                    );

                    if (!edgeExists) {
                        edges.push({
                            source: sourceNode,
                            target: targetNode,
                            type: relation
                        });
                    }

                    updateGraph()
                }
            } else if(typeof relationData === 'object' && relationData !== null) {
                relatedIds = Object.keys(relationData);
                for (let endId of relatedIds){
                    if (!nodeMap.has(endId)){
                        const newNode = await addNode(endId);
                        if (!newNode) continue;
                    }
                    
                    let sourceNode = nodeMap.get(id);
                    let targetNode = nodeMap.get(endId);
                    
                     // Avoid adding duplicate edges
                    const edgeExists = edges.some(e => 
                        e.source.id === sourceNode.id && e.target.id === targetNode.id && e.type === relation ||
                        e.source.id === targetNode.id && e.target.id === sourceNode.id && e.type === relation
                    );

                    if(!edgeExists) {
                        edges.push({
                            source: sourceNode,
                            target: targetNode,
                            type: relation
                        });
                    }
                    updateGraph() // Called once after all relations for the node are processed
                }
            }
        }
        nodeMap.get(id).expanded = true;
        edges = [...edges]; // Trigger Svelte reactivity if needed elsewhere, D3 updates separately
        updateGraph(); // Call updateGraph once after processing all relations for the current node
    }

    //Handle external sent artist focusing event
    let expanding = false;
    $: {
        if(importArtist && !expanding){
            expanding = true;
            if (!nodeMap.has(importArtist)){
                addNode(importArtist).then((node) => {
                    if (node) {
                        addNodeRelations(importArtist).then(() => {
                            selectedNodeId = importArtist;
                            updateGraph();
                            importArtist = null;
                            expanding = false;
                        });
                    } else { // Handle case where node couldn't be added
                        importArtist = null;
                        expanding = false;
                    }
                });
            } else if(!nodeMap.get(importArtist).expanded) {
                addNodeRelations(importArtist).then(() => {
                    selectedNodeId = importArtist;
                    updateGraph();
                    importArtist = null;
                    expanding = false;
                });
            } else {
                selectedNodeId = importArtist;
                updateGraph();
                importArtist = null;
                expanding = false;
            }
        }
    }

    //Handle artist click event
    function nodeClick(event, node){
        if(!expanding){
            expanding = true;
            
            // Optional: If you want to collapse previously selected node when a new one is clicked
            // if (selectedNodeId && selectedNodeId !== node.id && nodeMap.has(selectedNodeId)) {
            //     const previouslySelectedNode = nodeMap.get(selectedNodeId);
            //     if (previouslySelectedNode) previouslySelectedNode.expanded = false;
            //      // Optionally, remove edges related to the previously selected node if desired
            // }
            
            console.log("Clicked node", node)
            selectedNodeId = node.id;

            if (node.expanded){
                // If node is already expanded, perhaps just focus it or do nothing
                // console.log("Node already expanded, just re-focusing.");
                expanding = false;
                updateGraph(); // Re-color or re-center
            } else {
                // --- Adding zoom out before adding relations ---
                const svg = d3.select(svgNode)
                if (!svg.empty() && zoomBehavior && node.x !== undefined) {
                    const scale = 0.7

                    const targetX = node.x;
                    const targetY = node.y;
                    
                    const newTransform = d3.zoomIdentity
                        .translate(width / 2 - targetX * scale, height / 2 - targetY * scale)
                        .scale(scale);

                    svg.transition()
                        .duration(750) // Duration for zoom out
                        .call(zoomBehavior.transform, newTransform)
                        .on("end", () => { // After zoom, proceed to add relations
                            addNodeRelations(node.id).then(() => {
                                // updateGraph is called within and at the end of addNodeRelations
                                expanding = false;
                            });
                        });
                }
                else{
                    // Fallback if SVG/zoom not ready or node position unknown (should be rare for a clicked node)
                    console.warn("SVG or node position not available for pre-zoom.");
                    addNodeRelations(node.id).then(() => {
                        // updateGraph(); // updateGraph is called within addNodeRelations
                        expanding = false;
                    });
                }
                
                // addNodeRelations(node.id).then(() => {
                //     // node.expanded is set to true inside addNodeRelations
                //     updateGraph();
                //     expanding = false;
                // });
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

    //D3 variables
    let simulation;
    let svgEdges;
    let svgNodes;
    let svgLabels;
    let zoomBehavior;
    let tickCount = 0;
    let alreadyZoomed = false;
    let focusNode; 

    let highlightNode; 
    function updateGraph() {
        const svg = d3.select(svgNode);
        const zoomGroup = d3.select("#zoom-group");
        // let ref = d3.select("#ref"); // Removed as #ref element doesn't exist in SVG
        if (!simulation) {
            simulation = d3.forceSimulation(nodes)
                .force("link", d3.forceLink(edges).id((d) => d.id).distance(100))
                .force("charge", d3.forceManyBody().strength(-300))
                .force("center", d3.forceCenter(0, 0));

            svgEdges = zoomGroup.append("g").attr("stroke", "#999").attr("stroke-opacity", 0.6);
            svgNodes = zoomGroup.append("g").attr("stroke", "#fff").attr("stroke-width", 1.5);
            svgLabels = zoomGroup.append("g").attr("class", "labels");

            simulation.on("end", () => {
                tickCount = 0;
                alreadyZoomed = false;
                focusNode = null;
            });

            simulation.on("tick", () => {
                svgEdges.selectAll("line")
                    .attr("x1", (d) => d.source.x)
                    .attr("y1", (d) => d.source.y)
                    .attr("x2", (d) => d.target.x)
                    .attr("y2", (d) => d.target.y);
                svgNodes.selectAll("g")
                    .attr("transform", (d) => `translate(${d.x},${d.y})`);
                svgLabels.selectAll("text")
                    .attr("x", (d) => d.x)
                    .attr("y", (d) => d.y);

                tickCount++;
                if(tickCount > 60 && !alreadyZoomed && focusNode){
                    alreadyZoomed = true;
                    const translateX = (width / 2) - (focusNode.x);
                    const translateY = (height / 2) - (focusNode.y);
                    const newTransform = d3.zoomIdentity
                        .translate(translateX, translateY)
                        .scale(1); // You might want to adjust scale or make it dynamic
                    svg.transition()
                        .duration(500)
                        .call(zoomBehavior.transform, newTransform);
                }
            });

            zoomBehavior = d3.zoom()
                .extent([[0, 0], [width, height]])
                .scaleExtent([0.1, 10])
                .on("zoom", (event) => {
                    zoomGroup.attr("transform", event.transform);
                    // ref.attr("transform", event.transform); // Removed as #ref was removed
                });
            svg.call(zoomBehavior);
        }

        simulation.nodes(nodes);
        simulation.force("link").links(edges);
        
        // console.log("Animation started"); // Redundant console.log removed

        if(selectedNodeId && nodeMap.has(selectedNodeId)){ // Ensure node exists before trying to get it
            focusNode = nodeMap.get(selectedNodeId);
        } else {
            focusNode = null; // Reset focusNode if selectedNodeId is not valid
        }

        tickCount = 0;
        alreadyZoomed = false;
        simulation.alpha(1).restart();
        // console.log("Animation started"); // This one is fine

        svgEdges.selectAll("line")
            .data(edges, d => `${d.source.id}-${d.target.id}-${d.type}`)
            .join(
                enter => enter.append("line")
                    .attr("class", d => `edge relation-${d.type}`)
                    .attr("stroke", "#999") // Default edge color
                    .attr("stroke-opacity", "0.6"),
                update => update,
                exit => exit.remove()
            );

        const nodeGs = svgNodes.selectAll("g")
            .data(nodes, d => d.id)
            .join(enter => {
                    const g = enter.append("g")
                        .call(nodeDrag(simulation))
                        .on("click", nodeClick)
                        .on("mouseenter", (event, d) => {highlightNode = d;})
                        .on("mouseleave", () => {highlightNode = null;}); // Simplified mouseleave
                    g.append("circle")
                        .attr("r", 20);
                    return g;
                },
                update => update,
                exit => exit.remove()
            );
            
        nodeGs.select("circle")
            .attr("fill", d => getNodeColor(d))
            .attr("stroke", "#000") // Ensuring stroke is applied
            .attr("stroke-width", 1.5); 
            
        svgLabels.selectAll("text")
            .data(nodes, d => d.id)
            .join(enter => enter.append("text")
                .attr("dx", 0)
                .attr("dy", "0.35em") // Vertically center
                .attr("text-anchor", "middle") // Horizontally center
                // .attr("fill", "white") // Overridden below, can remove
                .attr("font-size", "10px")
                .attr("pointer-events", "none") 
                .attr("fill", "black") 
                .text(d => d.n),
                update => update,
                exit => exit.remove()
            )
            .attr("fill", "#fff") // Final label color - ensure this is what you want over "black"
            .attr("font-weight", d => d.id === selectedNodeId ? "bold" : "normal");
    }

    onMount(() => {
        const id = "a6c6897a-7415-4f8d-b5a5-3a5e05f3be67"; // Example initial node
        addNode(id).then((node) => {
            if (node){
                addNodeRelations(id).then(() => {
                    nodes = [...nodes]; // Ensure Svelte sees the change if nodes array itself needs to be reactive
                    selectedNodeId = id;
                    updateGraph();
                });
            }
        });
    });

</script>

<div class="graph-visualization">
    <div class="graph-container">
        <svg bind:this={svgNode} width={width} height={height}>
            <g id="zoom-group"></g>
        </svg>
        
    </div>
    <div class="tooltip">
        {#if highlightNode}
            <div style="position: absolute; top: 230px; left: 10px; background: white; padding: 5px; border: 1px solid #ccc; border-radius: 5px">
                <strong>Artist:</strong> {highlightNode.n}
            </div>
        {/if}
    </div>
</div>

<style>
    /* Removed '*' selector as it's too broad and can cause unintended styling issues. 
       Set body or specific container color if a global default is needed. */
    
    svg {
        border-style: solid;
        border-width: 3px;
        border-color: green;
        display: block; /* Often good for SVG to prevent extra space */
    }

    .graph-visualization {
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center; /* Example: center the graph container */
    }

    .tooltip div,
    .tooltip strong{
        fill: black;
        color: black;
    }
</style>