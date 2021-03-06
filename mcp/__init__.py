from flask import Flask
from flask.ext.pymongo import PyMongo

import os
import ConfigParser
import logging
import logging.config
from logging.handlers import RotatingFileHandler
from flask.ext.cache import Cache



#from utils.utils import Utils

# Create MongoDB database object.
mongo = PyMongo()

# Create utils instance.
#utils = Utils()


def create_app():
    ''' Create the Flask app.
    '''
    # Create the Flask app.
    app = Flask(__name__)

    # Load application configurations
    load_config(app)

    # Configure logging.
    configure_logging(app)

    # Register URL rules.
    register_url_rules(app)

    # Init app for use with this PyMongo
    # http://flask-pymongo.readthedocs.org/en/latest/#flask_pymongo.PyMongo.init_app
    mongo.init_app(app, config_prefix='MONGO')

    return app


def load_config(app):
    ''' Reads the config file and loads configuration properties into the Flask app.
    :param app: The Flask app object.
    '''

    # Get the path to the application directory, that's where the config file resides.
    par_dir = os.path.join(__file__, os.pardir)
    par_dir_abs_path = os.path.abspath(par_dir)
    app_dir = os.path.dirname(par_dir_abs_path)

    # Read config file
    # FIXME: Use the "common pattern" described in "Configuring from Files": http://flask.pocoo.org/docs/config/
    config = ConfigParser.RawConfigParser()
    config_filepath = app_dir + '/config.cfg'
    config.read(config_filepath)

    # Set up config properties
    app.config['SERVER_PORT'] = config.get('Application', 'SERVER_PORT')
    app.config['BASE_PATH'] = config.get('Application', 'BASE_PATH')

    # Set up MongoDB DB Name
    app.config['MONGO_DBNAME'] = config.get('Mongo', 'DB_NAME')

    # Logging path might be relative or starts from the root.
    # If it's relative then be sure to prepend the path with the application's root directory path.
    log_path = config.get('Logging', 'PATH')
    if log_path.startswith('/'):
        app.config['LOG_PATH'] = log_path
    else:
        app.config['LOG_PATH'] = app_dir + '/' + log_path

    app.config['LOG_LEVEL'] = config.get('Logging', 'LEVEL').upper()

     # Caching
    app.config['CACHE_TYPE'] = config.get('Caching', 'TYPE')
    app.config['CACHE_DEFAULT_TIMEOUT'] = int(config.get('Caching', 'DEFAULT_TIMEOUT'))

    app.cache = Cache(app)



def configure_logging(app):

    # Get the path of the log from the config
    log_path = app.config['LOG_PATH']

    # Get the level of logging from the config
    log_level = app.config['LOG_LEVEL']

    # If path directory doesn't exist, create it.
    log_dir = os.path.dirname(log_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create Log_Handler
    log_handler = RotatingFileHandler(log_path, maxBytes=250000, backupCount=5)

    # add formatter to log handler
    log_handler.setFormatter(formatter)

    # Get the level of the Debug and set it to the logger
    app.logger.setLevel(log_level)

    # Add the handlers to the logger
    app.logger.addHandler(log_handler)

    # Test if the logging is working by typing this string to a file.
    app.logger.info('Logging to: %s', log_path)

# Views for json responses
from views.index import Index
from views.budget import BudgetType
from views.company import CompanyDetails
from views.company1 import CompanyList
from views.pie import Piechart
from views.procurement import ProcurementType
from views.tree import Treemap
from views.treemapprice import TreemapPrice
from views.vlera_cmimi import VleraCmimi
from views.municipalityPV import MunicipalityList
from views.company_names import CompanyNames
from views.map import Map




def register_url_rules(app):
    ''' Register URLs
    :param app: The Flask application instance.
    '''

    # Show instructional index page.
    cached_index = app.cache.cached()(Index.as_view('index'))
    app.add_url_rule('/', view_func=cached_index)



    cached_buget = app.cache.cached()(BudgetType.as_view('json_budget'))
    app.add_url_rule(
        '/<string:komuna>/budget-type/<int:year>', view_func=cached_buget)

    cached_company = app.cache.cached()(CompanyDetails.as_view('json_company'))
    app.add_url_rule(
        '/<string:komuna>/company/<string:name>', view_func=cached_company)

    cached_company1 = app.cache.cached()(CompanyList.as_view('json_company1'))
    app.add_url_rule(
        '/<string:komuna>/monthly-summary', view_func=cached_company1)

    cached_municipality = app.cache.cached()(MunicipalityList.as_view('json_municipality'))
    app.add_url_rule(
        '/monthly-summary/<int:viti>', view_func=cached_municipality)

    cached_company_names = app.cache.cached()(CompanyNames.as_view('json_company_names'))
    app.add_url_rule(
        '/<string:komuna>/company-names/<int:viti>', view_func=cached_company_names)

    cached_pie = app.cache.cached()(Piechart.as_view('json_pie'))
    app.add_url_rule(
        '/<string:komuna>/piechart/<int:viti>', view_func=cached_pie)

    cached_map = app.cache.cached()(Map.as_view('json_map'))
    app.add_url_rule(
        '/<string:komuna>/map/<int:viti>', view_func=cached_map)

    cached_tree = app.cache.cached()(Treemap.as_view('json_tree'))
    app.add_url_rule(
        '/<string:komuna>/treemap/<int:viti>', view_func=cached_tree)

    cached_tree_map_price = app.cache.cached()(Treemap.as_view('json_treemap_price'))
    app.add_url_rule(
        '/<string:komuna>/treemap/price/<int:viti>', view_func=cached_tree_map_price)

    cached_procurement = app.cache.cached()(ProcurementType.as_view('json_procurement'))
    app.add_url_rule(
        '/<string:komuna>/procurement-type/<int:year>', view_func=cached_procurement)

    cached_vlera_cmimi = app.cache.cached()(VleraCmimi.as_view('json_vlera_cmimi'))
    app.add_url_rule(
        '/<string:komuna>/monthly-summary/<int:viti>', view_func=cached_vlera_cmimi)
