
currentDir=$(pwd)

cd /home/dean/tools/calc/ || exit ;

sudo python setup.py install >> /dev/null 2>&1 ;

cd "$currentDir" || exit ;

python test.py ;
