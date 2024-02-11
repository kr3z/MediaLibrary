import os
import hashlib
from typing import List, Optional
from sqlalchemy.ext.declarative import AbstractConcreteBase
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from sqlalchemy import Integer, String, Float, ForeignKey, UniqueConstraint, Index, Boolean

from Base import Base,id_seq, engine

class LibraryFile(Base):
    __tablename__ = "File"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    path: Mapped[str] = mapped_column(String(500))
    md5: Mapped[str] = mapped_column(String(50))
    missing_on_disk: Mapped[Optional[bool]] = mapped_column(Boolean)
    #content_type: Mapped[str] = mapped_column(String(10))
    #content_key
    #part

    #tracks: Mapped[List["GeneralTrack"|"VideoTrack"|"AudioTrack"|"ImageTrack"]] = relationship(back_populates="file")
    #tracks: Mapped[List["Track"]] = relationship(back_populates="file")
    general_tracks: Mapped[List["GeneralTrack"]] = relationship(back_populates="file")
    video_tracks: Mapped[List["VideoTrack"]] = relationship(back_populates="file")
    audio_tracks: Mapped[List["AudioTrack"]] = relationship(back_populates="file")
    image_tracks: Mapped[List["ImageTrack"]] = relationship(back_populates="file")

    __table_args__ = (
        UniqueConstraint("name", "path", name="ux_File_name_path"),
        Index('ix_File_path', "path"))
    
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.id = id_seq.next_value()

        md5 = hashlib.md5()
        with open(os.path.join(self.path,self.name), 'rb') as f:
            while True:
                data = f.read(65536)
                if not data:
                    break
                md5.update(data)
        self.md5 = md5.hexdigest()

    def parse_tracks(self,media_info):
        for track in media_info.general_tracks:
            t = GeneralTrack(self.id,track)
            t.file = self
        for track in media_info.video_tracks:
            t = VideoTrack(self.id,track)
            t.file = self
        for track in media_info.audio_tracks:
            t = AudioTrack(self.id,track)
            t.file = self
        for track in media_info.image_tracks:
            t = ImageTrack(self.id,track)
            t.file = self

    @property
    def tracks(self):
        return self.general_tracks + self.video_tracks + self.audio_tracks + self.image_tracks

    #@property
    #def general(self):
    #    return [track for track in self.tracks if isinstance(track,GeneralTrack)]
    
    #@property
    #def video(self):
    #    return [track for track in self.tracks if isinstance(track,VideoTrack)]
    
    #@property
    #def audio(self):
    #    return [track for track in self.tracks if isinstance(track,AudioTrack)]
    
    #@property
    #def image(self):
    #    return [track for track in self.tracks if isinstance(track,ImageTrack)]

class Track(AbstractConcreteBase, Base):
    strict_attrs = True

    id: Mapped[int] #= mapped_column(id_seq,primary_key=True)
    file_key: Mapped[int] #= mapped_column(Integer, ForeignKey("File.id"))
    track_id: Mapped[int] #= mapped_column(Integer)
    #track_type = mapped_column(Integer)

    #file: Mapped["LibraryFile"]# = relationship(back_populates="tracks")



