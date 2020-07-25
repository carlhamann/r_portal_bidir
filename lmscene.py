import os
import numpy as np
import lightmetrica as lm

def scenes():
    return [
        'fireplace_room',
        'cornell_box_sphere',
        'bedroom',
        'vokselia_spawn',
        'breakfast_room',
        'buddha',
        'bunny',
        'cloud',
        'conference',
        'cube',
        'powerplant'
    ]

def scenes_small():
    return [
        'fireplace_room',
        'cornell_box_sphere',
        'cube',
    ]

def load(scene, scene_path, name):
    return globals()[name](scene, scene_path)

def scene_create_func(scene_name):
    return globals()[scene_name]

def fireplace_room(scene, scene_path):
    camera = lm.load_camera('camera_main', 'pinhole', {
        'position': [5.101118, 1.083746, -2.756308],
        'center': [4.167568, 1.078925, -2.397892],
        'up': [0,1,0],
        'vfov': 43.001194,
        'aspect': 16/9
    })
    model = lm.load_model('model_obj', 'wavefrontobj', {
        'path': os.path.join(scene_path, 'fireplace_room/fireplace_room.obj')
    })
    scene.add_primitive({
        'camera': camera.loc()
    })
    scene.add_primitive({
        'model': model.loc()
    })

def cornell_box_sphere(scene, scene_path):
    camera = lm.load_camera('camera_main', 'pinhole', {
        'position': [0,1,5],
        'center': [0,1,0],
        'up': [0,1,0],
        'vfov': 30,
        'aspect': 16/9
    })
    model = lm.load_model('model_obj', 'wavefrontobj', {
        'path': os.path.join(scene_path, 'cornell_box/CornellBox-Sphere.obj')
    })
    scene.add_primitive({
        'camera': camera.loc()
    })
    scene.add_primitive({
        'model': model.loc()
    })

# -------------------------------------------------------------------------------------------------

def cornell_box_empty_white(scene, scene_path):
    camera = lm.load_camera('camera_main', 'pinhole', {
        'position': [0,1,5],
        'center': [0,1,0],
        'up': [0,1,0],
        'vfov': 30,
        'aspect': 16/9
    })
    model = lm.load_model('model_obj', 'wavefrontobj', {
        'path': os.path.join(scene_path, 'cornell_box/CornellBox-Empty-White.obj')
    })
    scene.add_primitive({
        'camera': camera.loc()
    })
    scene.add_primitive({
        'model': model.loc()
    })

def cornell_box_empty_glossy(scene):
    camera = lm.load_camera('camera_main', 'pinhole', {
        'position': [0,1,5],
        'center': [0,1,0],
        'up': [0,1,0],
        'vfov': 30
    })
    model = lm.load_model('model_obj', 'wavefrontobj', {
        'path': os.path.join('scene', 'cornell_box/CornellBox-Empty-Glossy.obj')
    })
    scene.add_primitive({
        'camera': camera.loc()
    })
    scene.add_primitive({
        'model': model.loc()
    })
    
def cornell_box_glossy(scene, scene_path):
    camera = lm.load_camera('camera_main', 'pinhole', {
        'position': [0,1,5],
        'center': [0,1,0],
        'up': [0,1,0],
        'vfov': 30
    })
    model = lm.load_model('model_obj', 'wavefrontobj', {
        'path': os.path.join('scene', 'cornell_box/CornellBox-Glossy.obj'),
        'skip_specular_mat': True
    })
    scene.add_primitive({
        'camera': camera.loc()
    })
    scene.add_primitive({
        'model': model.loc()
    })
    
def fireplace_room_diffuse(scene, scene_path):
    camera = lm.load_camera('camera_main', 'pinhole', {
        'position': [5.101118, 1.083746, -2.756308],
        'center': [4.167568, 1.078925, -2.397892],
        'up': [0,1,0],
        'vfov': 43.001194
    })
    model = lm.load_model('model_obj', 'wavefrontobj', {
        'path': os.path.join(scene_path, 'fireplace_room/fireplace_room.obj'),
        'skip_specular_mat': True
    })
    scene.add_primitive({
        'camera': camera.loc()
    })
    scene.add_primitive({
        'model': model.loc()
    })
    
