
currentDir=$(pwd)

cd /Users/adam/Documents/projects/calc/ || exit 1 ;

python3 setup.py install >> /dev/null 2>&1 ;

cd "$currentDir" || exit 1 ;

python3 test.py ;