class GeneralTrack(Track):
    __tablename__ = "GeneralTrack"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    file_key: Mapped[int] = mapped_column(Integer, ForeignKey("File.id"))
    track_id: Mapped[int] = mapped_column(Integer)
    #track_type = mapped_column(Integer)

    file: Mapped["LibraryFile"] = relationship(back_populates="general_tracks")

    codec: Mapped[str] = mapped_column(String(10))
    codec_id: Mapped[Optional[str]] = mapped_column(String(10))
    count_of_audio_streams: Mapped[Optional[int]] = mapped_column(Integer)
    count_of_video_streams: Mapped[Optional[int]] = mapped_column(Integer)
    count_of_image_streams: Mapped[Optional[int]] = mapped_column(Integer)
    #datasize = mapped_column(Integer)
    duration: Mapped[Optional[int]] = mapped_column(Integer)
    file_extension: Mapped[str] = mapped_column(String(10))
    file_name: Mapped[str] = mapped_column(String(200))
    file_size: Mapped[int] =  mapped_column(Integer)
    folder_name: Mapped[str] = mapped_column(String(200))
    format: Mapped[str] = mapped_column(String(10))
    format_profile: Mapped[Optional[str]] = mapped_column(String(30))
    frame_count: Mapped[Optional[int]] = mapped_column(Integer)
    frame_rate: Mapped[Optional[float]] = mapped_column(Float)
    overall_bit_rate: Mapped[Optional[int]] = mapped_column(Integer)
    overall_bit_rate_mode: Mapped[Optional[str]] = mapped_column(String(10))
    stream_identifier: Mapped[int] = mapped_column(Integer)

    __mapper_args__ = {
        "polymorphic_identity": "GeneralTrack",
        "concrete": True,
    }

    def __init__(self,file_key,track_data):
        self.id = id_seq.next_value()
        self.file_key = file_key
        self.track_id = track_data.track_id or 0
        self.codec = track_data.codec
        self.codec_id = track_data.codec_id
        self.count_of_audio_streams = track_data.count_of_audio_streams
        self.count_of_video_streams = track_data.count_of_video_streams
        self.count_of_image_streams = track_data.count_of_image_streams
        self.duration = track_data.duration
        self.file_extension = track_data.file_extension
        self.file_name = track_data.file_name
        self.file_size = track_data.file_size
        self.folder_name = track_data.folder_name
        self.format = track_data.format
        self.format_profile = track_data.format_profile
        self.frame_count = track_data.frame_count
        self.frame_rate = track_data.frame_rate
        self.overall_bit_rate = track_data.overall_bit_rate
        self.overall_bit_rate_mode = track_data.overall_bit_rate_mode
        self.stream_identifier = track_data.stream_identifier

class VideoTrack(Track):
    __tablename__ = "VideoTrack"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    file_key: Mapped[int] = mapped_column(Integer, ForeignKey("File.id"))
    track_id: Mapped[Optional[int]] = mapped_column(Integer)
    #track_type = mapped_column(Integer)

    file: Mapped["LibraryFile"] = relationship(back_populates="video_tracks")

    duration: Mapped[Optional[int]] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)
    width: Mapped[int] = mapped_column(Integer)

    frame_count: Mapped[Optional[int]] = mapped_column(Integer)
    frame_rate: Mapped[Optional[float]] = mapped_column(Float)
    frame_rate_mode: Mapped[Optional[str]] = mapped_column(String(10))

    bit_depth: Mapped[Optional[int]] = mapped_column(Integer)
    bit_rate: Mapped[Optional[int]] = mapped_column(Integer)
    maximum_frame_rate: Mapped[Optional[float]] = mapped_column(Float)
    minimum_frame_rate: Mapped[Optional[float]] = mapped_column(Float)
    color_space: Mapped[Optional[str]] = mapped_column(String(10))

    scan_type: Mapped[Optional[str]] = mapped_column(String(30))
    stream_size: Mapped[Optional[int]] = mapped_column(Integer)

    codec: Mapped[Optional[str]] = mapped_column(String(10))
    codec_cc: Mapped[Optional[str]] = mapped_column(String(10))
    codec_family: Mapped[Optional[str]] = mapped_column(String(10))
    codec_id: Mapped[Optional[str]] = mapped_column(String(10))
    codec_id_info: Mapped[Optional[str]] = mapped_column(String(50))
    codec_info: Mapped[Optional[str]] = mapped_column(String(50))
    codec_profile: Mapped[Optional[str]] = mapped_column(String(30))
    codec_settings: Mapped[Optional[str]] = mapped_column(String(100))
    display_aspect_ratio: Mapped[Optional[float]] = mapped_column(Float)
    format: Mapped[Optional[str]] = mapped_column(String(10))
    format_info: Mapped[Optional[str]] = mapped_column(String(30))
    format_profile: Mapped[Optional[str]] = mapped_column(String(30))
    format_settings: Mapped[Optional[str]] = mapped_column(String(30))
    interlacement: Mapped[Optional[str]] = mapped_column(String(10))
    internet_media_type: Mapped[Optional[str]] = mapped_column(String(30))
    pixel_aspect_ratio: Mapped[Optional[float]] = mapped_column(Float)
    resolution: Mapped[Optional[int]] = mapped_column(Integer)
    streamorder: Mapped[Optional[int]] = mapped_column(Integer)

    __mapper_args__ = {
        "polymorphic_identity": "VideoTrack",
        "concrete": True,
    }

    def __init__(self,file_key,track_data):
        self.id = id_seq.next_value()
        self.file_key = file_key
        self.track_id = track_data.track_id

        self.duration = track_data.duration
        self.height = track_data.height
        self.width = track_data.width

        self.frame_count = track_data.frame_count
        self.frame_rate = track_data.frame_rate
        self.frame_rate_mode = track_data.frame_rate_mode

        self.bit_depth = track_data.bit_depth
        self.bit_rate = track_data.bit_rate
        self.maximum_frame_rate = track_data.maximum_frame_rate
        self.minimum_frame_rate = track_data.minimum_frame_rate
        self.color_space = track_data.color_space

        self.scan_type = track_data.scan_type
        self.stream_size = track_data.stream_size

        self.codec = track_data.codec
        self.codec_cc = track_data.codec_cc
        self.codec_family = track_data.codec_family
        self.codec_id = track_data.codec_id
        self.codec_id_info = track_data.codec_id_info
        self.codec_info = track_data.codec_info
        self.codec_profile = track_data.codec_profile
        self.codec_settings = track_data.codec_settings
        self.display_aspect_ratio = track_data.display_aspect_ratio
        self.format = track_data.format
        self.format_info = track_data.format_info
        self.format_profile = track_data.format_profile
        self.format_settings = track_data.format_settings
        self.interlacement = track_data.interlacement
        self.internet_media_type = track_data.internet_media_type
        self.pixel_aspect_ratio = track_data.pixel_aspect_ratio
        self.resolution = track_data.resolution
        self.streamorder = track_data.streamorder