def single_plane_light(scene, scene_path):
    camera = lm.load_camera('camera_main', 'pinhole',
        position=[0,0,5],
        center=[0,0,0],
        up=[0,1,0],
        vfov=30,
        aspect=16/9)
    model = lm.load_model('model_obj', 'wavefrontobj',
        path=os.path.join(scene_path, 'single_plane_light.obj'))
    scene.add_primitive(camera=camera.loc())
    scene.add_primitive(model=model.loc())

def single_plane_light_transformed(scene):
    camera = lm.load_camera('camera_main', 'pinhole', {
        'position': [0,0,5],
        'center': [0,0,0],
        'up': [0,1,0],
        'vfov': 30,
        'aspect': 16/9
    })
    model = lm.load_model('model_obj', 'wavefrontobj', {
        'path': os.path.join('scene', 'single_plane_light.obj')
    })
    scene.add_primitive({'camera': camera.loc()})
    scene.add_transformed_primitive(
        lm.translate(np.array([0.0,1.0,0.0])) @
        lm.rotate(lm.rad(90), np.array([1.0,0.0,0.0])),
        {'model': model.loc()})

def cornell_box_sphere_refract(scene):
    camera = lm.load_camera('camera_main', 'pinhole', {
        'position': [0,1,5],
        'center': [0,1,0],
        'up': [0,1,0],
        'vfov': 30
    })
    model = lm.load_model('model_obj', 'wavefrontobj', {
        'path': os.path.join('scene', 'cornell_box/CornellBox-Sphere.obj'),
        'skip_specular_mat': True
    })
    scene.add_primitive({
        'camera': camera.loc()
    })
    scene.add_primitive({
        'model': model.loc()
    })

def cornell_box_sphere_reflect(scene):
    camera = lm.load_camera('camera_main', 'pinhole', {
        'position': [0,1,5],
        'center': [0,1,0],
        'up': [0,1,0],
        'vfov': 30
    })
    model = lm.load_model('model_obj', 'wavefrontobj', {
        'path': os.path.join('scene', 'cornell_box/CornellBox-Sphere2.obj')
    })
    scene.add_primitive({
        'camera': camera.loc()
    })
    scene.add_primitive({
        'model': model.loc()
    })

def plane_with_hole(scene):
    camera = lm.load_camera('camera_main', 'pinhole', {
        'position': [0,2,5],
        'center': [0,0,0],
        'up': [0,1,0],
        'vfov': 90
    })
    model = lm.load_model('model_obj', 'wavefrontobj', {
        'path': os.path.join('scene', 'plane_with_hole.obj')
    })
    scene.add_primitive({
        'camera': camera.loc()
    })
    scene.add_primitive({
        'model': model.loc()
    })

