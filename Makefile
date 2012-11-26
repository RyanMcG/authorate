DOCS_BRANCH=docs
SEPARATOR="=========================================================="
ECHO=@/usr/bin/env echo -e

.PHONY: docs clean

# Default task is to run tasks
test:
	$(ECHO) ${SEPARATOR}
	$(ECHO) "Running doctest. . ."
	$(ECHO) ${SEPARATOR}
	python -m doctest authorate.py

docs:
	$(ECHO) ${SEPARATOR}
	$(ECHO) "Generating Documentation. . ."
	$(ECHO) ${SEPARATOR}
	pycco *.py

# Copy generated docs DOCS_BRANCH branch
prepare_docs: docs
	$(ECHO) ${SEPARATOR}
	$(ECHO) "Preparing docs in ${DOCS_BRANCH} branch. . ."
	$(ECHO) ${SEPARATOR}
	@-mkdir -p .git/_deploy/
	rm -rf .git/_deploy/*
	cp docs/* .git/_deploy/
	@-git stash
	git checkout ${DOCS_BRANCH}
	cp .git/_deploy/* .
	git add *.html *.css
	-git commit -am "Update documentation."
	@git checkout - > /dev/null
	@-git stash pop
	$(ECHO)

# Deploy prepared documents
deploy_docs: prepare_docs
	$(ECHO) ${SEPARATOR}
	$(ECHO) "Attempting deployment to origin's ${DOCS_BRANCH} branch."
	$(ECHO) ${SEPARATOR}
	git push -u origin ${DOCS_BRANCH}:${DOCS_BRANCH}


init_docs:
	$(ECHO)
	$(ECHO) ${SEPARATOR}
	$(ECHO) "Initializing orphan ${DOCS_BRANCH} branch. . ."
	$(ECHO) ${SEPARATOR}
	-git stash
	git checkout --orphan ${DOCS_BRANCH}
	-git rm -rf .
	echo "*" > .gitignore
	$(ECHO)
	$(ECHO) "\tAttempting an initial commit. . ."
	$(ECHO)
	-git commit -m "Initial commit."
	git checkout -
	-git stash pop

clean:
	rm -rf __pycache__ *.pyc .ropeproject docs/*

rmdb:
	rm -f *.db
