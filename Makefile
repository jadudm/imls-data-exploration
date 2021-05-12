deps:
	npm install

js:
	./node_modules/watchify/bin/cmd.js -v visualization.js -o bundle.js

html:
	./node_modules/live-server/live-server.js
