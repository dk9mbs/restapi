import unittest

from core.database import CommandBuilderFactory
#from core.database import FetchXmlParser
from config import CONFIG
from core.appinfo import AppInfo
#from core.plugin import Plugin
from core.xml_reader import XmlReader

class TestPluginExecution(unittest.TestCase):
    def setUp(self):
        AppInfo.init(__name__, CONFIG['default'])
        session_id=AppInfo.login("root","password")
        self.context=AppInfo.create_context(session_id)

    def test_execution(self):
        context=self.context

        xml=f'''<?xml version="1.0" encoding="UTF-8"?>
        <DELVRY01 xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:fn="http://www.w3.org/2005/xpath-functions" xmlns:xdt="http://www.w3.org/2005/02/xpath-datatypes">
        <IDOC BEGIN="1">
            <EDI_DC40 SEGMENT="1">
            <TABNAM>EDI_DC40</TABNAM>
            <MANDT>100</MANDT>
            <DOCREL>740</DOCREL>
            <DIRECT>2</DIRECT>
            <IDOCTYP>DELVRY01</IDOCTYP>
            <MESTYP>SHPCON</MESTYP>
            <SNDPOR>MX</SNDPOR>
            <SNDPRT>LS</SNDPRT>
            <SNDPFC>LS</SNDPFC>
            <SNDPRN>MX</SNDPRN>
            <RCVPOR>SAP1</RCVPOR>
            <RCVPRT>LS</RCVPRT>
            <RCVPFC>LS</RCVPFC>
            <RCVPRN>P100</RCVPRN>
            <CREDAT>20230609</CREDAT>
            <CRETIM>143000</CRETIM>
            </EDI_DC40>
            <E1EDL20 SEGMENT="1">
            <VBELN>0012724677</VBELN>
            <BTGEW>99</BTGEW>
            <NTGEW>78.096</NTGEW>
            <GEWEI>KGM</GEWEI>
            <E1EDL22 SEGMENT="1" />
            <E1EDL18 SEGMENT="1">
                <QUALF>PIC</QUALF>
            </E1EDL18>
            <E1EDL18 SEGMENT="1">
                <QUALF>NWT</QUALF>
            </E1EDL18>
            <E1EDL18 SEGMENT="1">
                <QUALF>GWT</QUALF>
            </E1EDL18>
            <E1EDT13 SEGMENT="1">
                <QUALF>010</QUALF>
                <ISDD>20230612</ISDD>
                <ISDZ>000000</ISDZ>
            </E1EDT13>
            <E1EDL24 SEGMENT="1">
                <POSNR>000010</POSNR>
                <MATNR>0000000000X001</MATNR>
                <WERKS>51</WERKS>
                <LGORT>0100</LGORT>
                <CHARG>23456789</CHARG>
                <LFIMG>300</LFIMG>
                <VRKME>UN</VRKME>
                <NTGEW>75.000</NTGEW>
                <BRGEW>75.000</BRGEW>
                <GEWEI>KGM</GEWEI>
                <VFDAT>20250404</VFDAT>
                <E1EDL19 SEGMENT="1">
                <QUALF>NWT</QUALF>
                </E1EDL19>
                <E1EDL19 SEGMENT="1">
                <QUALF>GWT</QUALF>
                </E1EDL19>
                <E1EDL19 SEGMENT="1">
                <QUALF>CHG</QUALF>
                </E1EDL19>
                <E1EDL19 SEGMENT="1">
                <QUALF>VDT</QUALF>
                </E1EDL19>
            </E1EDL24>
            <E1EDL24 SEGMENT="1">
                <POSNR>000020</POSNR>
                <MATNR>000000000000X002</MATNR>
                <WERKS>51</WERKS>
                <LGORT>0100</LGORT>
                <CHARG>1234567</CHARG>
                <LFIMG>24</LFIMG>
                <VRKME>UN</VRKME>
                <NTGEW>3.096</NTGEW>
                <BRGEW>3.096</BRGEW>
                <GEWEI>KGM</GEWEI>
                <VFDAT>20250302</VFDAT>
                <E1EDL19 SEGMENT="1">
                <QUALF>NWT</QUALF>
                </E1EDL19>
                <E1EDL19 SEGMENT="1">
                <QUALF>GWT</QUALF>
                </E1EDL19>
                <E1EDL19 SEGMENT="1">
                <QUALF>CHG</QUALF>
                </E1EDL19>
                <E1EDL19 SEGMENT="1">
                <QUALF>VDT</QUALF>
                </E1EDL19>
            </E1EDL24>
            </E1EDL20>
        </IDOC>
        <IDOC BEGIN="1">
            <EDI_DC40 SEGMENT="1">
            <TABNAM>EDI_DC40</TABNAM>
            <MANDT>100</MANDT>
            <DOCREL>740</DOCREL>
            <DIRECT>2</DIRECT>
            <IDOCTYP>DELVRY01</IDOCTYP>
            <MESTYP>SHPCON</MESTYP>
            <SNDPOR>MX</SNDPOR>
            <SNDPRT>LS</SNDPRT>
            <SNDPFC>LS</SNDPFC>
            <SNDPRN>MX</SNDPRN>
            <RCVPOR>SAP1</RCVPOR>
            <RCVPRT>LS</RCVPRT>
            <RCVPFC>LS</RCVPFC>
            <RCVPRN>P100</RCVPRN>
            <CREDAT>20230609</CREDAT>
            <CRETIM>143000</CRETIM>
            </EDI_DC40>
            <E1EDL20 SEGMENT="1">
            <VBELN>0012724678</VBELN>
            <BTGEW>99</BTGEW>
            <NTGEW>78.096</NTGEW>
            <GEWEI>KGM</GEWEI>
            <E1EDL22 SEGMENT="1" />
            <E1EDL18 SEGMENT="1">
                <QUALF>PIC</QUALF>
            </E1EDL18>
            <E1EDL18 SEGMENT="1">
                <QUALF>NWT</QUALF>
            </E1EDL18>
            <E1EDL18 SEGMENT="1">
                <QUALF>GWT</QUALF>
            </E1EDL18>
            <E1EDT13 SEGMENT="1">
                <QUALF>010</QUALF>
                <ISDD>20230612</ISDD>
                <ISDZ>000000</ISDZ>
            </E1EDT13>
            <E1EDL24 SEGMENT="1">
                <POSNR>000010</POSNR>
                <MATNR>0000000000X001</MATNR>
                <WERKS>51</WERKS>
                <LGORT>0100</LGORT>
                <CHARG>23456789</CHARG>
                <LFIMG>300</LFIMG>
                <VRKME>UN</VRKME>
                <NTGEW>75.000</NTGEW>
                <BRGEW>75.000</BRGEW>
                <GEWEI>KGM</GEWEI>
                <VFDAT>20250404</VFDAT>
                <E1EDL19 SEGMENT="1">
                <QUALF>NWT</QUALF>
                </E1EDL19>
                <E1EDL19 SEGMENT="1">
                <QUALF>GWT</QUALF>
                </E1EDL19>
                <E1EDL19 SEGMENT="1">
                <QUALF>CHG</QUALF>
                </E1EDL19>
                <E1EDL19 SEGMENT="1">
                <QUALF>VDT</QUALF>
                </E1EDL19>
            </E1EDL24>
            <E1EDL24 SEGMENT="1">
                <POSNR>000020</POSNR>
                <MATNR>000000000000X002</MATNR>
                <WERKS>51</WERKS>
                <LGORT>0100</LGORT>
                <CHARG>1234567</CHARG>
                <LFIMG>24</LFIMG>
                <VRKME>UN</VRKME>
                <NTGEW>3.096</NTGEW>
                <BRGEW>3.096</BRGEW>
                <GEWEI>KGM</GEWEI>
                <VFDAT>20250302</VFDAT>
                <E1EDL19 SEGMENT="1">
                <QUALF>NWT</QUALF>
                </E1EDL19>
                <E1EDL19 SEGMENT="1">
                <QUALF>GWT</QUALF>
                </E1EDL19>
                <E1EDL19 SEGMENT="1">
                <QUALF>CHG</QUALF>
                </E1EDL19>
                <E1EDL19 SEGMENT="1">
                <QUALF>VDT</QUALF>
                </E1EDL19>
            </E1EDL24>
            </E1EDL20>
        </IDOC>

        </DELVRY01>
        '''

        def _inner(is_item, element, stack, globals):
            if globals['path']=="XXX.DELVRY01.IDOC.E1EDL20.VBELN":
                pass

            if globals['path']=="XXX.DELVRY01.IDOC.E1EDL20.E1EDL24.MATNR":
                pass

            return globals

        globals={}
        partner_id="DEFAULT_SAP_SHPCON"

        reader=XmlReader(_inner, context, partner_id, globals, xml.encode('utf-8') )
        reader.read()

        print(reader.globals['order'])
        print(reader.globals['position'])
        print(reader.globals['lot'])


    def tearDown(self):
        AppInfo.save_context(self.context, True)
        AppInfo.logoff(self.context)

if __name__ == '__main__':
    unittest.main()
