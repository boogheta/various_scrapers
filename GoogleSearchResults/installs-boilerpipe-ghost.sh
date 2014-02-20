#############
# BOILER PY #
#############

source $(which virtualenvwrapper.sh)

workon boilerpy

#BoilerPy
#pip install git+https://github.com/Yomguithereal/BoilerPy.git

#BoilerPipe
unzip python-boilerpipe.zip # TODO : put online
cd python-boilerpipe
unzip jpype.zip
cd JPype-0.5.4.2/
#Get JAVA_HOME
javahome=`which java`; while ls -l "$a" | grep '\->' > /dev/null; do a=$(ls -l $a | sed 's/^.*->\s*//ig'); done; JAVA_HOME=$(echo $a | sed 's#/bin/java$##')
sed "s#/usr/lib/jvm/java-1.5.0-sun-1.5.0.08#$javahome#g" setup.py > setup.py.new
mv setup.py{.new,}
python setup.py build
python setup.py install
cdvirtualenv
sed "s#/usr/lib/jvm/java-1.5.0-sun-1.5.0.08#$javahome#g" lib/python2.7/site-packages/jpype/_linux.py > lib/python2.7/site-packages/jpype/_linux.py.new
mv lib/python2.7/site-packages/jpype/_linux.py{.new,}
cd -
cd ..
python setup.py build
python setup.py install
cd ..

#############
# GHOST PY #
#############

sudo apt-get install cmake qt4-qmake libqt4-dev qt4-dev-tools
pip install python-qt
pip install PySide
# ou via PyQT
# pip install --no-install SIP
# pip install --no-install PyQt
# cd ~/.virtualenvs/myProject/build/SIP
# python configure.py
# make
# sudo make install
# cd ~/.virtualenvs/myProject/build/PyQt
# python configure.py
# make
# make install
pip install git+https://github.com/jeanphix/Ghost.py.git

