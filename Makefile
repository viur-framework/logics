
all: \
	logics/parser.py \
	logics-js/parser.js

logics/parser.py: logics.par
	unicc -swo logics/parser -l python $?

logics-js/parser.js: logics.par
	UNICC_TPLDIR=. unicc -swo logics-js/parser -l javascript $?


clean:
	rm logics/parser.py
	rm logics-js/parser.js
