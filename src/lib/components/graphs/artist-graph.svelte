<script>
    import * as d3 from "d3";
    import { onMount } from "svelte";

    export let width = 1280;
    export let height = 720;

    export let importArtist = null; //Input of the component, it will receive an id, focus on it and them set it to null
    export let removeArtist = null; //Input of the component, it will receive an id and remove it from graph them set to null
    export let forceHighlight = null;

    export let nodeMap; //Map to easen getting a node object by its id
    export let expandedNodes = []; //Shared resource with other components
    export let expanding; //Shared resource with other components
    export let selectedNode = null; //Shared resource with other components
    export let activeLegendItems = {}; //Shared resource with other components

    $: console.log(forceHighlight);

    let svgNode;

    let resizeObserver;
    let currentZoomScale = 1;

    let cache = {}; //Where to hold raw data fetched by file
    let nodes = []; //Where node objects are saved
    let edges = []; //Where the edges are saved

    let relations = ["ms", "im", "cs", "gc"]; //Type of relations between nodes
    let colorPallete = [
        "#EB743B",
        "#BA478F",
        "#669864",
        "#BEAF81",
        "#D99481",
    ];
    //Olá
    const legendItemDetails = [
        { key: "selected", text: "Selected artist/band", color: colorPallete[0], clickable: false},
        { key: "cs", text: "Covered song from selected artist/band🖱️", color: colorPallete[1], clickable: true},
        { key: "ms", text: "Member of selected band🖱️", color: colorPallete[2], clickable: true},
        { key: "im", text: "Band selected artist is Member Of🖱️", color: colorPallete[3], clickable: true},
        { key: "gc", text: "Artist/band Covered by selected artist/band🖱️", color: colorPallete[4], clickable: true},
        { key: "default", text: "Not directly related to the selected artist/band", color: "#a0a0a0", clickable: false},
    ];

    legendItemDetails.forEach(item => {
        activeLegendItems[item.key] = true;
    });
    
    let clickableLegendItems = {};
    legendItemDetails.forEach(item => {
        clickableLegendItems[item.key] = item.clickable;
    });

    let legendDisplayItems = []
    legendDisplayItems = legendItemDetails.map(item => ({
        ...item,
        active: activeLegendItems[item.key], // Get current active state
        clickable: clickableLegendItems[item.key] // Get current active state
    }));

    // --- Logic for getting the color of each node ---
    // $: console.log("selectedNodeId", selectedNodeId); // Retained for potential debugging, uncomment if needed
    // $: console.log("selectedNodeData", nodeMap.get(selectedNodeId)); // Retained for potential debugging, uncomment if needed

    $: console.log(activeLegendItems);

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

        //membership relations come first so they wont be painted with cover data

        // 1. If the related node is a member ("ms")
        if (activeLegendItems.ms && selectedNodeData.ms && selectedNodeData.ms.includes(d.id)) {
            return colorPallete[2];
        }

        // 2. If the related node is a band the expanded node is in ("im")
        if (activeLegendItems.im && selectedNodeData.im && selectedNodeData.im.includes(d.id)) {
            return colorPallete[3];
        }

        // 3. If the related node is an artist the expanded node covered ("gc")
        if (activeLegendItems.gc && selectedNodeData && d.gc && d.gc.includes(selectedNodeId)) { // Added check for d.gc
            return colorPallete[4];
        }

        // 4. If the related node has made a cover of him ("cs")
        if (activeLegendItems.cs && d.cs && Object.keys(d.cs).includes(selectedNodeId)) {
            return colorPallete[1];
        }

        // Default color for other nodes
        // return "gray";
        return activeLegendItems["default"] !== false ? "#a0a0a0" : "rgba(0,0,0,0)"; // Grey or transparent
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
                gc: nodeData.gc || [],
                linkCount: 0
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
            if (!activeLegendItems[relation]) {
                continue
            }
            
            // Determine the actual data key on the node object
            let dataAccessKey = relation;
            if (relation === "cs") { // Legend "cs": artists who covered selected node
                dataAccessKey = "gc"; // Data is in selected node's 'gc' property (array)
            } else if (relation === "gc") { // Legend "gc": artists selected node covered
                dataAccessKey = "cs"; // Data is in selected node's 'cs' property (object)
            }

            const relationData = nodeInfo[dataAccessKey];

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
                        sourceNode.linkCount += 1;
                        targetNode.linkCount += 1;
                    }
                    
                    // TODO: Review Graph animation
                    // updateGraph()
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
                        sourceNode.linkCount += 1;
                        targetNode.linkCount += 1;
                    }
                    // TODO: Review Graph animation
                    // updateGraph() // Called once after all relations for the node are processed
                }
            }
        }
        nodeMap.get(id).expanded = true;
        expandedNodes = [...expandedNodes, nodeMap.get(id)];
        edges = [...edges];
        updateGraph(); // Call updateGraph once after processing all relations for the current node
    }

    //Remove edges from an expanded node, also removing any orphan node
    //As addNodeRelations, this needs to be protected with the expanding variable!
    function RemoveNodeRelations(id){
        if(simulation){
            simulation.stop().alpha(0);
        }
        if(!nodeMap.has(id) || !nodeMap.get(id).expanded){
            console.warn(`Tried to unexpand node ${id} but it wasnt expanded`);
        }
        let node = nodeMap.get(id); //Ensured that exists

        for(let i = edges.length - 1; i >= 0; --i) { //Old fashioned way of looping because elements are being removed
            let edge = edges[i];
            let other = null;
            if(edge.source.id == id){
                other = edge.target;
            } else if(edge.target.id == id){
                other = edge.source;
            }
            if(other && !other.expanded){
                edges.splice(i, 1);
                node.linkCount -= 1;
                other.linkCount -= 1;
                if (other.linkCount == 0){
                    nodeMap.delete(other.id);
                    const arrayIndex = nodes.indexOf(other);
                    if (arrayIndex > -1) {
                        nodes.splice(arrayIndex, 1);
                    }
                }
                if (node.linkCount == 0){
                    nodeMap.delete(node.id);
                    const arrayIndex = nodes.indexOf(node);
                    if (arrayIndex > -1) {
                        nodes.splice(arrayIndex, 1);
                    }
                    break; //No more edges will point to it
                }
                updateGraph();
            }
        }
        if(node.linkCount != 0){
            node.expanded = false;
        }
        const arrayIndex = expandedNodes.indexOf(node);
            if (arrayIndex > -1) {
                expandedNodes.splice(arrayIndex, 1);
            }
        expandedNodes = [...expandedNodes];
        edges = [...edges];
        updateGraph();
    }

    //Handle external sent artist focusing event
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

    //Handle external set artist remove event
    $: {
        if(removeArtist && !expanding){
            expanding = true;
            RemoveNodeRelations(removeArtist);
            removeArtist = null;
            expanding = false;
        }
    }
    let selectedNodeId;
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
    $: {
        selectedNode = nodeMap.get(selectedNodeId);
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

    //Checks if a node has an displayed edge with another
    function isConnectedWith(node_1, node_2){
        //True if they are the same
        if(node_1.id == node_2.id){
            return true;
        }
        //If both are unexpanded then no edge can exist between them
        if (!(node_2.expanded || node_1.expanded)){
            return false;
        }
        //Seeks in all the relations (even unexpanded ones) if they are related. No ghost edge will happen here because of the above condition.
        for (let relation of relations){
            if(Array.isArray(node_1[relation])){
                if(node_1[relation].includes(node_2.id)){
                    return true;
                }
            }
            else {
                if(Object.hasOwn(node_1[relation], node_2.id)){
                    return true;
                }
            }
        }
        return false;
    }

    let highlightNode;
    let tooltipTop = 0;
    let tooltipLeft = 0;

    //I call the function in the reactive block instead of doing directly there to avoid triggering by node or edge variable update
    $: HandleHighlight(highlightNode);

    function HandleHighlight(node){
        if(nodeGs && svgEdges){ //Only do when there are cicles and edges in graph
            if(node){ //Verify the relations of adjacency
                nodeGs.select("circle")
                    .attr("stroke", d => {return isConnectedWith(node, d)? "#FFF" : "#000";})
                    .attr("stroke-width", d => {return isConnectedWith(node, d)? 3 : 1.5});
                svgEdges.selectAll("line")
                    .attr("stroke", e => {return (e.target.id == node.id || e.source.id == node.id) ? "#FFF" : "#999"})
                    .attr("stroke-width", e => {return (e.target.id == node.id || e.source.id == node.id) ? 3 : 1})
            } else { //reset to default values
                nodeGs.select("circle")
                    .attr("stroke", "#000") // Ensuring stroke is applied
                    .attr("stroke-width", 1.5);
                svgEdges.selectAll("line")
                    .attr("stroke", "#999") // Default edge color
                    .attr("stroke-width", 1) // Default edge color
            }
            // console.log("handled highlight change")
        }
    }

    async function toggleLegendItem(itemKey) {
        const visualOnlyLegendKeys = ['selected', 'default']

        if (visualOnlyLegendKeys.includes(itemKey)) {
            return;
        }

        if (expanding) {
            console.warn("Graph is busy (expanding/modifying). Please try toggling legend item later.");
            return; // Prevent concurrent modifications
        }

        expanding = true

        let wasActive = activeLegendItems[itemKey]
        activeLegendItems[itemKey] = !activeLegendItems[itemKey]

        if (wasActive) {
            _remove_edges_and_orphans_by_type(itemKey)
            updateGraph()
        } else {
            // Relation was inactive, now it's being activated (marked)
            await _add_edges_for_newly_active_type(itemKey);
            updateGraph()
        }
        
        expanding = false; // Release lock
        
        legendDisplayItems = legendItemDetails.map(item => ({
            ...item,
            active: activeLegendItems[item.key] // Get current active state
        }));

        updateGraph()
    }

    function _remove_edges_and_orphans_by_type(relationType) {
        if (simulation) {
            simulation.stop().alpha(0); // Stop simulation during modification
        }

        const remainingEdges = [];
        for (const edge of edges) {
            if (edge.type === relationType) {
                // Decrement link count for connected nodes
                if (edge.source) edge.source.linkCount--;
                if (edge.target) edge.target.linkCount--;
            } else {
                remainingEdges.push(edge);
            }
        }
        edges = remainingEdges;

        // Remove orphan nodes (nodes with linkCount 0 that are NOT expanded and NOT selected)
        const currentNodes = [];
        for (const node of nodes) {
            if (node.linkCount === 0 && !node.expanded && node.id !== selectedNodeId) {
                nodeMap.delete(node.id); // Remove from map
            } else {
                currentNodes.push(node);
            }
        }
        nodes = currentNodes;
        
        // Ensure nodes array reflects the current state of nodeMap if any selected/expanded nodes were somehow affected
        // This pass primarily cleans up non-essential orphans.
        // A more robust cleanup might be needed if expanded nodes can become "orphaned" by filters.
    }

    async function _add_edges_for_newly_active_type(relationType) {
        if (simulation) {
            simulation.stop().alpha(0);
        }

        const currentExpandedNodes = [...expandedNodes]; // Iterate over a stable copy

        for (const sourceNode of currentExpandedNodes) {
            const nodeId = sourceNode.id;
            const letter = nodeId.slice(0, 2);

            if (!cache[letter] || !cache[letter][nodeId]) {
                console.warn(`Cache miss for expanded node ${nodeId} while re-activating relation ${relationType}`);
                continue;
            }
            const nodeInfo = cache[letter][nodeId];
            
            let dataAccessKey = relationType; // relationType is the legend key
            if (relationType === "cs") {
                dataAccessKey = "gc";
            } else if (relationType === "gc") {
                dataAccessKey = "cs";
            }
            const relationData = nodeInfo[dataAccessKey];

            if (!relationData) continue;

            let relatedIds = [];
            if (Array.isArray(relationData)) {
                relatedIds = relationData;
            } else if (typeof relationData === 'object' && relationData !== null) {
                relatedIds = Object.keys(relationData);
            }

            for (const targetId of relatedIds) {
                let targetNode = nodeMap.get(targetId);
                if (!targetNode) {
                    const newNode = await addNode(targetId); // addNode adds to 'nodes' and 'nodeMap'
                    if (!newNode) continue;
                    targetNode = newNode;
                }

                const edgeExists = edges.some(e =>
                    e.type === relationType &&
                    ((e.source.id === nodeId && e.target.id === targetId) ||
                    (e.source.id === targetId && e.target.id === nodeId))
                );

                if (!edgeExists && sourceNode && targetNode) {
                    edges.push({
                        source: sourceNode,
                        target: targetNode,
                        type: relationType
                    });
                    sourceNode.linkCount++;
                    targetNode.linkCount++;
                }
            }

        }
        edges = [...edges]; // Trigger Svelte reactivity
        nodes = [...nodes]; // Trigger Svelte reactivity
    }

    //D3 variables
    let simulation;
    let svgEdges;
    let svgNodes;
    let svgLabels;
    let nodeGs;
    let zoomBehavior;
    let tickCount = 0;
    let alreadyZoomed = false;
    let focusNode;

    // Constante para o limite de zoom para mostrar o texto
    const TEXT_ZOOM_THRESHOLD = 0.6;
    const BASE_FONT_SIZE = 11; // Em pixels

    function updateGraph() {
        const svg = d3.select(svgNode);
        const zoomGroup = d3.select("#zoom-group");
        // let ref = d3.select("#ref"); // Removed as #ref element doesn't exist in SVG
        if (!simulation) {
            simulation = d3.forceSimulation(nodes)
                .force("link", d3.forceLink(edges).id((d) => d.id).distance(100))
                .force("charge", d3.forceManyBody().strength(-500))
                .force("x", d3.forceX())
                .force("y", d3.forceY());

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
                    .attr("y", (d) => d.y)


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
                    currentZoomScale = event.transform.k; // Armazena o nível de zoom

                    svgLabels.selectAll("text")
                        .attr("opacity", d => {
                            if (d.expanded) {
                                return 1;
                            }
                            if (currentZoomScale > TEXT_ZOOM_THRESHOLD) {
                                return 1;
                            }
                            return 0;
                        })
                        .attr("font-size", d => {
                            if (d.expanded) {
                                const effectiveScale = Math.max(0.1, currentZoomScale);
                                return `${Math.max(BASE_FONT_SIZE,BASE_FONT_SIZE / effectiveScale**1.1)}px`;
                            }
                            return  `${BASE_FONT_SIZE}px`;
                        });
                    // ref.attr("transform", event.transform); // Removed as #ref was removed
                });
            svg.call(zoomBehavior);
        } else {
            // Se a simulação já existe, apenas atualize as forças de centro com as novas dimensões
            simulation.force("x", d3.forceX(width / 2))
                      .force("y", d3.forceY(height / 2));
            zoomBehavior.extent([[0, 0], [width, height]]); // Atualiza a extensão do zoom
            d3.select(svgNode).call(zoomBehavior); // Re-aplica o comportamento de zoom no SVG
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
                    .attr("stroke-opacity", "0.6")
                    .attr("stroke-width", 1),
                update => update,
                exit => exit.remove()
            );

        nodeGs = svgNodes.selectAll("g")
            .data(nodes, d => d.id)
            .join(enter => {
                    const g = enter.append("g")
                        .call(nodeDrag(simulation))
                        .on("click", nodeClick)
                        .on("mouseenter", (event, d) => {highlightNode = d; tooltipLeft = event.pageX; tooltipTop = event.pageY;})
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
                .attr("font-size", "10px")
                .attr("pointer-events", "none")
                .attr("fill", "#fff") // Final label color
                .attr("font-weight", d => d.id === selectedNodeId ? "bold" : "normal")
                .attr("opacity", d => { // Define a opacidade inicial
                    if (d.expanded) {
                        return 1;
                    }
                    if (currentZoomScale > TEXT_ZOOM_THRESHOLD) {
                        return 1;
                    }
                    return 0;
                })
                .text(d => d.n),
                update => update
                    .attr("opacity", d => { // Atualiza a opacidade no update
                        if (d.expanded) {
                            return 1;
                        }
                        if (currentZoomScale > TEXT_ZOOM_THRESHOLD) {
                            return 1;
                        }
                        return 0;
                    })
                    .attr("font-weight", d => d.id === selectedNodeId ? "bold" : "normal"), // Garante que o negrito é aplicado no update
                exit => exit.remove()
            );

            // --- Creating legend for the colors ---
            let legendGroup = svg.select("g.legend")
            if (legendGroup.empty()){
                legendGroup = svg.append("g")
                    .attr("class", "legend")
                    .attr("transform", "translate(20, 20)")
            }

            const legendItemSelection = legendGroup.selectAll("g.legend-item")
                .data(legendDisplayItems, d => d.key)
            
            legendItemSelection.join(
                enter => {
                    const legendItemG = enter.append('g')
                        .attr("class", "legend-item")
                        .attr("transform", (d, i) => `translate(0, ${i * 25})`)
                        .style("cursor", d => d.clickable ? "pointer" : "default")
                        .on("click", (event, d_clicked) => { // Use d_clicked to avoid conflict with outer d if any
                            toggleLegendItem(d_clicked.key);
                        });
                    
                    legendItemG.append('rect')
                        .attr("class", "legend-color-checkbox")
                        .attr("x", 0)
                        .attr("y", 0)
                        .attr("width", 18)
                        .attr("height", 18)
                        // Fill color depends on the active state
                        .style("fill", d => d.active ? d.color : "black")
                        // Border color is the item's specific color
                        .style("stroke", d => d.color) // Checkbox border color
                        .style("stroke-width", 1);

                    // Text label for the legend item
                    legendItemG.append('text')
                        .attr("class", "legend-text")
                        .attr("x", 22 + 18 + 5) // Positioned after the color swatch, with some padding
                        .attr("y", 9) // Align with middle of checkbox/color swatch
                        .attr("dy", "0.35em") // Vertical alignment adjustment
                        .style("font-family", "sans-serif")
                        .style("font-size", "12px")
                        .style("fill", "#fff") // Text color for the legend
                        .text(d => d.text);
                        
                        return legendItemG;
                    },
                    update => {
                        // Update the checkmark text (visibility) when data changes
                        update.select("rect.legend-color-checkbox")
                        .style("fill", d => d.active ? d.color : "none");
                        
                        update.select("text.legend-text")
                            .style("text-decoration", d => d.active ? "none" : "line-through")
                            .style("opacity", d => d.active ? 1 : 0.6)

                    // If color or text could change, update them here too:
                    // update.select("rect.color-swatch").style("fill", d => d.color);
                    // update.select("text.legend-text").text(d => d.text);
                    return update;
                },
                exit => exit.remove()
            )
    }

    onMount(() => {
        resizeObserver = new ResizeObserver(entries => {
            for (let entry of entries) {
                width = entry.contentRect.width;
                height = entry.contentRect.height;
                updateGraph();
            }
        });

        if (svgNode) {
            resizeObserver.observe(svgNode);
        }

        const id = "a6c6897a-7415-4f8d-b5a5-3a5e05f3be67"; // Example initial node
        expanding = true;
        addNode(id).then((node) => {
            if (node){
                addNodeRelations(id).then(() => {
                    nodes = [...nodes]; // Ensure Svelte sees the change if nodes array itself needs to be reactive
                    selectedNodeId = id;
                    expanding = false;
                    updateGraph();
                });
            }
        });

        return () => {
            if (resizeObserver) {
                resizeObserver.disconnect();
            }
        };
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
            <div style="position: absolute; top: {tooltipTop}px; left: {tooltipLeft}px; transform: translate(15px, -20px);">
                <strong>Artista:</strong> {highlightNode.n}
                {#if selectedNodeId}
                    {#if highlightNode.gc.includes(selectedNodeId)}
                        <br>
                        <strong>Músicas de {highlightNode.n} que {nodeMap.get(selectedNodeId).n} fez cover:</strong>
                        {nodeMap.get(selectedNodeId).cs[highlightNode.id][1].join(", ")}
                    {:else if highlightNode.cs.hasOwnProperty(selectedNodeId)}
                        <br>
                        <strong>Músicas de {nodeMap.get(selectedNodeId).n} que {highlightNode.n} fez cover:</strong>
                        {highlightNode.cs[selectedNodeId][1].join(", ")}
                    {/if}
                {/if}
            </div>
        {/if}
    </div>
</div>

<style>
    svg {
        display: block; /* Often good for SVG to prevent extra space */
        width: 100vw;
        height: 100vh;
        box-sizing: border-box;
    }

    .graph-visualization {
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center; /* Example: center the graph container */
    }

    .tooltip div {
        max-width: 45ch;

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

    .relations-selector-container {
        display: flex;
        align-items: center;
        position: absolute;

        left: 450px;
    }
</style>