class AudioTrack(Track):
    __tablename__ = "AudioTrack"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    file_key: Mapped[int] = mapped_column(Integer, ForeignKey("File.id"))
    track_id: Mapped[Optional[int]] = mapped_column(Integer)

    file: Mapped["LibraryFile"] = relationship(back_populates="audio_tracks")

    duration: Mapped[Optional[int]] = mapped_column(Integer)
    channel_s: Mapped[Optional[int]] = mapped_column(Integer)
    channel_positions: Mapped[Optional[str]] = mapped_column(String(20))
    channellayout: Mapped[Optional[str]] = mapped_column(String(10))
    bit_rate_mode: Mapped[Optional[str]] = mapped_column(String(10))

    frame_count: Mapped[Optional[int]] = mapped_column(Integer)
    frame_rate: Mapped[Optional[float]] = mapped_column(Float)
    maximum_bit_rate: Mapped[Optional[float]] = mapped_column(Float)
    nominal_bit_rate: Mapped[Optional[float]] = mapped_column(Float)
    samples_count: Mapped[Optional[int]] = mapped_column(Integer)
    samples_per_frame: Mapped[Optional[int]] = mapped_column(Integer)
    sampling_rate: Mapped[Optional[int]] = mapped_column(Integer)

    codec: Mapped[Optional[str]] = mapped_column(String(10))
    codec_cc: Mapped[Optional[str]] = mapped_column(String(10))
    codec_family: Mapped[Optional[str]] = mapped_column(String(10))
    codec_id: Mapped[Optional[str]] = mapped_column(String(10))
    commercial_name: Mapped[Optional[str]] = mapped_column(String(10))
    compression_mode: Mapped[Optional[str]] = mapped_column(String(10))
    default: Mapped[Optional[str]] = mapped_column(String(10))
    format: Mapped[Optional[str]] = mapped_column(String(10))
    format_info: Mapped[Optional[str]] = mapped_column(String(30))
    format_profile: Mapped[Optional[str]] = mapped_column(String(30))

    source_delay: Mapped[Optional[int]] = mapped_column(Integer)
    source_delay_source: Mapped[Optional[str]] = mapped_column(String(30))
    source_duration: Mapped[Optional[int]] = mapped_column(Integer)
    source_frame_count: Mapped[Optional[int]] = mapped_column(Integer)
    source_stream_size: Mapped[Optional[int]] = mapped_column(Integer)
    source_streamsize_proportion: Mapped[Optional[float]] = mapped_column(Float)

    __mapper_args__ = {
        "polymorphic_identity": "AudioTrack",
        "concrete": True,
    }

    def __init__(self,file_key,track_data):
        self.id = id_seq.next_value()
        self.file_key = file_key
        self.track_id = track_data.track_id

        self.duration = track_data.duration
        self.channel_s = track_data.channel_s
        self.channel_positions = track_data.channel_positions
        self.channellayout = track_data.channellayout
        self.bit_rate_mode = track_data.bit_rate_mode

        self.frame_count = track_data.frame_count
        self.frame_rate = track_data.frame_rate
        self.maximum_bit_rate = track_data.maximum_bit_rate
        self.nominal_bit_rate = track_data.nominal_bit_rate
        self.samples_count = track_data.samples_count
        self.samples_per_frame = track_data.samples_per_frame
        self.sampling_rate = track_data.sampling_rate

        self.codec = track_data.codec
        self.codec_cc = track_data.codec_cc
        self.codec_family = track_data.codec_family
        self.codec_id = track_data.codec_id
        self.commercial_name = track_data.commercial_name
        self.compression_mode = track_data.compression_mode
        self.default = track_data.default
        self.format = track_data.format
        self.format_info = track_data.format_info
        self.format_profile = track_data.format_profile

        self.source_delay = track_data.source_delay
        self.source_delay_source = track_data.source_delay_source
        self.source_duration = track_data.source_duration
        self.source_frame_count = track_data.source_frame_count
        self.source_stream_size = track_data.source_stream_size
        self.source_streamsize_proportion = track_data.source_streamsize_proportion

