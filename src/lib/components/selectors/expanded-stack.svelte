<script>
	//Shared resource - expanded artists and expanding state
	export let expandedNodes = [];
	export let expanding;
	//Output of the component - node to remove
	export let removeNode;

	export let selectedNode = null; //Shared resource with other components
</script>

<div class="container">
	<h4>Artistas expandidos:</h4>
	<div id="artist-container">
		{#each expandedNodes.reverse() as node, index}
			<div
				class="artist-wrapper"
				class:selected={selectedNode
					? node.id === selectedNode.id
					: false}
				on:click={(e) => {
					selectedNode = node;
				}}
			>
				<div class="artist-tag" class:hid={index > 4}>
					{node.n}
				</div>
				<div class="remove-button" class:hid={index > 4}>
					<button
						on:click={(e) => {
							if (!expanding) {
								removeNode = node.id;
							}
						}}
						><img
							src={`icons/close.svg`}
							height="13rem"
							alt="close"
						/></button
					>
				</div>
			</div>
		{/each}
		{#if expandedNodes.length > 5}
			<div class="reticences">...</div>
		{/if}
	</div>
	{#if expanding}
		<!-- <i stlye="font-size: 90%;">Expandindo grafo... Interação bloqueada.</i> -->
	{/if}
</div>

<style>
	h4 {
		margin-bottom: 5px;
	}

	.container {
		position: fixed;
		bottom: 40px;
		left: 40px;
		/* transform: translateX(-50%); */
		z-index: 1000;

		/* background-color: var(--accent-black); */
		/* border-radius: 8px; */
		/* border: 2px solid rgba(100, 100, 100, 0.6); */
		/**/
		/* padding: 10px; */
		/* box-shadow: 0 0px 5px rgba(256, 256, 256, 0.25); */
		width: 90%;
		max-width: 400px;
		/* box-sizing: border-box; */
	}

	* {
		color: white;
	}

	#artist-container {
		display: flex;
		flex-wrap: wrap;
		gap: 4px;
	}

	.artist-wrapper:hover {
		background-color: #eee !important;
		cursor: pointer;
	}

	.artist-wrapper:hover .artist-tag {
		color: black;
	}

	.artist-wrapper:hover img {
		filter: invert(1);
	}

	.artist-wrapper.selected {
		background-color: #eee !important;
	}

	.artist-wrapper.selected img {
		filter: invert(1);
	}

	.artist-wrapper.selected .artist-tag {
		color: black;
		font-weight: bold;
	}

	#artist-container .artist-wrapper {
		background-color: #444;

		display: flex;
		align-items: center;
		justify-content: center;

		border-radius: 4px;
	}

	#artist-container .artist-tag {
		padding: 0 3px 0 1ch;
		font-size: 85%;
	}

	#artist-container .remove-button {
		width: 20px;
		border-radius: 0 4px 4px 0;
	}

	#artist-container .remove-button:hover {
		background-color: red;
	}

	button {
		cursor: pointer;
		border: 0;
		margin: auto;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 4px;
		background-color: transparent;
	}

	.hid {
		display: none;
	}

	#artist-container:hover .hid {
		display: block;
	}
	#artist-container:hover .reticences {
		display: none;
	}
</style>
