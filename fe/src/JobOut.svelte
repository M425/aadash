<script>
    import { onMount, afterUpdate } from 'svelte';
    import { getContext } from 'svelte';
    import { fly } from 'svelte/transition';

    import PopupLong from './PopupLong.svelte';

    const { open } = getContext('simple-modal');

    export let jobid;
    let hide_all_skipping = false;
    let loading = true;
    let error = false;
    let errorMsg = '';
    let job;
    let section_compact = {};

    async function getJobOut(jobid) {
        let response = await fetch("/api/job/" + jobid);
        console.log(response)
        if (response.status != 200) {
            throw new Error('' + response.statusText);
        } else {
            return await response.json();
        }
    }

    function err(msg) {
        error = true;
        loading = false;
        errorMsg = msg;
        return;
    }

    function section_compact_setall(state) {
        job.sections.forEach(element => {
            section_compact[element] = state;
        });
    }

    const showTaskInfo = (line, host) => {
        console.log('showing task info task', line);
        console.log('showing task info host', host);
        open(PopupLong, { line: line, host: host});
    };

    onMount(() => {
        console.log("Mounting JobOut, jobid:", jobid);
        if(/^([0-9]+)$/.test(jobid)) {
        } else {
            return err('Not a number');
        }
        getJobOut(jobid)
            .then((data) => {
                console.log('resolved', data);
                loading = false;
                job = data.body;
                section_compact_setall(true);
            })
            .catch((data) => {
                console.log(data);
                err(data);
            });
    })
    
    afterUpdate(() => {
    })
</script>


<main>
    {#if loading}
        loading...
    {:else if error}
        ERROR: {errorMsg}
    {:else}
        <h1>Job ID : {jobid} </h1>
        <table
            class="jobout"
            >
            <tr>
                <th style="width: 150px" class="text-verical button bg-grey" on:click="{() => section_compact_setall(true)}">Section</th>
                <th style="width: 100px" class="text-verical">role</th>
                <th style="width: 230px"></th>
                <th style="width: 29px"  class="text-verical button bg-grey" on:click="{() => hide_all_skipping = !hide_all_skipping}">Hide skip</th>
                
                {#each job.allhosts as r}
                    <th style="width: 29px" class="text-verical">{r}</th>
                {/each}
            </tr>
            <tr>
                <td></td>
                <td></td>
                <td class="text-right">changed</td>
                <td></td>

                {#each job.allhosts as r}
                    <td class="{job.playrecap[r].changed != '0' ? 'cell-changed' : ''}">{job.playrecap[r].changed}</td>
                {/each}
            </tr>
            <tr>
                <td></td>
                <td></td>
                <td class="text-right">failed</td>
                <td></td>

                {#each job.allhosts as r}
                    <td class="{job.playrecap[r].failed != '0' ? 'cell-failed' : ''}">{job.playrecap[r].failed}</td>
                {/each}
            </tr>

            {#each job.parsed as line}
            {#if line.new_sect}
            <tr class="row-section">
                <td style="display: none">
                    {line}
                </td>
                <td class="text-no-wrap text-left fg-white button bg-orange{section_compact[line.sect] ? '-dark' : ''}" on:click="{() => section_compact[line.sect] = !section_compact[line.sect]}">{line.sect}</td>
                <td class="text-no-wrap bg-lightgrey"></td>
                <td class="text-no-wrap bg-lightgrey"></td>
                <td></td>
                
                {#each job.allhosts as r}
                    {#if line.hosts[r]}<td class="border-round {line.hosts[r].all_changed ? 'bg-changed' : ''}"></td>
                    {:else}<td class="bg-grey">-</td>
                    {/if}
                {/each}
            </tr>
            {:else}
            <tr class="row-task"
                class:hide_by_allskip={line.all_skipping && hide_all_skipping}
                class:hide_by_compact={section_compact[line.sect]}>
                <td style="display: none">
                    {line.row} - {line.name}
                </td>
                <td class="border-white"></td>
                <td class="text-no-wrap text-left {line.role != '' ? 'bg-lightblue' : ''}">{line.role}</td>
                <td class="text-no-wrap text-left">{line.name}</td>
                <td class="{line.all_skipping ? 'bg-skipping' : ''}"></td>
                
                {#each job.allhosts as r}
                    {#if line.hosts[r]}
                    <td class="bg-{line.hosts[r].status} button" on:click={ () => showTaskInfo(line, r)}></td>
                    {:else}
                    <td class="bg-skipping">-</td>{/if}
                {/each}

            </tr>
            {/if}
            {/each}
        </table>
    {/if}
</main>

<style>
    table {
        border: 0px solid #999;
        table-layout: fixed;
        width: fit-content;
    }
    td,
    th {
        border: 1px solid #aaa;
        overflow: hidden;
    }
    td {
        height: 29px;
    }

    tr.hide_by_compact {
        display: none;
    }
    tr.hide_by_allskip {
        display: none;
    }

    .label {
        background: white;
        border-radius: 3px 3px 3px 3px;
        display: inline-block;
        margin: 1px 2px;
        padding: 0px 4px;
    }

    .bg-orange      { background: rgb(218, 136, 27) }
    .bg-orange-dark { background: rgb(169, 108, 29) }
    .bg-lightblue   { background: rgb(212, 255, 253) }
    .bg-lightgrey   { background: rgb(238, 240, 240) }
    .bg-grey        { background: rgb(186, 186, 186) }
    .bg-changed     { background: rgb(255, 208, 0)  }
    .bg-skipping    { background: rgb(215, 218, 232)  }
    .bg-ok          { background: rgb(0, 255, 34)    }
    .bg-failed      { background: rgb(255, 76, 67)    }
    .fg-white       { color: white }
    
    .text-no-wrap { white-space: nowrap       }
    .text-left    { text-align: left          }
    .text-right   { text-align: right         }
    .text-verical { writing-mode: vertical-lr }
    
    .button       { cursor: pointer }
    .button:hover { opacity: 0.5 }

    .border-round { border-radius: 50% }
    .border-white { border-color: white }
</style>