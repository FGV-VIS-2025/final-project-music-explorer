<script>
    //Shared resource - expanded artists and expanding state
    export let expandedNodes = [];
    export let expanding;
    //Output of the component - node to remove
    export let removeNode;

</script>

<div class="container">
    Artistas atualmente expandidos
    <div id="artist-container">
    {#each expandedNodes as node}
        <div>
            {node.n}
            <button on:click={e => {removeNode = node.id}}>x</button>
        </div>
    {/each}
    </div>
    {#if expanding}
        <p>expandindo agora hein</p>
    {/if}
</div>
<style>
    .container {
        position: fixed;
        bottom: 40px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 1000;

        background-color: var(--accent-black);
        border-radius: 8px;
        border: 3px solid #FF0000;

        padding: 10px;
        box-shadow: 0 2px 10px rgba(256, 256, 256, 0.25);
        width: 90%;
        max-width: 500px;
        box-sizing: border-box;
    }

    * {
        color: white;
    }

    #artist-container {
        display: flex;
        flex-wrap: wrap;
    }

    #artist-container div {
        background-color: #2f05d93a;
        border: 2px solid #2f05d9b6;
        border-radius: 5px;
        margin: 0.5ch;
        padding: 3px;
        font-size: 85%;
    }

</style>
