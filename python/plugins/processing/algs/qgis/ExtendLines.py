# -*- coding: utf-8 -*-

"""
***************************************************************************
    ExtendLines.py
    --------------------
    Date                 : October 2016
    Copyright            : (C) 2016 by Nyall Dawson
    Email                : nyall dot dawson at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Nyall Dawson'
__date__ = 'October 2016'
__copyright__ = '(C) 2016, Nyall Dawson'

# This will get replaced with a git SHA1 when you do a git archive323

__revision__ = '$Format:%H$'

from qgis.core import (QgsApplication,
                       QgsFeatureSink,
                       QgsProcessingUtils)
from processing.algs.qgis.QgisAlgorithm import QgisAlgorithm
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.core.parameters import ParameterVector, ParameterNumber
from processing.core.outputs import OutputVector
from processing.tools import dataobjects


class ExtendLines(QgisAlgorithm):

    INPUT_LAYER = 'INPUT_LAYER'
    OUTPUT_LAYER = 'OUTPUT_LAYER'
    START_DISTANCE = 'START_DISTANCE'
    END_DISTANCE = 'END_DISTANCE'

    def group(self):
        return self.tr('Vector geometry tools')

    def __init__(self):
        super().__init__()
        self.addParameter(ParameterVector(self.INPUT_LAYER,
                                          self.tr('Input layer'), [dataobjects.TYPE_VECTOR_LINE]))
        self.addParameter(ParameterNumber(self.START_DISTANCE,
                                          self.tr('Start distance'), default=0.0))
        self.addParameter(ParameterNumber(self.END_DISTANCE,
                                          self.tr('End distance'), default=0.0))

        self.addOutput(OutputVector(self.OUTPUT_LAYER, self.tr('Extended lines')))

    def name(self):
        return 'extendlines'

    def displayName(self):
        return self.tr('Extend lines')

    def processAlgorithm(self, parameters, context, feedback):
        layer = QgsProcessingUtils.mapLayerFromString(self.getParameterValue(self.INPUT_LAYER), context)

        writer = self.getOutputFromName(
            self.OUTPUT_LAYER).getVectorWriter(layer.fields(), layer.wkbType(), layer.crs(), context)

        start_distance = self.getParameterValue(self.START_DISTANCE)
        end_distance = self.getParameterValue(self.END_DISTANCE)

        features = QgsProcessingUtils.getFeatures(layer, context)
        total = 100.0 / layer.featureCount() if layer.featureCount() else 0

        for current, input_feature in enumerate(features):
            output_feature = input_feature
            input_geometry = input_feature.geometry()
            if input_geometry:
                output_geometry = input_geometry.extendLine(start_distance, end_distance)
                if not output_geometry:
                    raise GeoAlgorithmExecutionException(
                        self.tr('Error calculating extended line'))

                output_feature.setGeometry(output_geometry)

            writer.addFeature(output_feature, QgsFeatureSink.FastInsert)
            feedback.setProgress(int(current * total))

        del writer
