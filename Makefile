
LOGICS_PY=logics-py/logics/parser.py
LOGICS_JS=logics-js/parser.js

all: \
	$(LOGICS_PY) \
	$(LOGICS_JS)

$(LOGICS_PY): logics.par
	unicc -swo $(patsubst %.py,%,$@) -l python $?

$(LOGICS_JS): logics.par
	UNICC_TPLDIR=. unicc -swo $(patsubst %.js,%,$@) -l javascript $?

clean:
	rm $(LOGICS_JS) $(LOGICS_PY)
