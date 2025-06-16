<script>
	import * as d3 from "d3";
	export let data = {};

	let dims = {
		width: 600,
		height: 300,
		left: 40,
		bottom: 30,
		right: 40,
		top: 40,
	};

	$: width = dims.width;
	$: height = dims.height;

	let parsedData = [];

	let svgElement;
	let zoom;
	let zoomTransform = d3.zoomIdentity;

	$: {
		const years = Object.keys(data)
			.filter((y) => y !== "" && !isNaN(+y))
			.map(Number);
		const minYear = Math.min(...years);
		const maxYear = Math.max(...years);
		parsedData = [];
		for (let y = minYear; y <= maxYear; y++) {
			parsedData.push({
				year: y,
				count: data[y] || 0,
			});
		}
	}

	let originalXScale, xScale, yScale;
	let visibleData = [];
	let barWidth = 0;

	$: {
		if (parsedData.length === 0) {
			pass;
		}

		const years = parsedData.map((d) => d.year);
		const minYear = d3.min(years);
		const maxYear = d3.max(years);

		originalXScale = d3
			.scaleLinear()
			.domain([minYear - 0.5, maxYear + 0.5])
			.range([dims.left, width - dims.right]);

		xScale = zoomTransform.rescaleX(originalXScale);

		const totalYears = maxYear - minYear + 1;
		barWidth =
			((width - dims.left - dims.right) / totalYears) * zoomTransform.k;

		const [x0, x1] = xScale.domain();
		visibleData = parsedData.filter((d) => d.year >= x0 && d.year <= x1);

		const maxVisibleY =
			visibleData.length > 0 ? d3.max(visibleData, (d) => d.count) : 0;
		yScale = d3
			.scaleLinear()
			.domain([0, maxVisibleY])
			.range([height - dims.bottom, dims.top]);
	}

	let xAxis, yAxis;
	$: {
		if (xAxis && xScale && parsedData.length > 0) {
			d3.select(xAxis).call(
				d3.axisBottom(xScale).tickFormat(d3.format("d")),
			);
		}
		if (yAxis && yScale) {
			d3.select(yAxis).call(
				d3.axisRight(yScale).ticks(5).tickFormat(d3.format("d")),
			);
		}
	}

	$: if (svgElement && parsedData.length > 0) {
		zoom = d3
			.zoom()
			.scaleExtent([1, 10])
			.extent([
				[dims.left, dims.top],
				[width - dims.right, height - dims.bottom],
			])
			.translateExtent([
				[dims.left, dims.top],
				[width - dims.right, height - dims.bottom],
			])
			.on("zoom", (event) => {
				zoomTransform = event.transform;
			});

		d3.select(svgElement).call(zoom);
	}
</script>

<svg bind:this={svgElement} {width} {height} viewBox="0 0 {width} {height}">
	<g transform="translate(0, {height - dims.bottom})" bind:this={xAxis}>
		<text
			x={width / 2}
			y={dims.bottom - 4}
			fill="currentColor"
			text-anchor="middle"
		>
			Ano
		</text>
	</g>
	<g id="bars" fill="#FFF">
		{#each parsedData as d}
			{@const xPos = xScale(d.year)}
			{@const halfBarWidth = barWidth / 2}
			<rect
				x={xPos - halfBarWidth}
				y={yScale(d.count)}
				opacity={0.7}
				width={Math.max(1, barWidth)}
				height={yScale(0) - yScale(d.count)}
			/>
		{/each}
	</g>
	<g fill="var(--accent-black)">
		<rect
			x={0}
			y={0}
			width={dims.left}
			height={dims.height - dims.bottom}
		/>
		<rect
			x={0}
			y={0}
			width={dims.width}
			height={dims.top}
		/>
		<rect
			x={dims.width - dims.right}
			y={0}
			width={dims.right}
			height={dims.height - dims.bottom}
		/>
	</g>

	<g transform="translate({width - dims.left}, 0)" bind:this={yAxis}></g>

	<rect
		x={dims.left}
		y={dims.top}
		width={width - dims.left - dims.right}
		height={height - dims.top - dims.bottom}
		fill="transparent"
		style="cursor: grab;"
	/>
</svg>
