# set the package name
package_name = package

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
	pip install --upgrade pip
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

# run the pytest script
.PHONY: run-pytest
run-pytest:
	pytest test/test_*.py

# run code coverage and exclude p01_1_make_dummy_data.py and p01_2_make_dummy_data.py
.PHONY: run-coverage
run-coverage:
	coverage run -m --source=src --omit="src/p01_1_make_dummy_data.py","src/p01_2_make_dummy_data.py","src/mongoDB_prac.py","src/s3.py" pytest test/*.py
	coverage report -m
	coverage html

# open html report in browser chrome
.PHONY: open-html
open-html:
	open -a "Google Chrome" htmlcov/index.html

# run the following commands consecutively
# black, flake8, pytest, git-automated
.PHONY: run-all
run-all:
	make run-black
	make run-flake8
	#make run-pytest
	make run-coverage
	make git-automated

# zip the src folder, lambda_function.py and requirements.txt and use the package name
.PHONY: zip
zip:
	zip -r $(package_name).zip src/* -x "src/s3.py" "src/p01_1_make_dummy_data.py" \
	"src/p01_2_make_dummy_data.py" "src/mongoDB_prac.py" lambda_function.py requirments.txt


# print environment variables
.PHONY: print-env
print-env:
	printenv

# reset path variables
#.PHONY: reset-path
#reset-path:
#	export PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
#   export PATH=$PATH:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin

# run the app using uvicorn
.PHONY: run-app
run-app:
	uvicorn main:app --reload --port 8080

# stop the port 8000
.PHONY: stop-port
	stop-port: sudo lsof -t -i tcp:8000 | xargs kill -9

# make pytest coverage
.PHONY: run-pytest-coverage
run-pytest-coverage:
	pytest --cov=src --cov-report=html test/test_*.py

# show the coverage report
.PHONY: show-coverage
show-coverage:
	open htmlcov/index.html