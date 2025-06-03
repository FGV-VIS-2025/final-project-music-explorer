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


<div class="container">
    <form on:submit={searchTerm}>
        <div class="artistSearchBar">
            <input
                id="cityInput"
                type="text"
                bind:value={searchTerm}
                required
                placeholder="Busque por um gênero"
            />
            <button type="submit">Buscar</button>
        </div>
    </form>
</div>

<main>
    <CollapsibleTree data={originalHierarchicalData} highlightedNames={highlightedNodeNames} />
</main>


<style>
    main {
        background-color: var(--accent-black);
    }

	.container {
		position: fixed;
		top: 40px;
		right: 40px;
		/* transform: translateX(-50%); */
		z-index: 1000;

		width: 90%;
		max-width: 500px;
		box-sizing: border-box;
	}

    .artistSearchBar {
        display: flex;
        width: 100%;
        position: relative;
        background-color: rgba(100, 100, 100, 0.6);
        box-shadow: 0px 0px 5px rgba(100, 100, 100, 0.6);
        border-radius: 8px;
        overflow: hidden;
    }
    
    .artistSearchBar input {
        flex-grow: 1;
        padding: 12px 15px;
        border: none;
        border-radius: 6px 0 0 6px;
        background-color: var(--accent-black);
        color: white;
        font-size: 1rem;
        position: relative;
        z-index: 1;
    }

	.artistSearchBar input:focus {
		outline: #0056b3;
	}

    .artistSearchBar button[type="submit"] {
        padding: 0 18px;
        color: white;
        background-color: #007bff;
        border: none;
        border-radius: 0 6px 6px 0;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        font-weight: bold;
        position: relative;
        z-index: 1;
        transition: background-color 0.2s ease;
    }

	.artistSearchBar button[type="submit"]:hover {
		background-color: #0056b3;
	}

    .results {
        overflow-y: auto;
        max-height: 250px;
        padding: 5px;
        margin-top: 10px;
        border-radius: 6px;
        background-color: #f9f9f9;
    }

    .searchResult {
        display: block;
        width: 100%;
        padding: 12px 15px;
        text-align: left;
        border: none;
        background: none;
        cursor: pointer;
        border-bottom: 1px solid #eee;
        font-size: 0.95rem;
        color: #333;
        transition: background-color 0.15s ease;
    }

	.searchResult:last-child {
		border-bottom: none;
	}

    .searchResult:hover,
	.searchResult:focus {
		background-color: #e9e9e9;
		border-radius: 4px;
	}

	.erro {
		color: #dc3545;
		margin-top: 10px;
	}

	.toggle-button {
		margin-top: 10px;
		padding: 8px 15px;
		background-color: #6c757d;
		color: white;
		border: none;
		border-radius: 4px;
		cursor: pointer;
	}

	.toggle-button:hover {
		background-color: #5a6268;
	}

	.disambiguation {
		font-size: 80%;
		color: gray;
	}
</style>