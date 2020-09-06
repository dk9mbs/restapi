import unittest

from core.database import CommandBuilderFactory
from core.database import FetchXmlParser
from config import CONFIG
from core.appinfo import AppInfo
from core.permission import Permission

class TestBand(unittest.TestCase):
    def test_band(self):
        #band=frequency_to_band(14.074)
        #print('Frequency => %s Band => %s' % (14.074, band.name))
        #self.assertEqual(band.name, '20m')

        AppInfo.init(__name__, CONFIG['default'])
        session_id=AppInfo.login("root","password")
        context=AppInfo.create_context(session_id)

        print("Read permission")
        self.assertEqual(Permission().validate(context, "read", "guest", "dummy"), True)

        AppInfo.save_context(context, True)
        AppInfo.logoff(context)


if __name__ == '__main__':
    unittest.main()
