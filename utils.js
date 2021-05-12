
const base_url = 'https://api.data.gov/TEST/10x-imls/v1';

// TODO: public key
const key = 'yourkeyhere';

async function queryServer(query) {
  const options = {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ query })
  };
  var result = await fetch(`${base_url}/graphql/?api_key=${key}`, options);
  return result.json();
}

module.exports = {
  queryServer
};
