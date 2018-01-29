
all: parser.py

parser.py: logics.par
	unicc -swo parser -l python $?

clean:
	rm -f parser.py
