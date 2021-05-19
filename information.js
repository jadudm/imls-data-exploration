const { queryServer } = require('./utils.js');

function queryLastLibraryWifi(library) {
  return `
{
  items {
    wifi_v1(limit: 1,
            filter: { fcfs_seq_id: { _eq: "${library}" } },
            sort: ["-servertime"]) {
      device_tag
      session_id
      servertime
    }
  }
}
`;
}

function queryLastStartup(library) {
  return `
{
  items {
    events_v1(limit: 1,
              filter: { tag: { _eq: "startup" }, fcfs_seq_id: { _eq: "${library}" } },
              sort: ["-servertime"]) {
      servertime
    }
  }
}
`;
}

function isDevelopment(library) {
  return library.startsWith('CA') || library.startsWith('ME') || library.startsWith('JA');
}

function timeElapsed(when) {
  var diff = (new Date() - Date.parse(when))/1000; // milliseconds
  if (diff < 60) {
    return 'a minute ago';
  } else {
    diff /= 60;
    if (diff < 60) {
      const x = Math.trunc(diff);
      return `${x} minute${x == 1 ? '' : 's'} ago`;
    } else {
      diff /= 60;
      if (diff < 24) {
        const x = Math.trunc(diff);
        return `${x} hour${x == 1 ? '' : 's'} ago`;
      } else {
        diff /= 24;
        const x = Math.trunc(diff);
        return `${x} day${x == 1 ? '' : 's'} ago`;
      }
    }
  }
}

async function displayLibraryInformation(library) {
  var el = document.getElementById('library-information');
  el.innerText = 'Querying...';

  const latest = await queryServer(queryLastLibraryWifi(library));
  const [item] = latest.data.items.wifi_v1;
  const date = new Date(item.servertime);

  var div = document.createElement('div');
  div.id = 'library-information';

  var p1 = document.createElement('p');
  p1.innerText = `Last reported: ${timeElapsed(date)}`;
  div.appendChild(p1);

  const lastStartup = await queryServer(queryLastStartup(library));
  const [startup] = lastStartup.data.items.events_v1;
  var p2 = document.createElement('p');
  p2.innerText = startup ? `Started up: ${timeElapsed(startup.servertime)}` : 'No startup event was found.';
  div.appendChild(p2);

  var p3 = document.createElement('p');
  p3.innerText = `(This is a ${isDevelopment(library) ? 'development' : 'production'} device.)`;
  div.appendChild(p3);

  el.parentNode.replaceChild(div, el);
}

module.exports = {
  displayLibraryInformation
};
