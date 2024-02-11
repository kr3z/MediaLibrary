import os
import logging
import logging.config
from pymediainfo import MediaInfo
from sqlalchemy import select
from sqlalchemy.orm import Session

from Tracks import LibraryFile
from Base import engine

WORKING_DIR = os.path.dirname(os.path.realpath(__file__))
logging.config.fileConfig(WORKING_DIR+os.sep+'logging.conf')
logger = logging.getLogger('FileScanner')

class FileScanner:
    def __init__(self, root_dir: str):
        abs_root = os.path.abspath(os.path.expanduser(os.path.expandvars(root_dir)))
        if not os.path.isdir(abs_root):
            raise Exception("Invalid Path: %s" % (abs_root))
        self._root_dir = abs_root
        logger.debug("FileScanner initialized for path: %s", self._root_dir)

    def scan(self):
        for root, dirs, files in os.walk(self._root_dir):
            with Session(engine, autoflush=False) as session:
                logger.info("Scanning for media files in: %s", root)
                existing_files = session.execute(select(LibraryFile).where(LibraryFile.path==root)).all()
                existing_filenames = {existing_file[0].name for existing_file in existing_files}
                logger.debug(existing_filenames)
                for file in files:
                    if file in existing_filenames:
                        logger.debug("File %s in directory %s already existing in DB, skipping", file, root)
                        existing_filenames.remove(file)
                    else:
                        media_info = MediaInfo.parse(os.path.join(root,file))
                        if len(media_info.tracks)>1:
                            logger.debug("File %s in directory %s does not exist in DB, scanning", file, root)
                            lf = LibraryFile(file,root)
                            lf.parse_tracks(media_info)
                            session.add(lf)
                if len(existing_filenames)>1:
                    logger.info("Files in DB that were not found on disk: %s", existing_filenames)
                    missing_files = session.execute(select(LibraryFile).where(LibraryFile.name.in_(existing_filenames))).all()
                    for missing_file in missing_files:
                        missing_file[0].missing_on_disk=1
                session.flush()
                session.commit()