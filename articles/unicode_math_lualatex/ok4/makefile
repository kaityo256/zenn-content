all: test.pdf

test.pdf:
	pandoc test.md -o test.pdf --pdf-engine=lualatex -V documentclass=ltjarticle -H ./template.tex

clean:
	rm -f test.pdf
