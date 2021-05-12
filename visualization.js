const fetch = require("node-fetch");

// TODO: public key
const key = 'yourkeyhere';

const base_url = 'https://api.data.gov/TEST/10x-imls/v1';

async function queryServer(query) {
  const options = {
    method: 'POST',
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ query })
  };
  var result = await fetch(`${base_url}/graphql/?api_key=${key}`, options);
  return result.json();
}

function queryUniqueLibrary(known) {
  return `
{
  items
  {
    wifi_v1(limit: 1,
            filter: { fcfs_seq_id: { _nin: ${JSON.stringify(known)} } },
            sort: ["fcfs_seq_id"])
    {
      fcfs_seq_id
    }
  }
}
`;
}

async function getAllLibraries() {
  // get library ids one by one, since directus does not have any way
  // to get unique values (that I know of).
  var known_fcfs = [];
  var result = await queryServer(queryUniqueLibrary(known_fcfs));
  while (result.data && result.data.items.wifi_v1.length) {
    var fcfs = result.data.items.wifi_v1[0].fcfs_seq_id;
    known_fcfs.push(fcfs);
    result = await queryServer(queryUniqueLibrary(known_fcfs));
  }
  return known_fcfs;
}

var libraries = await getAllLibraries();
console.log(libraries);

// TODO: select
