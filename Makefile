deps:
	npm install

js:
	./node_modules/watchify/bin/cmd.js visualization.js -o bundle.js

html:
	./node_modules/live-server/live-server.js
