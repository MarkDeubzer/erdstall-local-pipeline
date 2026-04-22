from __future__ import annotations

from collections.abc import Callable

import pymeshlab

from .settings.fill_holes_settings import FillHolesSettings


LogCallback = Callable[[str], None] | None



def fill_holes(
 input_file: str,
 output_file: str,
 settings: FillHolesSettings | None = None,
 log_callback: LogCallback = None
) -> None:
    
    def log(message: str) -> None:
        if log_callback is not None:
            log_callback(message)
        else:
            print(message)
    
    ms = pymeshlab.MeshSet()
    log("Loading mesh...")
    ms.load_new_mesh(input_file)
    log("Loading mesh done.")

    original_index = 0
    original_mesh = ms.mesh(original_index)
    input_is_point_cloud = original_mesh.face_number() == 0


    if input_is_point_cloud:
        log("Detected point cloud -> reconstructing surface...")
        ms.generate_surface_reconstruction_screened_poisson(
            depth=settings.point_cloud_depth,
            fulldepth=settings.point_cloud_fulldepth,
            scale=settings.point_cloud_scale,
            samplespernode=settings.point_cloud_samplespernode,
            pointweight=settings.point_cloud_pointweight,
            iters=settings.point_cloud_iters,
            preclean=settings.point_cloud_preclean
        )

        reconstructed_index = ms.number_meshes() - 1
        ms.set_current_mesh(reconstructed_index)

        log("Point cloud converted to mesh.")
    else:
        reconstructed_index = original_index

    log("Computing normals...")
    ms.compute_normal_per_face()
    ms.compute_normal_per_vertex()
    log("Computing normals done.")


    log("Cleaning mesh...")
    ms.meshing_remove_unreferenced_vertices()
    log("Cleaning mesh done.")


    log("Repairing topology...")
    ms.meshing_repair_non_manifold_edges()
    ms.meshing_repair_non_manifold_vertices()
    log("Repairing topology done.")

    
    log("Running Poisson reconstruction...")
    try:
        ms.generate_surface_reconstruction_screened_poisson(
            depth=settings.poisson_depth,
            fulldepth=settings.poisson_fulldepth,
            cgdepth=settings.poisson_cgdepth,
            scale=settings.poisson_scale,
            samplespernode=settings.poisson_samplespernode,
            pointweight=settings.poisson_pointweight,
            iters=settings.poisson_iters,
            preclean=settings.poisson_preclean,
        )
    finally:
       log("Poisson reconstruction done.")

    final_mesh_index = ms.number_meshes() - 1
    ms.set_current_mesh(final_mesh_index)

    source_mesh = ms.mesh(reconstructed_index)
    if settings.transfer_texture_to_vertex_colors and source_mesh.face_number() > 0:
        log("Transferring texture to vertex colors...")
        try:
            ms.transfer_texture_to_color_per_vertex(
                sourcemesh=reconstructed_index,
                targetmesh=final_mesh_index
            )
            log("Transferring texture to vertex colors done.")
        except Exception as e:
            log(f"Skipping texture transfer: {e}")
    else:
        log("Skipping texture transfer.")

    ms.set_current_mesh(final_mesh_index)

    log("Final cleanup...")
    ms.meshing_remove_duplicate_faces()
    ms.meshing_remove_duplicate_vertices()
    ms.meshing_remove_unreferenced_vertices()
    log("Final cleanup done.")

    log("Saving repaired mesh...")
    ms.save_current_mesh(
        output_file,
        save_vertex_color=True,
        save_wedge_texcoord=False,
        save_textures=False
    )
    log(f"Saved: {output_file}")