def generate_plane_with_hole(scene, hole_size):
    """Generate a plane with a hole with configurable hole size."""

    camera = lm.load_camera('camera_main', 'pinhole', {
        'position': [0,0,1],
        'center': [0,0,0],
        'up': [0,1,0],
        'vfov': 60,
        'aspect': 1
    })
    scene.add_primitive({
        'camera': camera.loc()
    })

    def merge_mesh(p1, f1, p2, f2):
        """Merge two meshes."""
        l = len(p1)
        return np.concatenate((p1, p2)), np.concatenate((f1, f2 + l))

    def make_quad(a, b, z):
        """Make a quad with two triangles.
        .  -  b
        |  /  |
        a  -  .
        """
        return (np.array([[a[0],a[1],z], [b[0],a[1],z], [b[0],b[1],z], [a[0],b[1],z]]),
                np.array([[0,1,2],[0,2,3]]))

    def create_lm_raw_mesh(name, ps, fs, n):
        """Create mesh::raw asset from position and faces."""
        return lm.load_mesh(name, 'raw', {
            'ps': ps.flatten().tolist(),
            'ns': n,
            'ts': [0,0],
            'fs': {
                'p': fs.flatten().tolist(),
                'n': np.zeros(fs.size).tolist(),
                't': np.zeros(fs.size).tolist()
            }
        })

    # Common materials
    mat_black = lm.load_material('mat_black', 'diffuse', {'Kd': [0,0,0]})
    mat_white = lm.load_material('mat_white', 'diffuse', {'Kd': [1,1,1]})

    # Mesh and primitives
    def add_quad_with_hole_mesh():
        """ Add mesh with hole.
        We want to pierce a hole at the center of a quad [-1,1]^2 in the xy plane.
        The extent of the hole is [-hole_size,hole_size]^2.
        Note that the function doesn't use indices for the duplicated positions.
        """
        s = 10 
        p = [[hole_size,hole_size], [s,0], [s,s], [0,s]]
        rot = np.array([[0,-1],[1,0]])  # row major
        ps = np.array([]).reshape(0,3)
        fs = np.array([]).reshape(0,3)
        z = 1
        for i in range(4):
            ps, fs = merge_mesh(ps, fs, *make_quad(p[0],p[1],z))
            ps, fs = merge_mesh(ps, fs, *make_quad(p[0],p[2],z))
            ps, fs = merge_mesh(ps, fs, *make_quad(p[0],p[3],z))
            p = p @ rot
        mesh = create_lm_raw_mesh('quad_with_hole', ps, fs, [0,0,1])
        scene.add_primitive({
            'mesh': mesh.loc(),
            'material': mat_black.loc()
        })

        # Returns portal vertices
        hs = hole_size
        return [
            [-hs,-hs,z],
            [hs,-hs,z],
            [-hs,hs,z]
        ]
    

    def add_light():
        s = 10 
        ps, fs = make_quad([-s,-s],[s,s],5)
        mesh = create_lm_raw_mesh('quad_light', ps, fs, [0,0,-1])
        Ke = 10
        light = lm.load_light('light', 'area', {
            'Ke': [Ke,Ke,Ke],
            'mesh': mesh.loc()
        })
        scene.add_primitive({
            'mesh': mesh.loc(),
            'material': mat_black.loc(),
            'light': light.loc()
        })
        pass

    def add_diffuser():
        ps, fs = make_quad([-1,-1],[1,1],0)
        mesh = create_lm_raw_mesh('quad_diffuser', ps, fs, [0,0,1])
        scene.add_primitive({
            'mesh': mesh.loc(),
            'material': mat_white.loc()
        })

    portal = add_quad_with_hole_mesh()
    add_light()
    add_diffuser()

    return portal


def sphere(scene, scene_path):
    camera = lm.load_camera('camera_main', 'pinhole', {
        'position': [0,2,5],
        'center': [0,1,0],
        'up': [0,1,0],
        'vfov': 30,
        'aspect': 16/9
    })
    scene.add_primitive({
        'camera': camera.loc()
    })

    model = lm.load_model('model_obj', 'wavefrontobj', {
        'path': os.path.join(scene_path, 'sphere.obj')
    })
    mat_diffuse_white = lm.load_material('mat_diffuse_white', 'diffuse', {
        'Kd': [.8,.8,.8]
    })
    
    # floor
    tex = lm.load_texture('tex_floor', 'bitmap', {
        'path': os.path.join(scene_path, 'default.png')
    })
    mat_floor = lm.load_material('mat_floor', 'diffuse', {
        'mapKd': tex.loc()
    })
    scene.add_primitive({
        'mesh': model.make_loc('mesh_1'),
        'material': mat_floor.loc()
    })
    # sphere
    # mat = lm.load_material('mat_ut', 'glass', {
    #     'Ni': 2
    # })
    mat = lm.load_material('mat_ut', 'mirror', {})
    # mat = mat_diffuse_white
    # mat = lm.load_material('mat_ut', 'mask', {})
    scene.add_primitive({
        'mesh': model.make_loc('mesh_3'),
        'material': mat.loc()
    })

    # Light source
    Ke = 10
    mat_black = lm.load_material('mat_black', 'diffuse', {'Kd': [0,0,0]})
    light = lm.load_light('light', 'area', {
        'Ke': [Ke,Ke,Ke],
        'mesh': model.make_loc('mesh_2')
    })
    scene.add_primitive({
        'mesh':  model.make_loc('mesh_2'),
        'material': mat_black.loc(),
        'light': light.loc()
    })

