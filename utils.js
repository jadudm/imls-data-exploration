const { api_key } = require('./key.js');

const base_url = 'https://api.data.gov/TEST/10x-imls/v1';

async function queryServer(query) {
  const options = {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ query })
  };
  var result = await fetch(`${base_url}/graphql/?api_key=${api_key}`, options);
  return result.json();
}

module.exports = {
  queryServer
};
