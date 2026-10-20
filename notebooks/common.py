import time
from datetime import date, timedelta
from pathlib import Path
import numpy as np
import requests
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import pandas as pd
from db import get_engine
from sqlalchemy.types import NVARCHAR, Float