def plane_with_back(scene, scene_path):
    camera = lm.load_camera('camera_main', 'pinhole', {
        'position': [0,2,5],
        'center': [0,1,0],
        'up': [0,1,0],
        'vfov': 30,
        'aspect': 16/9
    })
    scene.add_primitive({
        'camera': camera.loc()
    })

    model = lm.load_model('model_obj', 'wavefrontobj', {
        'path': os.path.join(scene_path, 'plane_with_back.obj')
    })
    mat_diffuse_white = lm.load_material('mat_diffuse_white', 'diffuse', {
        'Kd': [.8,.8,.8]
    })
    
    # floor
    tex = lm.load_texture('tex_floor', 'bitmap', {
        'path': os.path.join(scene_path, 'default.png')
    })
    mat_floor = lm.load_material('mat_floor', 'diffuse', {
        'mapKd': tex.loc()
    })
    scene.add_primitive({
        'mesh': model.make_loc('mesh_1'),
        'material': mat_floor.loc()
    })
    # sphere
    mat = lm.load_material('mat_ut', 'glass', {
        'Ni': 2
    })
    # mat = lm.load_material('mat_ut', 'mirror', {})
    # mat = mat_diffuse_white
    # mat = lm.load_material('mat_ut', 'mask', {})
    scene.add_primitive({
        'mesh': model.make_loc('mesh_3'),
        'material': mat.loc()
    })

    # Light source
    Ke = 10
    mat_black = lm.load_material('mat_black', 'diffuse', {'Kd': [0,0,0]})
    light = lm.load_light('light', 'area', {
        'Ke': [Ke,Ke,Ke],
        'mesh': model.make_loc('mesh_2')
    })
    scene.add_primitive({
        'mesh':  model.make_loc('mesh_2'),
        'material': mat_black.loc(),
        'light': light.loc()
    })

def veach_door(scene, scene_path):
    """Veach's door scene."""
    base_path = os.path.join(scene_path, 'veach_door', 'data')
    g = lm.load_asset_group('veach_door', 'default')
    
    # Camera
    camera = g.load_camera('camera_main', 'pinhole',
        position=[-71.39, 71.49, 205.3],
        center=[-71.1997, 71.4202, 204.321],
        #center=[-70, 71.4202, 204.321],
        up=[0.013401, 0.99756, -0.0685194],
        #vfov=25,
        vfov=30,
        aspect=16/9)
    scene.add_primitive(camera=camera.loc())

    # Materials
    def tex(name):
        return g.load_texture('tex_' + os.path.splitext(name)[0], 'bitmap',
            path=os.path.join(base_path, name))
    mat_copper = g.load_material('mat_copper', 'glossy',
        Ks=[.9, .7, .5],
        ax=0.8,
        ay=0.8)
    mat_wood1 = g.load_material('mat_wood1', 'diffuse', 
        mapKd=tex('72cf.jpg'))
    mat_wood2 = g.load_material('mat_wood2', 'diffuse', 
        mapKd=tex('72rdf.jpg'))
    mat_table_leg = g.load_material('mat_table_leg', 'diffuse',
        Kd=[.65,.65,.47])
    mat_teapot1 = g.load_material('mat_teapot1', 'glossy',
        Ks=[.8, .8, .8],
        ax=0.15,
        ay=0.15)
    mat_teapot2 = g.load_material('mat_teapot2', 'diffuse',
        mapKd=tex('marble.jpg'))
    mat_glass = g.load_material('mat_glass', 'glass',
        Ni=1.5)
    mat_door_frame = g.load_material('mat_door_frame', 'diffuse',
        Kd=[.3, .2, .1])
    mat_checker = g.load_material('mat_checker', 'diffuse',
        mapKd=tex('checker.png'))
    mat_white = g.load_material('mat_white', 'diffuse',
        Kd=[.73, .73, .73])
    mat_black = g.load_material('mat_black', 'diffuse',
        Kd=[0, 0, 0])
    mat_picture_frame = g.load_material('mat_picture_frame', 'diffuse',
        Kd=[.2, .1, .05])
    mat_picture_image = g.load_material('mat_picture_image', 'diffuse',
        mapKd=tex('pic.jpg'))

    # Meshes
    def mesh(name):
        return g.load_mesh(name, 'wavefrontobj',
            path=os.path.join(base_path, name + '.obj'))
    # Transform
    M = np.array([
        [1, 0, 0, 0],
        [0, 0, 1, 0],
        [0, -1, 0, 0],
        [0, 0, 0, 1]]).astype(np.float)
    # Table
    scene.add_transformed_primitive(M,
        material=mat_wood2,
        mesh=mesh('table'))
    scene.add_transformed_primitive(M,
        material=mat_table_leg,
        mesh=mesh('table_leg1'))
    scene.add_transformed_primitive(M,
        material=mat_table_leg,
        mesh=mesh('table_leg2'))
    scene.add_transformed_primitive(M,
        material=mat_table_leg,
        mesh=mesh('table_leg3'))
    scene.add_transformed_primitive(M,
        material=mat_table_leg,
        mesh=mesh('table_leg4'))
    # Teapot
    scene.add_transformed_primitive(M,
        material=mat_teapot1,
        mesh=mesh('teapot1'))
    scene.add_transformed_primitive(M,
        material=mat_teapot2,
        mesh=mesh('teapot2'))
    scene.add_transformed_primitive(M,
        material=mat_glass,
        mesh=mesh('teapot3'))
    # Door frame
    scene.add_transformed_primitive(M,
        material=mat_door_frame,
        mesh=mesh('door_frame_left'))
    scene.add_transformed_primitive(M,
        material=mat_door_frame,
        mesh=mesh('door_frame_right'))
    scene.add_transformed_primitive(M,
        material=mat_door_frame,
        mesh=mesh('door_frame_top'))
    # Door
    scene.add_transformed_primitive(M,
        material=mat_wood1,
        mesh=mesh('door'))
    # Hinge
    scene.add_transformed_primitive(M,
        material=mat_copper,
        mesh=mesh('door_hinge1'))
    scene.add_transformed_primitive(M,
        material=mat_copper,
        mesh=mesh('door_hinge2'))
    scene.add_transformed_primitive(M,
        material=mat_copper,
        mesh=mesh('door_hinge3'))
    # Knob
    scene.add_transformed_primitive(M,
        material=mat_copper,
        mesh=mesh('door_knob'))
    # Floor
    scene.add_transformed_primitive(M,
        material=mat_checker,
        mesh=mesh('floor'))
    scene.add_transformed_primitive(M,
        material=mat_white,
        mesh=mesh('floor01'))
    # Picture
    scene.add_transformed_primitive(M,
        material=mat_picture_frame,
        mesh=mesh('picture_frame'))
    scene.add_transformed_primitive(M,
        material=mat_picture_image,
        mesh=mesh('picture_image'))
    # Walls
    scene.add_transformed_primitive(M,
        material=mat_white,
        mesh=mesh('walls'))
    # Lamp
    mesh_lamp = mesh('lamp')
    light_lamp = g.load_light('light_lamp', 'area',
        mesh=mesh_lamp,
        Ke=[1420, 1552, 1642])
    scene.add_transformed_primitive(M,
        material=mat_black,
        mesh=mesh_lamp,
        light=light_lamp)

    # portal_mesh = [
    #     [113.718,-6.07255,-54.6317],
    #     [130.498,-6.07256,-73.566],
    #     [113.718,125.807,-54.6317]
    # ]
    # Portal mesh
    portal_mesh = g.load_mesh('portal', 'wavefrontobj',
        path=os.path.join(scene_path, 'veach_door', 'portal.obj'))

    return portal_mesh

