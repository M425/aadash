<script>
    import JobOut from './JobOut.svelte'
    import Modal from './Modal.svelte';
    import Popup from './Popup.svelte';
    import PopupLong from './PopupLong.svelte';
    import { modal } from './stores.js';
    let searchJobId = '111';
    let selectedJobId = '111';
    let unique = {};
    function inputSearchJobId(event){
        searchJobId = event.target.value;
    }
    function setSearchJobId(event){
        unique = {};
        selectedJobId = searchJobId;
    }
</script>

<main>
    <Modal show={$modal}>
        <div> 
            <label for="searchJobId">ID</label>
            <input type="text" id="searchJobId" value={searchJobId} on:input={inputSearchJobId}/>
            <button on:click={setSearchJobId}>Search</button>
        </div>
        {#if selectedJobId != '-'}
        {#key unique}
            <JobOut jobid="{selectedJobId}"></JobOut>
        {/key}
        {/if}
    </Modal>
</main>

<style>
    main {
        padding: 1em;
        max-width: 240px;
        margin: 0 auto;
    }

    h1 {
        color: #ff3e00;
        text-transform: uppercase;
        font-size: 4em;
        font-weight: 100;
    }

    @media (min-width: 640px) {
        main {
            max-width: none;
        }
    }
</style>