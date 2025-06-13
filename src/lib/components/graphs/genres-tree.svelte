<script>
    import { onMount } from "svelte";
    import * as d3 from "d3";

    export let data;
    export let highlightedNames = new Set();

    const width = 928;
    const marginTop = 100;
    const marginRight = 40;
    const marginBottom = 100;
    const marginLeft = 100;

    // $: console.log("Render triggered. HighlightedNames:", Array.from(highlightedNames));

    let svgContainer;
    let originalDataRoot;

    let root;
    let treeLayout;
    let diagonal;
    let svg;
    let gLink;
    let gNode;

    let currentData;
    let previousHighlightedNames = new Set();

    const hoverPathColor = "steelblue";
    const hoverPathStrokeWidth = 2.5;
    const hoverNodeRadius = 6;

    function isEmptyData(obj) {
        return !obj || Object.keys(obj).length === 0;
    }

    $: if (data && !isEmptyData(data) && svgContainer) {
        if (currentData !== data) {
            console.log("Data changed. Calling initializeChart.");
            initializeChart();
            currentData = data;
        }
    } else if (isEmptyData(data) && (root || originalDataRoot)) {
        clearChart();
        currentData = null;
    }

    $: if (highlightedNames !== previousHighlightedNames) {
        console.log(
            "HighlightedNames changed. Re-determining root and managing expansion.",
            Array.from(highlightedNames),
        );
        if (originalDataRoot) {
            setDisplayRootAndRender(false);
        }
        previousHighlightedNames = new Set(highlightedNames);
    }

    onMount(() => {
        console.log("Componente CollapsibleTree montado.");
        svg = d3
            .select(svgContainer)
            .attr("width", width)
            .attr("height", 100)
            .attr("viewBox", [-marginLeft, -marginTop, width, 100])
            .attr(
                "style",
                "max-width: 100%; height: auto; font: 10px sans-serif; user-select: none;",
            );

        gLink = svg
            .append("g")
            .attr("fill", "none")
            .attr("stroke", "#555")
            .attr("stroke-opacity", 0.4)
            .attr("stroke-width", 1.5);

        gNode = svg
            .append("g")
            .attr("cursor", "pointer")
            .attr("pointer-events", "all");

        if (data && !isEmptyData(data)) {
            initializeChart();
            currentData = data;
        }
    });

    function clearChart() {
        if (gNode) gNode.selectAll("*").remove();
        if (gLink) gLink.selectAll("*").remove();
        if (svg) {
            svg.attr("height", 0).attr("viewBox", [
                -marginLeft,
                -marginTop,
                width,
                0,
            ]);
        }
        root = null;
        originalDataRoot = null;
        console.log("Chart cleared.");
    }

    function initializeChart() {
        console.log("initializeChart iniciado com dados:", data);
        if (!data || isEmptyData(data)) {
            console.warn("initializeChart chamado sem dados válidos.");
            clearChart();
            return;
        }

        originalDataRoot = d3.hierarchy(data);
        const dx = 20;

        const consistentDy =
            (width - marginRight - marginLeft) / (1 + originalDataRoot.height);

        treeLayout = d3.tree().nodeSize([dx, consistentDy]);
        diagonal = d3
            .linkHorizontal()
            .x((d) => d.y)
            .y((d) => d.x);

        originalDataRoot.x0 = dx / 2;
        originalDataRoot.y0 = 0;

        originalDataRoot.descendants().forEach((d, index) => {
            d.id = `node-${index}`;
            d._children = d.children;
            d.children = null;
        });

        previousHighlightedNames = new Set(highlightedNames);
        setDisplayRootAndRender(true);
    }

    function setDisplayRootAndRender(isInitialCall = false) {
        if (!originalDataRoot) {
            console.warn(
                "setDisplayRootAndRender: originalDataRoot is not available.",
            );
            if (!isEmptyData(data)) {
                console.warn(
                    "Attempting to re-initialize chart due to missing originalDataRoot.",
                );
                initializeChart();
            } else {
                clearChart();
            }
            return;
        }

        let newDisplayRoot = originalDataRoot;

        if (highlightedNames && highlightedNames.size >= 2) {
            const namesArray = Array.from(highlightedNames);
            const targetName = namesArray[1];
            const targetNode = originalDataRoot
                .descendants()
                .find((d) => d.data.name === targetName);

            if (targetNode) {
                newDisplayRoot = targetNode;
            }
        }

        root = newDisplayRoot;
        manageExpansionAndStyles(isInitialCall);
    }

    function applyExpansionLogic() {
        if (!root) return;
        const searchActive = highlightedNames && highlightedNames.size > 0;

        root.each((d) => {
            if (searchActive) {
                if (highlightedNames.has(d.data.name)) {
                    if (d._children && !d.children) {
                        d.children = d._children;
                    }
                }
            } else {
                if (d.depth > 0) {
                    if (d.children) d.children = null;
                } else if (d.depth === 0 && d._children && !d.children) {
                    d.children = d._children;
                }
            }
        });
    }

    function manageExpansionAndStyles(isInitialCall = false) {
        if (!root) {
            console.warn("manageExpansionAndStyles: root is not set.");
            return;
        }
        applyExpansionLogic();
        update(null, root, isInitialCall ? 0 : undefined);
    }

    function setNodeAppearance(selection) {
        selection
            .select("circle")
            .attr("r", 4.5)
            .attr("fill", (d) =>
                highlightedNames.has(d.data.name)
                    ? "orange"
                    : d._children
                      ? "#555"
                      : "var(--accent-black)",
            )
            .attr("stroke", (d) =>
                highlightedNames.has(d.data.name)
                    ? "darkred"
                    : d._children
                      ? "#555"
                      : "#999",
            );

        selection
            .select("text")
            .attr("font-weight", (d) =>
                highlightedNames.has(d.data.name) ? "bold" : "normal",
            );
    }

    function setLinkAppearance(selection) {
        selection
            .attr("stroke", (d_link) =>
                highlightedNames.has(d_link.source.data.name) &&
                highlightedNames.has(d_link.target.data.name)
                    ? "orange"
                    : "#555",
            )
            .attr("stroke-opacity", (d_link) =>
                highlightedNames.has(d_link.source.data.name) &&
                highlightedNames.has(d_link.target.data.name)
                    ? 1
                    : 0.4,
            )
            .attr("stroke-width", (d_link) =>
                highlightedNames.has(d_link.source.data.name) &&
                highlightedNames.has(d_link.target.data.name)
                    ? 2.5
                    : 1.5,
            );
    }

    function handleMouseOverPath(event, hoveredNode) {
        if (!root || !hoveredNode) return;

        const pathNodes = [];
        let current = hoveredNode;
        while (current) {
            pathNodes.unshift(current);
            if (current === root) break;
            current = current.parent;
        }
        // if (!current && hoveredNode !== root) return;

        const pathNodeIds = new Set(pathNodes.map((n) => n.id));

        gNode.selectAll("g.node").each(function (d_node) {
            const nodeSelection = d3.select(this);
            if (pathNodeIds.has(d_node.id)) {
                nodeSelection
                    .select("circle")
                    .attr("fill", hoverPathColor)
                    .attr("stroke", d3.color(hoverPathColor).darker(0.7))
                    .attr("r", hoverNodeRadius);
                nodeSelection.select("text").attr("font-weight", "bold");
            }
        });

        gLink
            .selectAll("path")
            .filter(
                (d_link) =>
                    pathNodeIds.has(d_link.source.id) &&
                    pathNodeIds.has(d_link.target.id),
            )
            .attr("stroke", hoverPathColor)
            .attr("stroke-width", hoverPathStrokeWidth)
            .attr("stroke-opacity", 1);
    }

    function handleMouseOutPath() {
        if (gNode) gNode.selectAll("g.node").call(setNodeAppearance);
        if (gLink) gLink.selectAll("path").call(setLinkAppearance);
    }

    function update(event, source, durationOverride) {
        console.log(
            "update initiated. Source node:",
            source.data ? source.data.name : "N/A (root)",
            "Current display root:",
            root.data ? root.data.name : "N/A",
        );

        const duration =
            durationOverride !== undefined
                ? durationOverride
                : event?.altKey
                  ? 2500
                  : 250;

        treeLayout(root);

        let left = root;
        let right = root;
        root.eachBefore((node) => {
            if (node.x < left.x) left = node;
            if (node.x > right.x) right = node;
        });

        const height = right.x - left.x + marginTop + marginBottom;

        const transition = svg
            .transition()
            .duration(duration)
            .attr("height", Math.max(height, 100))
            .attr("viewBox", [
                -marginLeft,
                left.x - marginTop,
                width,
                Math.max(height, 100),
            ]);

        let nodes = root.descendants().reverse();
        let links = root.links();

        if (root.data && root.data.name === "") {
            nodes = nodes.filter((node) => node !== root);
        }

        if (root.data && root.data.name === "") {
            links = links.filter((link) => link.source !== root);
        }

        const node = gNode.selectAll("g.node").data(nodes, (d) => d.id);

        const nodeEnter = node
            .enter()
            .append("g")
            .attr("class", "node")
            .attr("transform", (d) => `translate(${source.y0},${source.x0})`)
            .attr("fill-opacity", 0)
            .attr("stroke-opacity", 0)
            .on("click", (event, d) => {
                if (d.children) {
                    d.children = null;
                } else if (d._children) {
                    d.children = d._children;
                }
                update(event, d);
            });

        nodeEnter.append("circle").attr("stroke-width", 1.5);

        nodeEnter
            .append("text")
            .attr("dy", "0.31em")
            .attr("x", (d) => (d._children ? -8 : 8))
            .attr("text-anchor", (d) => (d._children ? "end" : "start"))
            .text((d) => d.data.name)
            .attr("fill", "white")
            .attr("font-size", "12px")
            .attr("stroke-linejoin", "round")
            .attr("stroke-width", 4)
            .attr("stroke", "var(--accent-black)")
            .attr("paint-order", "stroke");

        const nodeUpdate = node.merge(nodeEnter);

        nodeUpdate
            .transition(transition)
            .attr("transform", (d) => `translate(${d.y},${d.x})`)
            .attr("fill-opacity", 1)
            .attr("stroke-opacity", 1);

        nodeUpdate.call(setNodeAppearance);

        nodeUpdate
            .on("mouseover.path", (event, d_node) =>
                handleMouseOverPath(event, d_node),
            )
            .on("mouseout.path", handleMouseOutPath);

        node.exit()
            .transition(transition)
            .remove()
            .attr("transform", (d) => `translate(${source.y},${source.x})`)
            .attr("fill-opacity", 0)
            .attr("stroke-opacity", 0);

        const link = gLink.selectAll("path").data(links, (d) => d.target.id);

        const linkEnter = link
            .enter()
            .append("path")
            .attr("d", (d_link) => {
                const o = { x: source.x0, y: source.y0 };
                return diagonal({ source: o, target: o });
            });

        const linkUpdate = link.merge(linkEnter);

        linkUpdate.transition(transition).attr("d", diagonal);

        linkUpdate.call(setLinkAppearance);

        linkUpdate
            .on("mouseover.path", (event, d_link) =>
                handleMouseOverPath(event, d_link.target),
            )
            .on("mouseout.path", handleMouseOutPath);

        link.exit()
            .transition(transition)
            .remove()
            .attr("d", (d_link) => {
                const o = { x: source.x, y: source.y };
                return diagonal({ source: o, target: o });
            });

        root.eachBefore((d) => {
            d.x0 = d.x;
            d.y0 = d.y;
        });
    }
</script>

<div id="svg-wrapper">
    <svg bind:this={svgContainer}></svg>
</div>

<style>
    #svg-wrapper {
        height: 100vh;
        width: 100vw;

        /* border: 3px solid red; */
        box-sizing: border-box;
        overflow-y: auto;
    }
    
    svg {
        display: block;
        min-height: 100%;
        /* border: 3px solid red; */
        box-sizing: border-box;

    }
</style>