# -------------------------------------------------------------------------------------------------

def breakfast_room(scene, scene_path, no_light=False):
    base_path = os.path.join(scene_path, 'breakfast_room_0625')
    g = lm.load_asset_group('breakfast_room', 'default')

    camera = g.load_camera('camera_main', 'pinhole',
        position=[-0.518201, 2.987403, 9.745724],
        center=[-0.518201, 2.918664, 8.748089],
        up=[0,1,0],
        vfov=27.278080,
        aspect=16/9)

    model = g.load_model('model_obj', 'wavefrontobj',
        path=os.path.join(base_path, 'breakfast_room.obj'))
    scene.add_primitive(camera=camera)
    scene.add_primitive(model=model)

    # Light
    if not no_light:
        Le = 50
        light_env = g.load_light('light_env', 'envconst', Le=[Le,Le,Le])
        scene.add_primitive(light=light_env)

    # Portal mesh
    portal_mesh = g.load_mesh('portal', 'wavefrontobj',
        path=os.path.join(base_path, 'portal.obj'))

    return portal_mesh

# -------------------------------------------------------------------------------------------------

def salle_de_bain(scene, scene_path, no_light=False):
    base_path = os.path.join(scene_path, 'salle_de_bain_0622')
    g = lm.load_asset_group('salle_de_bain', 'default')

    camera = g.load_camera('camera_main', 'pinhole',
        position=[16.282997, 14.476411, 52.534241],
        center=[15.891605, 14.432939, 51.615044],
        up=[0,1,0],
        vfov=27.278080,
        aspect=16/9)

    model = g.load_model('model_obj', 'wavefrontobj',
        path=os.path.join(base_path, 'salle_de_bain.obj'))
    scene.add_primitive(camera=camera)
    scene.add_primitive(model=model)

    # Light
    if not no_light:
        Le = 5
        light_env = g.load_light('light_env', 'envconst', Le=[Le,Le,Le])
        scene.add_primitive(light=light_env)

    # Portal mesh
    portal_mesh = g.load_mesh('portal', 'wavefrontobj',
        path=os.path.join(base_path, 'portal.obj'))

    return portal_mesh

