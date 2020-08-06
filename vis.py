import numpy as np
import lightmetrica as lm
import pythreejs as three
import math
from IPython.display import display
import ipywidgets as widgets

def normalize(v):
    return v / np.linalg.norm(v)


def lookat_matrix(position, center, up):
    w = normalize(position - center)
    u = normalize(np.cross(up, w))
    v = np.cross(w, u)
    return np.column_stack([u, v, w])


def display_scene(lm_scene):
    """Display Lightmetrica scene."""

    # Scene
    scene = three.Scene()


    # Camera
    # Get lm camera information
    lm_main_camera = lm_scene.camera()
    lm_camera_params = lm_main_camera.underlying_value()
    camera = three.PerspectiveCamera(
        fov=lm_camera_params['vfov'],
        aspect=lm_camera_params['aspect'],
        near=0.1,
        far=10000
    )
    camera.position = lm_camera_params['eye']
    camera.up = lm_camera_params['up']
    
    scene.add(camera)


    # Mesh
    def add_lm_scene_mesh():
        # Default material
        mat_default = three.MeshBasicMaterial(
            color='#000000',
            wireframe=True,
            transparent=True,
            opacity=0.2,
            depthTest=False
        )

        # Convert lm mesh
        def traverse_func(node, trans):
            # Underlying mesh
            mesh = node.primitive.mesh
            if mesh is None:
                return
            
            # Iterate through all triangles
            vs = []
            def process_triangle(face_index, tri):
                vs.append(list(tri.p1.p))
                vs.append(list(tri.p2.p))
                vs.append(list(tri.p3.p))
            mesh.foreach_triangle(process_triangle)
            
            # Create geometry
            ps_attr = three.BufferAttribute(array=vs, normalized=False)
            geom = three.BufferGeometry(
                attributes={'position': ps_attr}
            )
            
            # Create mesh
            mesh = three.Mesh(
                geometry=geom,
                material=mat_default
            )
            mesh.matrixAutoUpdate = False
            mesh.matrix = trans.T.flatten().tolist()
            scene.add(mesh)

        lm_scene.traverse_primitive_nodes(traverse_func)

    add_lm_scene_mesh()


    # View frustum
    def add_view_frustum():
        position = np.array(lm_camera_params['eye'])
        center = np.array(lm_camera_params['center'])
        up = np.array(lm_camera_params['up'])
        aspect = lm_camera_params['aspect']
        fov = math.radians(lm_camera_params['vfov'])

        M = lookat_matrix(position, center, up)
        z = 5
        half_fov = fov * .5
        y = math.tan(half_fov) * z
        x = aspect * y

        p  = list(position)
        p1 = list(position + np.dot(M, [-x,-y,-z]))
        p2 = list(position + np.dot(M, [ x,-y,-z]))
        p3 = list(position + np.dot(M, [ x, y,-z]))
        p4 = list(position + np.dot(M, [-x, y,-z]))

        # Add mesh
        geom = three.Geometry(vertices=[
            p, p1, p2,
            p, p2, p3,
            p, p3, p4,
            p, p4, p1
        ])
        mat = three.MeshBasicMaterial(
            color='#00ff00',
            wireframe=True,
            side='DoubleSide'
        )
        mesh = three.Line(
            geometry=geom,
            material=mat
        )
        scene.add(mesh)
        
    add_view_frustum()


    # Axis
    axes = three.AxesHelper(size=1)
    scene.add(axes)


    # Renderer
    controls = three.OrbitControls(
        controlling=camera
    )

    # Rendered image size
    w = 1000
    h = w / lm_camera_params['aspect']

    # We need to set both target and lookAt in this order.
    # Otherwise the initial target position becomes wrong.
    # cf. https://github.com/jupyter-widgets/pythreejs/issues/200
    controls.target = lm_camera_params['center']
    camera.lookAt(lm_camera_params['center'])
    renderer = three.Renderer(
        camera=camera,
        scene=scene,
        width=w,
        height=h,
        controls=[controls]
    )

    # Button to reset camera configuration
    # Note that we need to press the button twice to reset the control
    # to the correct target possibly due to the bug of pythreejs.
    reset_camera_button = widgets.Button(description="Reset Camera")
    @reset_camera_button.on_click
    def reset_camera_button_on_click(b):
        controls.reset()
        controls.target = lm_camera_params['center']
        camera.lookAt(lm_camera_params['center'])

    # Display all
    display(reset_camera_button)
    display(renderer)

    return scene, camera, renderer


def display_portal(th_scene, portal):
    """Display portal."""
    def portal_vertices(portal):
        p1 = np.array(portal[0])
        p2 = np.array(portal[1])
        p4 = np.array(portal[2])
        p3 = p1 + (p2-p1) + (p4-p1)
        return [p1,p2,p3,p1,p3,p4]
    
    ps_attr = three.BufferAttribute(
        array=portal_vertices(portal), 
        normalized=False
    )
    geom = three.BufferGeometry(attributes={'position': ps_attr})
    mat = three.MeshBasicMaterial(
        color='#ff0000',
        transparent=True,
        opacity=0.1,
        side='DoubleSide'
    )
    mesh = three.Mesh(
        geometry=geom,
        material=mat
    )
    th_scene.add(mesh)

def display_portal_mesh(th_scene, portal_mesh):
    # Extract vertices
    if portal_mesh.num_triangles() != 2:
        raise RuntimeError('Number of triangles must be 2')
    tri = portal_mesh.triangle_at(0)
    display_portal(th_scene, [tri.p2.p, tri.p3.p, tri.p1.p])

def display_path(th_scene, vs, **kwargs):
    """Display path."""
    geom = three.Geometry(vertices=vs)
    mat_line = three.LineBasicMaterial(**kwargs)
    line = three.Line(geometry=geom, material=mat_line)
    th_scene.add(line)
    mat_points = three.PointsMaterial(**kwargs)
    points = three.Points(geometry=geom, material=mat_points)
    th_scene.add(points)

    
def display_ray(th_scene, o, d, **kwargs):
    """Display ray."""
    o2 = o + np.array(d) * kwargs['scale']
    display_path(th_scene, [o, o2.tolist()], **kwargs)

