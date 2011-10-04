from distutils.core import setup
import qtwifimon

setup(
        name="qtwifimon",
        description="Qt monitor for your wireless net",
        long_description=qtwifimon.__doc__,
        version=qtwifimon.__version__,
        author=qtwifimon.__author__,
        license=qtwifimon.__license__,
        url="http://github.com/bielern/qtwifimon",
        scripts=['scripts/qtwifimon'],
        packages=['qtwifimon'],
        package_data={'qtwifimon': ['img/*.svg', 'default_config']}
)