def salle_de_bain_2(scene, scene_path, no_light=False):
    base_path = os.path.join(scene_path, 'salle_de_bain_0622_2')
    g = lm.load_asset_group('salle_de_bain', 'default')

    camera = g.load_camera('camera_main', 'pinhole',
        position=[16.282997, 14.476411, 52.534241],
        center=[15.891605, 14.432939, 51.615044],
        up=[0,1,0],
        vfov=27.278080,
        aspect=16/9)

    model = g.load_model('model_obj', 'wavefrontobj',
        path=os.path.join(base_path, 'salle_de_bain.obj'))
    scene.add_primitive(camera=camera)
    scene.add_primitive(model=model)

    # Light
    if not no_light:
        Le = 50
        light_env = g.load_light('light_env', 'envconst', Le=[Le,Le,Le])
        scene.add_primitive(light=light_env)

    # Portal mesh
    portal_mesh = g.load_mesh('portal', 'wavefrontobj',
        path=os.path.join(base_path, 'portal.obj'))

    return portal_mesh

# -------------------------------------------------------------------------------------------------

def mitsuba_knob_base(scene, scene_path, **kwargs):
    # Camera
    camera = lm.load_camera('camera_main', 'pinhole', {
        'position': [0,4,5],
        'center': [0,0,-1],
        'up': [0,1,0],
        'vfov': 30,
        #'vfov': 1,
        'aspect': 16/9
    })
    scene.add_primitive({
        'camera': camera.loc()
    })
    
    # Model
    model = lm.load_model('model_obj', 'wavefrontobj', {
        'path': os.path.join(scene_path, 'mitsuba_knob', 'mitsuba.obj')
    })
    mat_diffuse_white = lm.load_material('mat_diffuse_white', 'diffuse', {
        'Kd': [.8,.8,.8]
    })
    scene.add_primitive({
        'mesh': model.make_loc('mesh_4'),
        #'material': mat_diffuse_white.loc()
        'material': model.make_loc('backdrop')
    })
    if 'mat_knob' in kwargs:
        scene.add_primitive({
            'mesh': model.make_loc('mesh_5'),
            'material': kwargs['mat_inside'] if 'mat_inside' in kwargs else mat_diffuse_white.loc()
        })
        scene.add_primitive({
            'mesh': model.make_loc('mesh_6'),
            'material': kwargs['mat_knob']
        })

def mitsuba_knob_with_area_light(scene, scene_path, **kwargs):
    mitsuba_knob_base(scene, scene_path, **kwargs)
    
    # Area light
    Ke = 10
    model_light = lm.load_model('model_light', 'wavefrontobj', {
        'path': os.path.join(scene_path, 'mitsuba_knob', 'light.obj')
    })
    mat_black = lm.load_material('mat_black', 'diffuse', {'Kd': [0,0,0]})
    light = lm.load_light('light', 'area', {
        'Ke': [Ke,Ke,Ke],
        'mesh': model_light.make_loc('mesh_1')
    })
    scene.add_primitive({
        'mesh':  model_light.make_loc('mesh_1'),
        'material': mat_black.loc(),
        'light': light.loc()
    })

def mitsuba_knob_with_env_light_const(scene, scene_path, **kwargs):
    mitsuba_knob_base(scene, scene_path, **kwargs)
    
    # Environment light
    Le = 1
    light_env = lm.load_light('light_env', 'envconst', {
        'Le': [Le,Le,Le] 
    })
    scene.add_primitive({
        'light': light_env.loc()
    })

def mitsuba_knob_with_env_light(scene, scene_path, **kwargs):
    mitsuba_knob_base(scene, scene_path, **kwargs)

    # Environment light
    light_env = lm.load_light('light_env', 'env', kwargs)
    scene.add_primitive({
        'light': light_env.loc()
    })

