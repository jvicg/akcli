# Makefile to build and host Sphinx documentation
# Generated with `sphinx-quickstart` and adding other functions like `serve` or `autobuild`

SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build
HTMLDIR       = $(BUILDDIR)/html

DEFBUILDER    = html
SERVERPORT    ?= 8080
SERVERCMD     = python -m http.server "$(SERVERPORT)" --directory
AUTOBUILDCMD  = sphinx-autobuild --port "$(SERVERPORT)" --builder "$(DEFBUILDER)"

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

serve: $(DEFBUILDER)
	@$(SERVERCMD) "$(HTMLDIR)"

# Auto re-build if changes are detected. Needs `sphinx-autobuild` to be installed
autobuild:
	@$(AUTOBUILDCMD) "$(SOURCEDIR)" "$(HTMLDIR)"

.PHONY: help serve autobuild Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option. $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
