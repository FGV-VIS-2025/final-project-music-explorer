export function getHighlightedPathForGenreTree(rawData, searchTerm) {

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
                if (!foundParentInMap && allParentNames.has(node.name)) {
                     rootNodes.push(node);
                     validNodes.add(node.name);
                }
            }

            if (!isChild && allParentNames.has(node.name)) {
                rootNodes.push(node);
                validNodes.add(node.name);
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

    function getPathToNodeByName(node, targetNameString, currentPathNames = [], caseSensitive = false) {
        if (!node) return null;

        const nodeNameStr = typeof node.name === 'string' ? node.name : '';
        const targetNameClean = typeof targetNameString === 'string' ? targetNameString : '';

        const currentNameForCompare = caseSensitive ? nodeNameStr : nodeNameStr.toLowerCase();
        const targetNameForCompare = caseSensitive ? targetNameClean : targetNameClean.toLowerCase();

        currentPathNames.push(node.name);

        if (nodeNameStr && currentNameForCompare === targetNameForCompare) {
            return [...currentPathNames];
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

    const hierarchicalData = buildHierarchy(rawData);
    let highlightedNames = new Set();

    if (hierarchicalData && searchTerm.trim()) {
        const searchVal = searchTerm.trim();
        const pathArray = getPathToNodeByName(hierarchicalData, searchVal, [], false);
        if (pathArray && pathArray.length > 0) {
            highlightedNames = new Set(pathArray);
        }
    }

    return {
        hierarchicalData,
        highlightedNames
    };
}
