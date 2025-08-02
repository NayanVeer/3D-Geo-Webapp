from sqlalchemy import Column, Integer, String
from geoalchemy2 import Geometry
from db import Base

# ------------------ Public Schema Models ------------------

class Buildings(Base):
    __tablename__ = 'buildings'
    __table_args__ = {'schema': 'public'}
    ogc_fid = Column(Integer, primary_key=True)
    name = Column(String)
    wkb_geometry = Column(Geometry('MULTIPOLYGON'))

class Landuse(Base):
    __tablename__ = 'landuse'
    __table_args__ = {'schema': 'public'}
    ogc_fid = Column(Integer, primary_key=True)
    landuse = Column(String)
    wkb_geometry = Column(Geometry('MULTIPOLYGON'))

class PlacePoints(Base):
    __tablename__ = 'place_points'
    __table_args__ = {'schema': 'public'}
    ogc_fid = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    wkb_geometry = Column(Geometry('POINT'))

class PlacePolygon(Base):
    __tablename__ = 'place_polygon'
    __table_args__ = {'schema': 'public'}
    ogc_fid = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    wkb_geometry = Column(Geometry('MULTIPOLYGON'))

class Places(Base):
    __tablename__ = 'places'
    __table_args__ = {'schema': 'public'}
    ogc_fid = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    wkb_geometry = Column(Geometry('GEOMETRY'))

class Railway(Base):
    __tablename__ = 'railway'
    __table_args__ = {'schema': 'public'}
    ogc_fid = Column(Integer, primary_key=True)
    railway = Column(String)
    wkb_geometry = Column(Geometry('LINESTRING'))

class Roads(Base):
    __tablename__ = 'roads'
    __table_args__ = {'schema': 'public'}
    ogc_fid = Column(Integer, primary_key=True)
    name = Column(String)
    highway = Column(String)
    wkb_geometry = Column(Geometry('LINESTRING'))

class TrafficPoint(Base):
    __tablename__ = 'traffic_point'
    __table_args__ = {'schema': 'public'}
    ogc_fid = Column(Integer, primary_key=True)
    fclass = Column(String)
    name = Column(String)
    wkb_geometry = Column(Geometry('POINT'))

class TrafficPolygon(Base):
    __tablename__ = 'traffic_polygon'
    __table_args__ = {'schema': 'public'}
    ogc_fid = Column(Integer, primary_key=True)
    fclass = Column(String)
    name = Column(String)
    wkb_geometry = Column(Geometry('MULTIPOLYGON'))

class TransportStops(Base):
    __tablename__ = 'transport_stops'
    __table_args__ = {'schema': 'public'}
    ogc_fid = Column(Integer, primary_key=True)
    name = Column(String)
    fclass = Column(String)
    wkb_geometry = Column(Geometry('POINT'))

class WaterType(Base):
    __tablename__ = 'water_type'
    __table_args__ = {'schema': 'public'}
    ogc_fid = Column(Integer, primary_key=True)
    fclass = Column(String)
    name = Column(String)
    wkb_geometry = Column(Geometry('MULTIPOLYGON'))

class Waterway(Base):
    __tablename__ = 'waterway'
    __table_args__ = {'schema': 'public'}
    ogc_fid = Column(Integer, primary_key=True)
    fclass = Column(String)
    name = Column(String)
    width = Column(Integer)
    wkb_geometry = Column(Geometry('LINESTRING'))

class WorshipPlaces(Base):
    __tablename__ = 'worship_places'
    __table_args__ = {'schema': 'public'}
    ogc_fid = Column(Integer, primary_key=True)
    fclass = Column(String)
    name = Column(String)
    wkb_geometry = Column(Geometry('POINT'))
