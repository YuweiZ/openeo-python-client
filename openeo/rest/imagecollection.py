import base64
from typing import List, Dict

import cloudpickle
from pandas import Series

from ..imagecollection import ImageCollection
from ..sessions import Session


class RestImageCollection(ImageCollection):
    """Class representing an Image Collection. """


    def __init__(self, parentgraph:Dict,session:Session):
        self.graph = parentgraph
        self.session = session


    def apply_pixel(self, bands:List, bandfunction) -> 'ImageCollection':
        """Apply a function to the given set of bands in this image collection."""
        pickled_lambda = cloudpickle.dumps(bandfunction)
        graph = {
            'process_id': 'apply_pixel',
            'args' : {
                'collections':[self.graph],
                'bands':bands,
                'function': str(base64.b64encode(pickled_lambda),"UTF-8")
            }
        }
        return RestImageCollection(graph,session=self.session)

    def aggregate_time(self, temporal_window, aggregationfunction) -> Series :
        """ Applies a windowed reduction to a timeseries by applying a user defined function.

            :param temporal_window: The time window to group by
            :param aggregationfunction: The function to apply to each time window. Takes a pandas Timeseries as input.
            :return A pandas Timeseries object
        """
        # /api/jobs
        pickled_lambda = cloudpickle.dumps(aggregationfunction)
        graph = {
            'process_id': 'reduce_by_time',
            'args' : {
                'collections':[self.graph],
                'temporal_window': temporal_window,
                'function': str(base64.b64encode(pickled_lambda),"UTF-8")
            }
        }
        return RestImageCollection(graph,session=self.session)

    def min_time(self) -> 'ImageCollection':
        graph = {
            'process_id': 'min_time',
            'args' : {
                'collections':[self.graph]
            }
        }
        return RestImageCollection(graph,session=self.session)


    ####VIEW methods #######
    def timeseries(self, x, y, srs="EPSG:4326") -> Dict:
        """
        Extract a time series for the given point location.

        :param x: The x coordinate of the point
        :param y: The y coordinate of the point
        :param srs: The spatial reference system of the coordinates, by default this is 'EPSG:4326', where x=longitude and y=latitude.
        :return: Dict: A timeseries
        """
        return self.session.point_timeseries(self.graph, x, y, srs)


    def download(self,outputfile:str, bbox="", time="",outputformat="geotiff") -> str:
        """Extraxts a geotiff from this image collection."""
        return self.session.download(self.graph,time,outputformat,outputfile)

    def tiled_viewing_service(self) -> Dict:
        return self.session.tiled_viewing_service(self.graph)

