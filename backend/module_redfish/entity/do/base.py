"""
Redfish模块DO层基础配置
"""
from sqlalchemy.ext.declarative import declarative_base

# Redfish模块专用的SQLAlchemy Base
Base = declarative_base() 