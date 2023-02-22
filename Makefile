# git automated message
# use and add date and time to the message
# include the date in the message and write automated git
message = automated git @ $(shell date)

# make automated git
# pass a customized argument to the make command
# include the date and time into the message
.PHONY: git-automated
git-automated:
	# remove the .idea folder
	# remember that another option is to add it to the
	# .gitignore file so it is not include in the git
	git add .
	git commit -m "$(message)"
	git push

# install requirements.txt
.PHONY: install-requirements
install-requirements:
	# install the requirements.txt
	pip install -r requirements.txt
	pip install -r requirements-test.txt

# run the flake8 script on all python files in the src folder
.PHONY: run-flake8
run-flake8:
	isort src/*.py
	isort test/*.py
	flake8 src/*.py
	flake8 test/*.py

# run black on all python files in the src folder
.PHONY: run-black
run-black:
	black src/*.py
	black test/*.py