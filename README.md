# Getting started

```
npm install
```

Live reload is also supported.

```
# (in a terminal)
make js
# (in another terminal)
make html
```

## Authorization

The `utils.js` file must be configured with the appropriate api.data.gov key.

## API Key

Create a (git ignored) `key.js`:

```
const api_key = "YOURKEYHERE"

module.exports = {
    api_key
  };
```