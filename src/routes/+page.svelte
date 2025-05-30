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
    let edges = [];
    let nodeMap = new Map(); //Map to easen getting a node object by its id
    let relations = ["ms", "im", "cs", "gc"]; //Type of relations between nodes
    $: console.log(nodes);
    $: console.log(edges);

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
        let node = { id: id, n: cache[letter][id].n };
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
        console.log(`Adicionei arestas de ${id}`);
    }

    onMount(() => {
        console.log("mounted");
        const id = "57961a97-3796-4bf7-9f02-a985a8979ae9";
        addNode(id).then(() => {
            console.log("catatau 2");
            addNodeRelations(id).then(() => {
                console.log("catatau 3");
                console.log(nodes);
                console.log(edges);
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
     width={width} height={height}
     viewBox="[0, 0, {width}, {height}]"
     bind:this={svgNode}
></svg>
<div class="tooltip"></div>

<style>
</style>
