const d3 = require('d3');
const { queryServer } = require('./utils.js');

const wifi_count = 1000;

function getWifiData(library) {
  return `
{
  items {
    wifi_v1(limit: ${wifi_count},
            filter: { fcfs_seq_id: { _eq: "${library}" } },
            sort: ["servertime"]) {
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

async function chartLibraryInformation(library) {
  var el = document.getElementById('library-chart');
  el.innerHTML = '';

  var data = await queryServer(getWifiData(library));
  var wifi = data.data.items.wifi_v1;

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
