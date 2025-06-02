<script>
    import CollapsibleTree from "../../lib/components/graphs/genres-tree.svelte";
    import rawData from "../../lib/data/genres.json";

    function buildHierarchy(data) {
        const dataMap = new Map();
        const nodesArray = [];
        const allParentNames = new Set();

        for (const key in data) {
            const node = { name: key, children: [], ...data[key] };
            dataMap.set(key, node);
            nodesArray.push(node);
        }

        nodesArray.forEach(node => {
            if (node.parent && node.parent.length > 0) {
                node.parent.forEach(pName => {
                    allParentNames.add(pName);
                });
            }
        });

        const rootNodes = [];
        const validNodes = new Set();

        nodesArray.forEach(node => {
            let isChild = false;
            if (node.parent && node.parent.length > 0) {
                let foundParentInMap = false;
                node.parent.forEach(pName => {
                    const parentNode = dataMap.get(pName);
                    if (parentNode) {
                        if (!parentNode.children) parentNode.children = [];
                        parentNode.children.push(node);
                        validNodes.add(parentNode.name);
                        validNodes.add(node.name);
                        foundParentInMap = true;
                        isChild = true;
                    }
                });
                if (!foundParentInMap) {
                    if (allParentNames.has(node.name)) {
                        rootNodes.push(node);
                        validNodes.add(node.name);
                    }
                }
            }

            if (!isChild) {
                if (allParentNames.has(node.name)) {
                    rootNodes.push(node);
                    validNodes.add(node.name);
                }
            }
        });

        const finalRootNodes = rootNodes.filter(node => validNodes.has(node.name));
        finalRootNodes.forEach(node => {
            if (!node.children) {
                node.children = [];
            }
        });

        if (finalRootNodes.length > 1) {
            return { name: "", children: finalRootNodes };
        } else if (finalRootNodes.length === 1) {
            return finalRootNodes[0];
        }
        return null;
    }

    let originalHierarchicalData = buildHierarchy(rawData);
    let searchTerm = '';
    let highlightedNodeNames = new Set();
    
    function getPathToNodeByName(node, targetNameString, currentPathNames = [], caseSensitive = false) {
        if (!node) return null;

        const nodeNameStr = typeof node.name === 'string' ? node.name : '';
        const targetNameClean = typeof targetNameString === 'string' ? targetNameString : '';

        const currentNameForCompare = caseSensitive ? nodeNameStr : nodeNameStr.toLowerCase();
        const targetNameForCompare = caseSensitive ? targetNameClean : targetNameClean.toLowerCase();

        currentPathNames.push(node.name); // Add current node's name to the path

        if (nodeNameStr && currentNameForCompare === targetNameForCompare) {
            return [...currentPathNames]; // Target found, return a copy of the path
        }

        if (Array.isArray(node.children)) {
            for (const child of node.children) {
                const foundPath = getPathToNodeByName(child, targetNameClean, currentPathNames, caseSensitive);
                if (foundPath) {
                    return foundPath;
                }
            }
        }

        currentPathNames.pop();
        return null;
    }

    // Reactive statement to update highlightedNodeNames based on searchTerm
    $: {
        if (!originalHierarchicalData) {
            highlightedNodeNames = new Set();
        } else if (!searchTerm.trim()) {
            highlightedNodeNames = new Set(); // No search term, highlight nothing
        } else {
            const searchVal = searchTerm.trim();
            const pathArray = getPathToNodeByName(originalHierarchicalData, searchVal, [], false); // Start with empty path
            if (pathArray && pathArray.length > 0) {
                highlightedNodeNames = new Set(pathArray);
            } else {
                highlightedNodeNames = new Set(); // Not found, highlight nothing
            }
        }
    }
</script>

<main>
    <div class="search-container">
        <input
            type="text"
            bind:value={searchTerm}
            placeholder="Pesquisar por um gênero..."
            aria-label="Search for a genre"
        />
    </div>

    {#if originalHierarchicalData}
        <CollapsibleTree data={originalHierarchicalData} highlightedNames={highlightedNodeNames} />
    {:else if searchTerm.trim()}
        <p>Aguardando dados para pesquisar por "{searchTerm}".</p>
    {:else}
        <p>Carregando dados ou dados de gênero não disponíveis...</p>
    {/if}
</main>

<style>
    main {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 20px;
        gap: 20px;
    }
    .search-container { margin-bottom: 10px; }
    input[type="text"] {
        color: black;
        padding: 10px; font-size: 1rem; width: 300px;
        max-width: 100%; border: 1px solid #ccc; border-radius: 4px;
    }
    p { color: #333; }

</style>