conda remove -y -n test_install --all  > /dev/null
conda create -y -n test_install python > /dev/null

source activate test_install > /dev/null 
conda install -y numpy numba ipython-notebook distribute > /dev/null

cd /home/gabriele/workspace/chemview
python setup.py develop

python -c 'import chemview'

conda install -y -c http://conda.binstar.org/gabrielelanaro cclib pyopengl
conda install -y pyqt cython scipy

cd /home/gabriele/workspace/chemlab
python setup.py build_ext --inplace
python setup.py develop

python -c 'import chemlab'

ipython notebook
