all: test.pdf

test.pdf:
	pandoc test.md -o test.pdf --pdf-engine=lualatex -V documentclass=ltjarticle

clean:
	rm -f test.pdf
