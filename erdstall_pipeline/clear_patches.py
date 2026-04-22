import os.path
import pymeshlab

from .config import PATCHES_DIR

def clear_patches(filled_holes_input_file, output_file, unused_patches):
    first_iteration = True

    for patch in unused_patches:
        ms = pymeshlab.MeshSet()

        if first_iteration:
            first_iteration = False
            ms.load_new_mesh(filled_holes_input_file)
        else:
            ms.load_new_mesh(output_file)

        ms.load_new_mesh(os.path.join(os.path.dirname(filled_holes_input_file), PATCHES_DIR, patch))
        ms.set_current_mesh(0)
        ms.set_selection_none()

        ms.get_hausdorff_distance(
            sampledmesh=0,
            targetmesh=1,
            savesample=True,
            maxdist=pymeshlab.PercentageValue(1)
        )

        ms.compute_selection_by_scalar_per_vertex(maxq=0.01)
        ms.meshing_remove_selected_vertices_and_faces()

        while ms.mesh_number() > 1:
            ms.set_current_mesh(ms.mesh_number() - 1)
            ms.delete_current_mesh()

        ms.set_current_mesh(0)
        ms.save_current_mesh(
            output_file,
            save_vertex_color=True,
            save_wedge_texcoord=False,
            save_textures=False
        )