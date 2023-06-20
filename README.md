# conexED-QA

## chrome driver
https://chromedriver.chromium.org/downloads
put the chrome driver in a PATH directory ie. /usr/local/bin/chromedriver
```
echo $PATH
```
verify chromedriver is in the PATH
```
which chromedriver
```

## install dependencies
```
python3 -m pip install -r requirements.txt
```

## run tests
for html report
```
pytest -s --html=reports/report.html --self-contained-html tests/
```
for allure report
```
pytest -s --alluredir=reports/my_allure_results tests
```
```
allure serve reports/my_allure_results
```