class ImageTrack(Track):
    __tablename__ = "ImageTrack"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    file_key: Mapped[int] = mapped_column(Integer, ForeignKey("File.id"))
    track_id: Mapped[Optional[int]] = mapped_column(Integer)

    file: Mapped["LibraryFile"] = relationship(back_populates="image_tracks")

    height: Mapped[int] = mapped_column(Integer)
    width: Mapped[int] = mapped_column(Integer)
    stream_size: Mapped[Optional[int]] = mapped_column(Integer)
    bit_depth: Mapped[Optional[int]] = mapped_column(Integer)
    chroma_subsampling: Mapped[Optional[str]] = mapped_column(String(10))
    codec: Mapped[Optional[str]] = mapped_column(String(10))
    color_space: Mapped[Optional[str]] = mapped_column(String(10))
    commercial_name: Mapped[Optional[str]] = mapped_column(String(10))
    compression_mode: Mapped[Optional[str]] = mapped_column(String(10))
    format: Mapped[Optional[str]] = mapped_column(String(10))
    internet_media_type: Mapped[Optional[str]] = mapped_column(String(30))
    proportion_of_this_stream: Mapped[Optional[float]] = mapped_column(Float)
    resolution: Mapped[Optional[int]] = mapped_column(Integer)
    stream_identifier: Mapped[Optional[int]] = mapped_column(Integer)

    __mapper_args__ = {
        "polymorphic_identity": "ImageTrack",
        "concrete": True,
    }

    def __init__(self,file_key,track_data):
        self.id = id_seq.next_value()
        self.file_key = file_key
        self.track_id = track_data.track_id

        self.height = track_data.height
        self.width = track_data.width
        self.stream_size = track_data.stream_size
        self.bit_depth = track_data.bit_depth
        self.chroma_subsampling = track_data.chroma_subsampling
        self.codec = track_data.codec
        self.color_space = track_data.color_space
        self.commercial_name = track_data.commercial_name
        self.compression_mode = track_data.compression_mode
        self.format = track_data.format
        self.internet_media_type = track_data.internet_media_type
        self.proportion_of_this_stream = track_data.proportion_of_this_stream
        self.resolution = track_data.resolution
        self.stream_identifier = track_data.stream_identifier


Base.registry.configure()


#from sqlalchemy import , URL, MetaData, Table, ,Column, Integer
#from sqlalchemy.orm import Session, DeclarativeBase, mapped_column, 

#class TestSeq(Base):
#    __tablename__ = "TestSeq"
#    id: Mapped[int] = mapped_column(Integer,primary_key=True)


Base.metadata.create_all(engine)

#gt1 = TestSeq(id=id_seq.next_value())
#gt2 = TestSeq(id=id_seq.next_value())


#test1 = TestSeq(id=id_seq.next_value())
#test2 = TestSeq(id=id_seq.next_value())

#session = Session(engine)

#session.add(test1)
#session.add(test2)
#session.flush()
#session.commit()

#print(test1.id)
#print(test2.id)

#session.close()
