from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FillHolesSettings:
    point_cloud_depth: int = 10
    point_cloud_fulldepth: int = 5
    point_cloud_scale: float = 1.1
    point_cloud_samplespernode: float = 1.5
    point_cloud_pointweight: float = 4.0
    point_cloud_iters: int = 8
    point_cloud_preclean: bool = True

    poisson_depth: int = 12
    poisson_fulldepth: int = 5
    poisson_cgdepth: int = 0
    poisson_scale: float = 1.1
    poisson_samplespernode: float = 1.5
    poisson_pointweight: float = 4.0
    poisson_iters: int = 8
    poisson_preclean: bool = True

    transfer_texture_to_vertex_colors: bool = True