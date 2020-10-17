
all: logics/parser.py

logics/parser.py: logics.par
	unicc -swo logics/parser -l python $?

clean:
	rm logics/parser.py
