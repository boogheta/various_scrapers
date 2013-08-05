#############
# BOILER PY #
#############

v.mk boilerpy

#BoilerPy
#pip install git+https://github.com/Yomguithereal/BoilerPy.git

#BoilerPipe
unzip python-boilerpipe.zip # TODO : put online
cd python-boilerpipe
unzip jpype.zip
cd JPype-0.5.4.2/
#Get JAVA_HOME
a=`which java`; while ls -l "$a" | grep '\->' > /dev/null; do a=$(ls -l $a | sed 's/^.*->\s*//ig'); done; JAVA_HOME=$(echo $a | sed 's#/bin/java$##')
#sudo echo "JAVA_HOME=$JAVA_HOME" >> /etc/environment
vim setup.pyi +47 # set JAVA_HOME properly
python setup.py build
python setup.py install
vim $PYENVS/boilerpy/lib/python2.7/site-packages/jpype/_linux.py +53 # set JAVA_HOME properly
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

