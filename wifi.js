const d3 = require('d3');
const { queryServer } = require('./utils.js');

const wifi_count = 1000;

// TODO: wifi minutes count
// TODO: filter out devices (less than 10 minutes, ...)

function getSessionData(library, session, page) {
  return `
{
  items {
    wifi_v1(limit: ${wifi_count},
            page: ${page},
            filter: { fcfs_seq_id: { _eq: "${library}" },
                      session_id: { _eq: "${session}" } },
            sort: ["servertime"]) {
      id
      session_id
      event_id
      manufacturer_index
      patron_index
      localtime
      servertime
    }
  }
}
`;
}

function getSessionStart(library, session) {
  return `
{
  items {
    wifi_v1(limit: 1,
            filter: { fcfs_seq_id: { _eq: "${library}" },
                      session_id: { _eq: "${session}" } },
            sort: ["servertime"]) {
      servertime
    }
  }
}
`;
}

function getCurrentSession(library) {
  return `
{
  items {
    wifi_v1(limit: 1,
            filter: { fcfs_seq_id: { _eq: "${library}" } },
            sort: ["-servertime"]) {
      session_id
      servertime
    }
  }
}
`;
}

async function chartLibraryInformation(library) {
  var el = document.getElementById('library-chart');
  el.innerHTML = '';

  var currentSessionData = await queryServer(getCurrentSession(library));
  const currentSession = currentSessionData.data.items.wifi_v1[0].session_id;
  const endDate = currentSessionData.data.items.wifi_v1[0].servertime;

  var startSession = await queryServer(getSessionStart(library, currentSession));
  const startDate = startSession.data.items.wifi_v1[0].servertime;

  var p = document.createElement('p');
  p.innerHTML = `Displaying data for current session: <code>${currentSession}</code>, from ${startDate} to ${endDate}`;
  el.appendChild(p);

  var page = 1;
  var data = await queryServer(getSessionData(library, currentSession, page));
  var wifi = data.data.items.wifi_v1.slice(); // make a copy of the data

  while (data.data.items.wifi_v1.length !== 0) {
    page += 1;
    data = await queryServer(getSessionData(library, currentSession, page));
    wifi = Array.prototype.concat(wifi, data.data.items.wifi_v1.slice());
  }

  var last_seen = -1;
  const seen_devices = wifi.reduce((accum, val) => {
    var id = val.event_id;
    if (last_seen !== id) {
      last_seen = id;
      return [...accum, 1];
    }
    var count = accum[accum.length - 1] + 1;
    return [...accum.slice(0, accum.length - 1), count];
  }, []);

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

  el.appendChild(svg.node());
}

module.exports = {
  chartLibraryInformation
};
