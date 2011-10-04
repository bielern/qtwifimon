from distutils.core import setup
import wifimon

setup(
        name="wifimon",
        description="Qt monitor for your wireless net",
        long_decription=wifimon.__doc__,
        version=wifimon.__version__,
        author=wifimon.__author__,
        license=wifimon.__license__,
        url="github",
        scripts=['scripts/wifimon'],
        packages=['wifimon'],
        package_data={'wifimon': ['img/*.svg', 'default_config']}
        #data_files=[('share/wifimon', ['img/*.svg']),
        #           ('share/wifimon', ['default_config'])]
        )


