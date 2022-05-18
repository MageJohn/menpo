import sys

from setuptools import find_packages, setup


def get_version_and_cmdclass(package_path):
    """Load version.py module without importing the whole package.

    Template code from miniver
    """
    import os
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("version", os.path.join(package_path, "_version.py"))
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.__version__, module.cmdclass


version, cmdclass = get_version_and_cmdclass("menpo")
def build_extension_from_pyx(pyx_path, extra_sources_paths=None):
    if extra_sources_paths is None:
        extra_sources_paths = []
    extra_sources_paths.insert(0, pyx_path)
    ext = Extension(name=pyx_path[:-4].replace('/', '.'),
                    sources=extra_sources_paths,
                    include_dirs=[NUMPY_INC_PATH],
                    language='c++')
    if IS_LINUX or IS_OSX:
        ext.extra_compile_args.append('-Wno-unused-function')
    if IS_OSX:
        ext.extra_link_args.append('-headerpad_max_install_names')
    return ext


try:
    from Cython.Build import cythonize
except ImportError:
    import warnings

    cythonize = no_cythonize
    warnings.warn('Unable to import Cython - attempting to build using the '
                  'pre-compiled C++ files.')

cython_modules = [
    build_extension_from_pyx('menpo/external/skimage/_warps_cy.pyx'),
    build_extension_from_pyx(
        'menpo/feature/windowiterator.pyx',
        extra_sources_paths=['menpo/feature/cpp/ImageWindowIterator.cpp',
                             'menpo/feature/cpp/WindowFeature.cpp',
                             'menpo/feature/cpp/HOG.cpp',
                             'menpo/feature/cpp/LBP.cpp']),
    build_extension_from_pyx('menpo/image/patches.pyx')
]
cython_exts = cythonize(cython_modules, quiet=True,
                        language_level=sys.version_info[0])

# Please see conda/meta.yaml for other binary dependencies
install_requires = ["numpy>=1.14", "scipy>=1.0", "matplotlib>=3.0", "pillow>=4.0"]


setup(
    name="menpo",
    version=version,
    cmdclass=cmdclass,
    description="A Python toolkit for handling annotated data",
    author="The Menpo Team",
    author_email="hello@menpo.org",
    packages=find_packages(),
    install_requires=install_requires,
    package_data={"menpo": ["data/*"]},
    tests_require=["pytest>=6.0", "pytest-mock>=3.0", "black>=20.0"],
)