def mitsuba_knob_with_point_light(scene, scene_path, **kwargs):
    mitsuba_knob_base(scene, scene_path, **kwargs)

    # Point light
    Le = 100
    light_point = lm.load_light('light_point', 'point', {
        'Le': [Le,Le,Le],
        'position': [5,5,5]
    })
    scene.add_primitive({
        'light': light_point.loc()
    })

def mitsuba_knob_with_directional_light(scene, scene_path, **kwargs):
    mitsuba_knob_base(scene, scene_path, **kwargs)

    # Directional light
    Le = 2
    light_directional = lm.load_light('light_directional', 'directional', {
        'Le': [Le,Le,Le],
        'direction': [-1,-1,-1]
    })
    scene.add_primitive({
        'light': light_directional.loc()
    })

# -------------------------------------------------------------------------------------------------

def portal_box(scene, scene_path, **kwargs):
    mitsuba_knob_base(scene, scene_path, **kwargs)

    base_path = os.path.join(scene_path, 'portal_box')
    g = lm.load_asset_group('portal_box', 'default')

    # Camera
    # camera = g.load_camera('camera_main', 'pinhole',
    #     position=[1,1,1],
    #     #position=[10,10,10],
    #     center=[0,0,0],
    #     up=[0,1,0],
    #     #vfov=30,
    #     vfov=60,
    #     aspect=16/9)
    # scene.add_primitive(camera=camera.loc())

    # Cube
    mat = g.load_material('mat_white', 'diffuse', Kd=[.8,.8,.8])
    cube = g.load_mesh('cube', 'wavefrontobj', path=os.path.join(base_path, 'cube.obj'))
    scene.add_primitive(mesh=cube, material=mat)

    # Light
    Le = 50
    light_env = g.load_light('light_env', 'envconst', Le=[Le,Le,Le])
    scene.add_primitive(light=light_env)

    # Portal mesh
    portal_mesh = g.load_mesh('portal', 'wavefrontobj', path=os.path.join(base_path, 'portal.obj'))

    return portal_mesh


def portal_box_dragon(scene, scene_path, no_light=False, **kwargs):
    base_path = os.path.join(scene_path, 'dragon_in_box')
    g = lm.load_asset_group('dragon', 'default')

    # Load dragon scene
    camera = lm.load_camera('camera_main', 'pinhole',
        position=[-0.191925, 2.961061, 4.171464],
        center=[-0.185709, 2.478091, 3.295850],
        up=[0,1,0],
        vfov=28.841546,
        aspect=16/9)
    scene.add_primitive(camera=camera)

    # Model
    model = g.load_model('model_obj', 'wavefrontobj',
        path=os.path.join(base_path, 'dragon_with_plane.obj'))
    
    # Floor
    tex = lm.load_texture('tex_floor', 'bitmap',
        path=os.path.join(base_path, 'default.png'))
    mat_floor = lm.load_material('mat_floor', 'diffuse', mapKd=tex)
    scene.add_primitive(
        mesh=model.make_loc('mesh_2'),
        material=mat_floor)

    # Dragon
    mat = lm.load_material('mat_ut', 'glossy', Ks=[.8,.8,.8], ax=0.2, ay=0.2)
    #mat_white = g.load_material('mat_white', 'diffuse', Kd=[.8,.8,.8])
    scene.add_primitive(
        mesh=model.make_loc('mesh_4'),
        material=mat)

    # Light
    if not no_light:
        Le = 50
        light_env = g.load_light('light_env', 'envconst', Le=[Le,Le,Le])
        scene.add_primitive(light=light_env)

    # Cube
    mat = g.load_material('mat_white', 'diffuse', Kd=[.8,.8,.8])
    cube = g.load_mesh('cube', 'wavefrontobj', path=os.path.join(base_path, 'cube.obj'))
    scene.add_primitive(mesh=cube, material=mat)

    # Portal mesh
    portal_mesh = g.load_mesh('portal', 'wavefrontobj', path=os.path.join(base_path, 'portal.obj'))

    return portal_mesh

