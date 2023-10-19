
LOGICS_PY=logics-py/logics/parser.py
LOGICS_JS=logics-js/parser.js

all: \
	$(LOGICS_PY) \
	$(LOGICS_JS)

$(LOGICS_PY): logics.par
	unicc -swo $(patsubst %.py,%,$@) -l python $?
	cd logics-py; pipenv install --dev; pipenv run fmt

$(LOGICS_JS): logics.par
	unicc -swo $(patsubst %.js,%,$@) -l javascript $?
	cd logics-js; npm i; npm run fmt

clean:
	rm $(LOGICS_JS) $(LOGICS_PY)
