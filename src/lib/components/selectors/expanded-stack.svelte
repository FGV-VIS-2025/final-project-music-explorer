<script>
    //Shared resource - expanded artists and expanding state
    export let expandedNodes = [];
    export let expanding;
    //Output of the component - node to remove
    export let removeNode;

</script>

<div class="container">
    <h3>Artistas atualmente expandidos</h3>
    <div id="artist-container">
    {#each expandedNodes as node, index}
        <div class:hid={index > 4}>
            {node.n}
            <button on:click={e => {
                if(!expanding){
                    removeNode = node.id
                }
            }}><img src={`icons/close.svg`} height="13rem" alt="close"></button>
        </div>
    {/each}
    {#if expandedNodes.length > 5}
        <div class="reticences">...</div>
    {/if}
    </div>
    {#if expanding}
        <i stlye="font-size: 90%;">Expandindo grafo... Interação bloqueada.</i>
    {/if}
</div>
<style>
    h3 {
        margin: auto;
        text-align: center;
    }

    .container {
        position: fixed;
        bottom: 40px;
        left: 40px;
        /* transform: translateX(-50%); */
        z-index: 1000;

        background-color: var(--accent-black);
        border-radius: 8px;
        border: 2px solid rgba(100, 100, 100, 0.6);

        padding: 10px;
        box-shadow: 0 0px 5px rgba(256, 256, 256, 0.25);
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

    button {
        cursor: pointer;
        border: 0px;
        padding: 2px;
        margin: auto;
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
