const fetch = require('node-fetch');
const d3 = require('d3');
const { queryServer } = require('./utils.js');

// known FCFS as of the time of this writing. we'll query for any
// extra ones we don't know about.
var known_fcfs = [
  'AR0012-004',
  'CA0001-001',
  'CA0001-002',
  'CA0001-004',
  'CA0001-005',
  'CA0001-999',
  'CA9999-999',
  'GA0014-002',
  'GA0027-004',
  'GA0058-003',
  'JA1234-123',
  'KY0069-002',
  'KY0069-003',
  'MA0352-002',
  'ME0064-001',
  'ME0064-002',
  'ME0064-003',
  'ME0064-004',
  'ME1011-137',
];

function queryUniqueLibrary(known) {
  return `
{
  items
  {
    wifi_v1(limit: 1,
            filter: { fcfs_seq_id: { _nin: ${JSON.stringify(known)} } },
            sort: ['fcfs_seq_id'])
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
  var result = await queryServer(queryUniqueLibrary(known_fcfs));
  while (result.data && result.data.items.wifi_v1.length) {
    var fcfs = result.data.items.wifi_v1[0].fcfs_seq_id;
    known_fcfs.push(fcfs);
    result = await queryServer(queryUniqueLibrary(known_fcfs));
  }
  return known_fcfs;
}

document.body.onload = () => {
  var el = document.getElementById('libraries');
  getAllLibraries().then(results => {
    for (var library of results) {
      el.insertAdjacentHTML('beforeend', `<li>${library}</li>`);
    }
  });
};
