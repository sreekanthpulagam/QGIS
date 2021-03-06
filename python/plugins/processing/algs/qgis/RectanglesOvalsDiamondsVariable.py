# -*- coding: utf-8 -*-

"""
***************************************************************************
    RectanglesOvalsDiamondsVariable.py
    ---------------------
    Date                 : April 2016
    Copyright            : (C) 2016 by Alexander Bruy
    Email                : alexander dot bruy at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
from builtins import range

__author__ = 'Alexander Bruy'
__date__ = 'August 2012'
__copyright__ = '(C) 2012, Victor Olaya'

# This will get replaced with a git SHA1 when you do a git archive323

__revision__ = '$Format:%H$'

import math

from qgis.core import (QgsApplication,
                       QgsWkbTypes,
                       QgsFeature,
                       QgsFeatureSink,
                       QgsGeometry,
                       QgsPointXY,
                       QgsMessageLog,
                       QgsProcessingUtils)

from processing.algs.qgis.QgisAlgorithm import QgisAlgorithm
from processing.core.parameters import ParameterVector
from processing.core.parameters import ParameterSelection
from processing.core.parameters import ParameterTableField
from processing.core.parameters import ParameterNumber
from processing.core.outputs import OutputVector
from processing.tools import dataobjects


class RectanglesOvalsDiamondsVariable(QgisAlgorithm):

    INPUT_LAYER = 'INPUT_LAYER'
    SHAPE = 'SHAPE'
    WIDTH = 'WIDTH'
    HEIGHT = 'HEIGHT'
    ROTATION = 'ROTATION'
    SEGMENTS = 'SEGMENTS'
    OUTPUT_LAYER = 'OUTPUT_LAYER'

    def group(self):
        return self.tr('Vector geometry tools')

    def __init__(self):
        super().__init__()
        self.shapes = [self.tr('Rectangles'), self.tr('Diamonds'), self.tr('Ovals')]

        self.addParameter(ParameterVector(self.INPUT_LAYER,
                                          self.tr('Input layer'),
                                          [dataobjects.TYPE_VECTOR_POINT]))
        self.addParameter(ParameterSelection(self.SHAPE,
                                             self.tr('Buffer shape'), self.shapes))
        self.addParameter(ParameterTableField(self.WIDTH,
                                              self.tr('Width field'),
                                              self.INPUT_LAYER,
                                              ParameterTableField.DATA_TYPE_NUMBER))
        self.addParameter(ParameterTableField(self.HEIGHT,
                                              self.tr('Height field'),
                                              self.INPUT_LAYER,
                                              ParameterTableField.DATA_TYPE_NUMBER))
        self.addParameter(ParameterTableField(self.ROTATION,
                                              self.tr('Rotation field'),
                                              self.INPUT_LAYER,
                                              ParameterTableField.DATA_TYPE_NUMBER,
                                              True))
        self.addParameter(ParameterNumber(self.SEGMENTS,
                                          self.tr('Number of segments'),
                                          1,
                                          999999999,
                                          36))

        self.addOutput(OutputVector(self.OUTPUT_LAYER,
                                    self.tr('Output'),
                                    datatype=[dataobjects.TYPE_VECTOR_POLYGON]))

    def name(self):
        return 'rectanglesovalsdiamondsvariable'

    def displayName(self):
        return self.tr('Rectangles, ovals, diamonds (variable)')

    def processAlgorithm(self, parameters, context, feedback):
        layer = QgsProcessingUtils.mapLayerFromString(self.getParameterValue(self.INPUT_LAYER), context)
        shape = self.getParameterValue(self.SHAPE)
        width = self.getParameterValue(self.WIDTH)
        height = self.getParameterValue(self.HEIGHT)
        rotation = self.getParameterValue(self.ROTATION)
        segments = self.getParameterValue(self.SEGMENTS)

        writer = self.getOutputFromName(
            self.OUTPUT_LAYER).getVectorWriter(layer.fields(), QgsWkbTypes.Polygon, layer.crs(), context)

        features = QgsProcessingUtils.getFeatures(layer, context)

        if shape == 0:
            self.rectangles(writer, features, width, height, rotation)
        elif shape == 1:
            self.diamonds(writer, features, width, height, rotation)
        else:
            self.ovals(writer, features, width, height, rotation, segments)

        del writer

    def rectangles(self, writer, features, width, height, rotation):
        ft = QgsFeature()

        if rotation is not None:
            for current, feat in enumerate(features):
                w = feat[width]
                h = feat[height]
                angle = feat[rotation]
                if not w or not h or not angle:
                    QgsMessageLog.logMessage(self.tr('Feature {} has empty '
                                                     'width, height or angle. '
                                                     'Skipping...'.format(feat.id())),
                                             self.tr('Processing'), QgsMessageLog.WARNING)
                    continue

                xOffset = w / 2.0
                yOffset = h / 2.0
                phi = angle * math.pi / 180

                point = feat.geometry().asPoint()
                x = point.x()
                y = point.y()
                points = [(-xOffset, -yOffset), (-xOffset, yOffset), (xOffset, yOffset), (xOffset, -yOffset)]
                polygon = [[QgsPointXY(i[0] * math.cos(phi) + i[1] * math.sin(phi) + x,
                                       -i[0] * math.sin(phi) + i[1] * math.cos(phi) + y) for i in points]]

                ft.setGeometry(QgsGeometry.fromPolygon(polygon))
                ft.setAttributes(feat.attributes())
                writer.addFeature(ft, QgsFeatureSink.FastInsert)
        else:
            for current, feat in enumerate(features):
                w = feat[width]
                h = feat[height]
                if not w or not h:
                    QgsMessageLog.logMessage(self.tr('Feature {} has empty '
                                                     'width or height. '
                                                     'Skipping...'.format(feat.id())),
                                             self.tr('Processing'), QgsMessageLog.WARNING)
                    continue

                xOffset = w / 2.0
                yOffset = h / 2.0

                point = feat.geometry().asPoint()
                x = point.x()
                y = point.y()
                points = [(-xOffset, -yOffset), (-xOffset, yOffset), (xOffset, yOffset), (xOffset, -yOffset)]
                polygon = [[QgsPointXY(i[0] + x, i[1] + y) for i in points]]

                ft.setGeometry(QgsGeometry.fromPolygon(polygon))
                ft.setAttributes(feat.attributes())
                writer.addFeature(ft, QgsFeatureSink.FastInsert)

    def diamonds(self, writer, features, width, height, rotation):
        ft = QgsFeature()

        if rotation is not None:
            for current, feat in enumerate(features):
                w = feat[width]
                h = feat[height]
                angle = feat[rotation]
                if not w or not h or not angle:
                    QgsMessageLog.logMessage(self.tr('Feature {} has empty '
                                                     'width, height or angle. '
                                                     'Skipping...'.format(feat.id())),
                                             self.tr('Processing'), QgsMessageLog.WARNING)
                    continue

                xOffset = w / 2.0
                yOffset = h / 2.0
                phi = angle * math.pi / 180

                point = feat.geometry().asPoint()
                x = point.x()
                y = point.y()
                points = [(0.0, -yOffset), (-xOffset, 0.0), (0.0, yOffset), (xOffset, 0.0)]
                polygon = [[QgsPointXY(i[0] * math.cos(phi) + i[1] * math.sin(phi) + x,
                                       -i[0] * math.sin(phi) + i[1] * math.cos(phi) + y) for i in points]]

                ft.setGeometry(QgsGeometry.fromPolygon(polygon))
                ft.setAttributes(feat.attributes())
                writer.addFeature(ft, QgsFeatureSink.FastInsert)
        else:
            for current, feat in enumerate(features):
                w = feat[width]
                h = feat[height]
                if not w or not h:
                    QgsMessageLog.logMessage(self.tr('Feature {} has empty '
                                                     'width or height. '
                                                     'Skipping...'.format(feat.id())),
                                             self.tr('Processing'), QgsMessageLog.WARNING)
                    continue

                xOffset = w / 2.0
                yOffset = h / 2.0

                point = feat.geometry().asPoint()
                x = point.x()
                y = point.y()
                points = [(0.0, -yOffset), (-xOffset, 0.0), (0.0, yOffset), (xOffset, 0.0)]
                polygon = [[QgsPointXY(i[0] + x, i[1] + y) for i in points]]

                ft.setGeometry(QgsGeometry.fromPolygon(polygon))
                ft.setAttributes(feat.attributes())
                writer.addFeature(ft, QgsFeatureSink.FastInsert)

    def ovals(self, writer, features, width, height, rotation, segments):
        ft = QgsFeature()

        if rotation is not None:
            for current, feat in enumerate(features):
                w = feat[width]
                h = feat[height]
                angle = feat[rotation]
                if not w or not h or not angle:
                    QgsMessageLog.logMessage(self.tr('Feature {} has empty '
                                                     'width, height or angle. '
                                                     'Skipping...'.format(feat.id())),
                                             self.tr('Processing'), QgsMessageLog.WARNING)
                    continue

                xOffset = w / 2.0
                yOffset = h / 2.0
                phi = angle * math.pi / 180

                point = feat.geometry().asPoint()
                x = point.x()
                y = point.y()
                points = []
                for t in [(2 * math.pi) / segments * i for i in range(segments)]:
                    points.append((xOffset * math.cos(t), yOffset * math.sin(t)))
                polygon = [[QgsPointXY(i[0] * math.cos(phi) + i[1] * math.sin(phi) + x,
                                       -i[0] * math.sin(phi) + i[1] * math.cos(phi) + y) for i in points]]

                ft.setGeometry(QgsGeometry.fromPolygon(polygon))
                ft.setAttributes(feat.attributes())
                writer.addFeature(ft, QgsFeatureSink.FastInsert)
        else:
            for current, feat in enumerate(features):
                w = feat[width]
                h = feat[height]
                if not w or not h:
                    QgsMessageLog.logMessage(self.tr('Feature {} has empty '
                                                     'width or height. '
                                                     'Skipping...'.format(feat.id())),
                                             self.tr('Processing'), QgsMessageLog.WARNING)
                    continue

                xOffset = w / 2.0
                yOffset = h / 2.0

                point = feat.geometry().asPoint()
                x = point.x()
                y = point.y()
                points = []
                for t in [(2 * math.pi) / segments * i for i in range(segments)]:
                    points.append((xOffset * math.cos(t), yOffset * math.sin(t)))
                polygon = [[QgsPointXY(i[0] + x, i[1] + y) for i in points]]

                ft.setGeometry(QgsGeometry.fromPolygon(polygon))
                ft.setAttributes(feat.attributes())
                writer.addFeature(ft, QgsFeatureSink.FastInsert)
