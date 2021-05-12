const { queryServer } = require('./utils.js');

// TODO: select
var library = 'AR0012-004';

// development/prod?

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
