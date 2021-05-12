const fetch = require('node-fetch');
const d3 = require('d3');

// TODO: graphql library
// TODO: public key
// TODO: utils.

const key = 'yourkeyhere';

const base_url = 'https://api.data.gov/TEST/10x-imls/v1';

async function queryServer(query) {
  const options = {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
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
            sort: ['fcfs_seq_id'])
    {
      fcfs_seq_id
    }
  }
}
`;
}

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

var el = document.getElementById('libraries');
getAllLibraries().then(results => {
  for (library of results) {
    console.log(library);
    el.insertAdjacentHTML('beforeend', `<li>${library}</li>`);
  }
});

// TODO: select
var library = 'AR0012-004';

function queryLastLibraryData(library) {
  return `
{
  items
  {
    wifi_v1(limit: 1,
            filter: { fcfs_seq_id: { _eq: '${library}' } },
            sort: ['-servertime'])
    {
      device_tag
      session_id
      servertime
    }
  }
}
`;
}

var latest = queryServer(queryLastLibraryData(library));
var item = latest.data.items.wifi_v1[0];
var date = new Date(item.servertime);

// md`${library} last reported:

// - ${date.toISOString().slice(0, 10)} ${date.toISOString().slice(11, 16)}
//   - ${(new Date() - Date.parse(item.servertime))/1000} seconds ago
// - session id: <code>${item.session_id}</code>
// - tag: <code>${item.device_tag}</code>`

function queryLastStartup(library) {
  return `
{
  items
  {
    events_v1(limit: 1,
              filter: { tag: { _eq: 'startup' }, fcfs_seq_id: { _eq: '${library}' } },
              sort: ['servertime'])
    {
      servertime
    }
  }
}
`;
}

var lastStartupEvent = queryServer(queryLastStartup(library));
{
  if (lastStartupEvent.data.items.events_v1.length !== 0) {
    var servertime = lastStartupEvent.data.items.events_v1[0].servertime;
    // return md`The last startup event for ${library} was on ${new Date(servertime).toISOString().slice(0, 10)}`;
  } else {
    // return md`No startup event for ${library} was found.`;
  }
}

// recent activity
const wifi_count = 1000;

function getLibraryData(library) {
  return `
{
  items
  {
    wifi_v1(limit: ${wifi_count},
            filter: { fcfs_seq_id: { _eq: '${library}' } },
            sort: ['servertime'])
    {
      id
      session_id
      event_id
      manufacturer_index
      patron_index
      localtime
    }
  }
}
`;
}
var data = queryServer(getLibraryData(library));
var wifi = data.data.items.wifi_v1;

var seen_devices = (function() {
  var last_seen = -1;
  return wifi.reduce((accum, val) => {
    var id = val.event_id;
    if (last_seen !== id) {
      last_seen = id;
      return [...accum, 1];
    }
    var count = accum[accum.length - 1] + 1;
    return [...accum.slice(0, accum.length - 1), count];
  }, []);
})();

const width = 420;
var x = d3.scaleLinear()
    .domain([0, d3.max(seen_devices)])
    .range([0, width]);
var y = d3.scaleBand()
    .domain(d3.range(seen_devices.length))
    .range([0, 20 * seen_devices.length]);

const svg = d3.create('svg')
      .attr('width', width)
      .attr('height', y.range()[1])
      .attr('font-family', 'sans-serif')
      .attr('font-size', '10')
      .attr('text-anchor', 'end');

const bar = svg.selectAll('g')
    .data(seen_devices)
      .join('g')
      .attr('transform', (d, i) => `translate(0,${y(i)})`);

bar.append('rect')
  .attr('fill', 'steelblue')
  .attr('width', x)
  .attr('height', y.bandwidth() - 1);

bar.append('text')
  .attr('fill', 'white')
  .attr('x', d => x(d) - 3)
  .attr('y', (y.bandwidth() - 1) / 2)
  .attr('dy', '0.35em')
  .text(d => d);

var node = svg.node();