def portal_box_dragon_2(scene, scene_path, no_light=False, **kwargs):
    base_path = os.path.join(scene_path, 'dragon_in_box')
    g = lm.load_asset_group('dragon', 'default')

    # Load dragon scene
    camera = lm.load_camera('camera_main', 'pinhole',
        position=[-0.191925, 2.961061, 4.171464],
        center=[-0.185709, 2.478091, 3.295850],
        up=[0,1,0],
        vfov=28.841546,
        aspect=16/9)
    scene.add_primitive(camera=camera)

    # Model
    model = g.load_model('model_obj', 'wavefrontobj',
        path=os.path.join(base_path, 'dragon_with_plane.obj'))
    
    # Floor
    tex = lm.load_texture('tex_floor', 'bitmap',
        path=os.path.join(base_path, 'default.png'))
    mat_floor = lm.load_material('mat_floor', 'diffuse', mapKd=tex)
    scene.add_primitive(
        mesh=model.make_loc('mesh_2'),
        material=mat_floor)

    # Dragon
    mat = lm.load_material('mat_ut', 'glossy', Ks=[.8,.8,.8], ax=0.2, ay=0.2)
    #mat_white = g.load_material('mat_white', 'diffuse', Kd=[.8,.8,.8])
    scene.add_primitive(
        mesh=model.make_loc('mesh_4'),
        material=mat)

    # Light
    if not no_light:
        Le = 1000
        light_env = g.load_light('light_env', 'envconst', Le=[Le,Le,Le])
        scene.add_primitive(light=light_env)

    # Cube
    mat = g.load_material('mat_white', 'diffuse', Kd=[.8,.8,.8])
    cube = g.load_mesh('cube', 'wavefrontobj', path=os.path.join(base_path, 'cube.obj'))
    scene.add_primitive(mesh=cube, material=mat)

    # Lid
    lid = g.load_mesh('lid', 'wavefrontobj', path=os.path.join(base_path, 'lid.obj'))
    scene.add_primitive(mesh=lid, material=mat)

    # Portal meshes
    portal_mesh = g.load_mesh('portal', 'wavefrontobj', path=os.path.join(base_path, 'portal.obj'))
    portal_mesh_2 = g.load_mesh('portal2', 'wavefrontobj', path=os.path.join(base_path, 'portal2.obj'))

    return [portal_mesh, portal_mesh_2]

# -------------------------------------------------------------------------------------------------

def plane2_portal(scene, scene_path):
    base_path = os.path.join(scene_path, 'plane2')
    camera = lm.load_camera('camera_main', 'pinhole', {
        'position': [0,0,5],
        'center': [0,0,0],
        'up': [0,1,0],
        'vfov': 30,
        'aspect': 16/9
    })
    model = lm.load_model('model_obj', 'wavefrontobj', {
        'path': os.path.join(base_path, 'plane2.obj')
    })
    scene.add_primitive({'camera': camera.loc()})
    scene.add_primitive({'model': model.loc()})

    # Portal mesh
    portal_mesh = lm.load_mesh('portal', 'wavefrontobj', path=os.path.join(base_path, 'portal.obj'))

    return portal_mesh

def portal_cube(scene, scene_path):
    base_path = os.path.join(scene_path, 'portal_cube')
    camera = lm.load_camera('camera_main', 'pinhole', {
        'position': [1,0,0],
        'center': [2,0,0],
        'up': [0,1,0],
        'vfov': 30,
        'aspect': 16/9
    })
    model = lm.load_model('model_obj', 'wavefrontobj', {
        'path': os.path.join(base_path, 'portal_cube.obj')
    })
    scene.add_primitive({'camera': camera.loc()})
    scene.add_primitive({'model': model.loc()})    

    # Portal mesh
    portal_mesh = lm.load_mesh('portal', 'wavefrontobj', path=os.path.join(base_path, 'portal.obj'))

    return portal_mesh
    
def portal_cube2(scene, scene_path):
    base_path = os.path.join(scene_path, 'portal_cube2')
    camera = lm.load_camera('camera_main', 'pinhole', {
        'position': [1,0,0],
        'center': [2,0,0],
        'up': [0,1,0],
        'vfov': 30,
        'aspect': 16/9
    })
    model = lm.load_model('model_obj', 'wavefrontobj', {
        'path': os.path.join(base_path, 'portal_cube.obj')
    })
    scene.add_primitive({'camera': camera.loc()})
    scene.add_primitive({'model': model.loc()})    

    # Portal mesh
    portal_mesh = lm.load_mesh('portal', 'wavefrontobj', path=os.path.join(base_path, 'portal.obj'))

    return portal_mesh