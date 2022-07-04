<script>
    export let line;
    export let host;
  </script>
  
  <style>
    h1 {
          font-size: 2rem;
          text-align: center;
      }
      
    h2 {
          font-size: 1.25rem;
      }
  </style>
  
  <table>
    <tr> <td>host</td> <td>{host}</td> </tr>
    <tr> <td>role</td> <td>{line.role}</td> </tr>
    <tr> <td>name</td> <td>{line.name}</td> </tr>
    <tr> <td>row</td>  <td>{line.row}</td> </tr>
    <tr> <td>status</td>  <td>{line.hosts[host].status}</td> </tr>
    
    {#each line.hosts[host].res as res}
    <tr> <td>-></td>  <td>{res.out}</td> </tr>
    {/each}
  </table>