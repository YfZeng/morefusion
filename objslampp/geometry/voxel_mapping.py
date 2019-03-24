import numpy as np
import trimesh

from .. import extra


class VoxelMapping(object):

    def __init__(
        self,
        origin=None,
        pitch=None,
        voxel_size=None,
        nchannel=None,
    ):
        self.origin = origin
        self.voxel_size = voxel_size
        self.pitch = pitch
        self.nchannel = nchannel

        self._matrix = None
        self._values = None

    @property
    def matrix(self):
        if self._matrix is None:
            self._matrix = np.zeros((self.voxel_size,) * 3, dtype=float)
        return self._matrix

    @property
    def values(self):
        if self._values is None:
            self._values = np.zeros(
                (self.voxel_size,) * 3 + (self.nchannel,), dtype=float
            )
        return self._values

    @property
    def voxel_bbox_extents(self):
        return np.array((self.voxel_size * self.pitch,) * 3, dtype=float)

    def add(self, points, values):
        indices = trimesh.voxel.points_to_indices(
            points, self.pitch, self.origin
        )
        keep = ((indices >= 0) & (indices < self.voxel_size)).all(axis=1)
        indices = indices[keep]
        I, J, K = zip(*indices)
        self.matrix[I, J, K] = True
        self.values[I, J, K] = values[keep]

    def as_boxes(self):
        geom = trimesh.voxel.Voxel(
            self.matrix, self.pitch, self.origin
        )
        geom = geom.as_boxes()
        I, J, K = zip(*np.argwhere(self.matrix))
        geom.visual.face_colors = \
            self.values[I, J, K].repeat(12, axis=0)
        return geom

    def as_bbox(self, edge=True, face_color=None, origin_color=(1.0, 0, 0)):
        geometries = []

        if edge:
            bbox_edge = extra.trimesh.wired_box(
                self.voxel_bbox_extents,
                translation=self.origin + self.voxel_bbox_extents / 2,
            )
            geometries.append(bbox_edge)

        if face_color is not None:
            bbox = trimesh.creation.box(self.voxel_bbox_extents)
            bbox.apply_translation(self.origin + self.voxel_bbox_extents / 2)
            bbox.visual.face_colors = face_color
            geometries.append(bbox)

        origin = trimesh.creation.icosphere(radius=0.01)
        origin.apply_translation(self.origin)
        origin.visual.face_colors = origin_color
        geometries.append(origin)

        return geometries
