
currentDir=$(pwd)

cd /Users/adam/Documents/projects/calc/tests/ || exit ;

python3 setup.py install >> /dev/null 2>&1 ;

cd "$currentDir" || exit ;

python test.py ;
