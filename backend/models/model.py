from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from geoalchemy2 import Geometry

Base = declarative_base()

# ------------------ Public Schema Models ------------------

class Buildings(Base):
    __tablename__ = 'buildings'
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True)
    name = Column(String)
    geom = Column(Geometry('MULTIPOLYGON'))

class Landuse(Base):
    __tablename__ = 'landuse'
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True)
    landuse = Column(String)
    geom = Column(Geometry('MULTIPOLYGON'))

class PlacePoints(Base):
    __tablename__ = 'place_points'
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    geom = Column(Geometry('POINT'))

class PlacePolygon(Base):
    __tablename__ = 'place_polygon'
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    geom = Column(Geometry('MULTIPOLYGON'))

class Places(Base):
    __tablename__ = 'places'
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    geom = Column(Geometry('GEOMETRY'))

class Railway(Base):
    __tablename__ = 'railway'
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True)
    railway = Column(String)
    geom = Column(Geometry('LINESTRING'))

class Roads(Base):
    __tablename__ = 'roads'
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True)
    name = Column(String)
    highway = Column(String)
    geom = Column(Geometry('LINESTRING'))

class TrafficPoint(Base):
    __tablename__ = 'traffic_point'
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True)
    type = Column(String)
    geom = Column(Geometry('POINT'))

class TrafficPolygon(Base):
    __tablename__ = 'traffic_polygon'
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True)
    type = Column(String)
    geom = Column(Geometry('MULTIPOLYGON'))

class TransportStops(Base):
    __tablename__ = 'transport_stops'
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True)
    name = Column(String)
    stop_type = Column(String)
    geom = Column(Geometry('POINT'))

class WaterType(Base):
    __tablename__ = 'water_type'
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True)
    type = Column(String)
    geom = Column(Geometry('MULTIPOLYGON'))

class Waterway(Base):
    __tablename__ = 'waterway'
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True)
    waterway = Column(String)
    geom = Column(Geometry('LINESTRING'))

class WorshipPlaces(Base):
    __tablename__ = 'worship_places'
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True)
    religion = Column(String)
    name = Column(String)
    geom = Column(Geometry('POINT'))
