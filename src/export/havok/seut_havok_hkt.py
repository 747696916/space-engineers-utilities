import os	
import re	
import bpy	
import shutil	
import tempfile	

from collections            import OrderedDict	
from os.path                import basename, join	
from string                 import Template	
from xml.etree              import ElementTree	

from .seut_havok_options        import HAVOK_OPTION_FILE_CONTENT
from ..seut_export_utils        import ExportSettings, StdoutOperator, MissbehavingToolError, tool_path, write_to_log
from ...utils.called_tool_type  import ToolType

def process_hktfbx_to_fbximporterhkt(context, settings: ExportSettings, srcfile, dstfile):	
    settings.callTool(	
        context,
        [settings.fbximporter, srcfile, dstfile],	
        ToolType(1),
        logfile=dstfile+'.convert.log'
    )	

def process_fbximporterhkt_to_final_hkt_for_mwm(self, context, scene, path, settings: ExportSettings, srcfile, dstfile, havokoptions=HAVOK_OPTION_FILE_CONTENT):	
    hko = tempfile.NamedTemporaryFile(mode='wt', prefix='space_engineers_', suffix=".hko", delete=False) # wt mode is write plus text mode.	
    try:	
        with hko.file as tempfile_to_process:	
            tempfile_to_process.write(havokoptions)	

        # -t is for standard ouput, -s designates a filter set (hko created above), -p designates path.	
        # Above referenced from running "hctStandAloneFilterManager.exe -h"	
        settings.callTool(	
            context,
            [settings.havokfilter, '-t', '-s', hko.name, '-p', dstfile, srcfile], 	
            ToolType(2),
            logfile=dstfile+'.filter.log',	
            successfulExitCodes=[0,1]
        )	
    finally:	
        os.remove(hko.name)

        def copy(srcfile: str, dstfile: str):
            if srcfile is not None and dstfile != srcfile:
                shutil.copy2(srcfile, dstfile)

        # Create a copy of the main models HKT file for all the build stages to go through MWMB with their models.
        # This could be modified at a later date if unique collisions are implemented per build stage to not process based on their existence.
        if os.path.exists(srcfile):
            for collection in scene.collection.children:
                for childcollection in collection.children:
                    if "BS" in str(childcollection.name) and "LOD" not in str(childcollection.name) and len(childcollection.objects) > 0:
                        print(childcollection.name)
                        hktBSfile = join(path, scene.seut.subtypeId + '_' + str(childcollection.name)[:3] + ".hkt")
                        copy(srcfile, hktBSfile)
                        
        
        self.report({'INFO'}, "SEUT: Collision files have been created.") 