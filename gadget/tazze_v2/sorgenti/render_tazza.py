# Foto realistica della tazza 11oz con Blender (Cycles): ceramica lucida, stampa avvolta sul cilindro, bancone di legno, bar sfocato dietro.
# Uso: python3 render_tazza.py stampa.png out.png [angolo_gradi] [sfondo.jpg] [legno_dir] [campioni] [lato_px]
import sys, math, bpy
from mathutils import Vector
stampa, out = sys.argv[1], sys.argv[2]
ang = float(sys.argv[3]) if len(sys.argv) > 3 else -25
SFONDO = sys.argv[4] if len(sys.argv) > 4 else "sfondo.jpg"
LEGNO = sys.argv[5] if len(sys.argv) > 5 else "wood/Wood020_1K-JPG_Wood020_1K-JPG_"
SAMPLES = int(sys.argv[6]) if len(sys.argv) > 6 else 160
RES = int(sys.argv[7]) if len(sys.argv) > 7 else 1600

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = True
sc.render.resolution_x = RES; sc.render.resolution_y = RES
sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'; sc.view_settings.exposure = -0.6

R, Hm, T = 0.041, 0.095, 0.0035      # raggio, altezza, spessore parete (11 oz)
PW, PH = 0.216, 0.089                # area stampa 21,6 x 8,9 cm
ZP = 0.0045 + (Hm - 0.009 - PH) / 2  # base della stampa

def nodes(mat):
    mat.use_nodes = True; nt = mat.node_tree; nt.nodes.clear(); return nt, nt.nodes, nt.links

# ---------- tazza: profilo ruotato (parete, bordo arrotondato, fondo) ----------
prof = []
prof.append((0.0, 0.0)); prof.append((R - 0.004, 0.0)); prof.append((R - 0.0012, 0.0006)); prof.append((R, 0.004))
prof.append((R, Hm - 0.0015))
for i in range(1, 10):  # bordo arrotondato
    a = math.pi * i / 10; prof.append((R - T / 2 + (T / 2) * math.cos(a), Hm - 0.0015 + (T / 2) * math.sin(a) * 0.9))
prof.append((R - T, Hm - 0.0015)); prof.append((R - T, 0.009)); prof.append((R - T - 0.004, 0.0065)); prof.append((0.0, 0.0065))
import bmesh
me = bpy.data.meshes.new("tazza"); bm = bmesh.new()
N = 256
rings = []
for k in range(N):
    th = 2 * math.pi * k / N
    rings.append([bm.verts.new((r * math.cos(th), r * math.sin(th), z)) for (r, z) in prof])
for k in range(N):
    a, b = rings[k], rings[(k + 1) % N]
    for j in range(len(prof) - 1):
        try: bm.faces.new((a[j], b[j], b[j + 1], a[j + 1]))
        except ValueError: pass
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
bm.to_mesh(me); bm.free()
mug = bpy.data.objects.new("tazza", me); sc.collection.objects.link(mug)
for p in me.polygons: p.use_smooth = True
mod = mug.modifiers.new("ss", 'SUBSURF'); mod.levels = 1; mod.render_levels = 1

# ---------- manico: tubo ellittico a D, attaccato a +X... poi ruotiamo tutto ----------
cu = bpy.data.curves.new("manico", 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.0056; cu.bevel_resolution = 8
sp = cu.splines.new('BEZIER'); pts = [(R - 0.003, 0, 0.078), (R + 0.030, 0, 0.074), (R + 0.034, 0, 0.040), (R + 0.020, 0, 0.020), (R - 0.003, 0, 0.022)]
sp.bezier_points.add(len(pts) - 1)
for bp, p in zip(sp.bezier_points, pts):
    bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
man = bpy.data.objects.new("manico", cu); sc.collection.objects.link(man)
man.scale = (1, 1.25, 1)  # sezione ovale

# ---------- materiale ceramica con stampa ----------
img = bpy.data.images.load(stampa)
m = bpy.data.materials.new("ceramica"); nt, n, l = nodes(m)
o = n.new('ShaderNodeOutputMaterial'); bs = n.new('ShaderNodeBsdfPrincipled')
bs.inputs['Roughness'].default_value = 0.06; bs.inputs['Coat Weight'].default_value = 0.6; bs.inputs['Coat Roughness'].default_value = 0.03
bs.inputs['Subsurface Weight'].default_value = 0.05
tc = n.new('ShaderNodeTexCoord'); sx = n.new('ShaderNodeSeparateXYZ'); l.new(tc.outputs['Object'], sx.inputs[0])
at = n.new('ShaderNodeMath'); at.operation = 'ARCTAN2'; l.new(sx.outputs['Y'], at.inputs[0]); l.new(sx.outputs['X'], at.inputs[1])
# angolo 0 = lato opposto al manico (manico a +X => fronte a -X: atan2 = pi). u: lunghezza d'arco centrata sul fronte
def math_node(op, a=None, b=None, va=None, vb=None):
    mm = n.new('ShaderNodeMath'); mm.operation = op
    if a is not None: l.new(a, mm.inputs[0])
    else: mm.inputs[0].default_value = va
    if b is not None: l.new(b, mm.inputs[1])
    elif vb is not None: mm.inputs[1].default_value = vb
    return mm
# arc = (atan2 mod 2pi) - pi  -> 0 al fronte (-X)
a1 = math_node('ADD', at.outputs[0], vb=2 * math.pi); a2 = math_node('MODULO', a1.outputs[0], vb=2 * math.pi)
a3 = math_node('SUBTRACT', a2.outputs[0], vb=math.pi)
u = math_node('ADD', math_node('DIVIDE', math_node('MULTIPLY', a3.outputs[0], vb=R).outputs[0], vb=PW).outputs[0], vb=0.5)
v = math_node('DIVIDE', math_node('SUBTRACT', sx.outputs['Z'], vb=ZP).outputs[0], vb=PH)
cxyz = n.new('ShaderNodeCombineXYZ'); l.new(u.outputs[0], cxyz.inputs[0]); l.new(v.outputs[0], cxyz.inputs[1])
ti = n.new('ShaderNodeTexImage'); ti.image = img; img.alpha_mode = 'STRAIGHT'; ti.extension = 'CLIP'; ti.interpolation = 'Cubic'
l.new(cxyz.outputs[0], ti.inputs['Vector'])
# solo parete esterna
ln = n.new('ShaderNodeVectorMath'); ln.operation = 'LENGTH'
cx2 = n.new('ShaderNodeCombineXYZ'); l.new(sx.outputs['X'], cx2.inputs[0]); l.new(sx.outputs['Y'], cx2.inputs[1]); l.new(cx2.outputs[0], ln.inputs[0])
est = math_node('GREATER_THAN', ln.outputs['Value'], vb=R - 0.0008)
mk = math_node('MULTIPLY', ti.outputs['Alpha'], est.outputs[0])
mix = n.new('ShaderNodeMix'); mix.data_type = 'RGBA'
mix.inputs[6].default_value = (0.86, 0.86, 0.85, 1)
l.new(mk.outputs[0], mix.inputs['Factor']); l.new(ti.outputs['Color'], mix.inputs[7])
l.new(mix.outputs[2], bs.inputs['Base Color']); l.new(bs.outputs[0], o.inputs[0])
mug.data.materials.append(m); man.data.materials.append(m)

# ---------- caffe' ----------
bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=R - T - 0.0002, depth=0.002, location=(0, 0, Hm - 0.012))
caf = bpy.context.object
mc = bpy.data.materials.new("caffe"); nt, n, l = nodes(mc)
o = n.new('ShaderNodeOutputMaterial'); bs = n.new('ShaderNodeBsdfPrincipled')
bs.inputs['Base Color'].default_value = (0.010, 0.004, 0.0015, 1); bs.inputs['Roughness'].default_value = 0.12; bs.inputs['Specular IOR Level'].default_value = 0.35
l.new(bs.outputs[0], o.inputs[0]); caf.data.materials.append(mc)

# gruppo tazza ruotato: manico a destra-dietro, fronte verso camera ruotato di 'ang'
for ob in (mug, man, caf):
    ob.rotation_euler[2] = math.radians(180 + ang)  # fronte (-X) -> verso la camera (+Y?) gestito sotto
# camera guarda da -Y: il fronte (-X locale) deve andare verso -Y => ruota di +90
for ob in (mug, man, caf):
    ob.rotation_euler[2] = math.radians(90 + ang)

# ---------- bancone di legno ----------
bpy.ops.mesh.primitive_plane_add(size=2.0, location=(0, 0.3, 0)); tav = bpy.context.object
mt = bpy.data.materials.new("legno"); nt, n, l = nodes(mt)
o = n.new('ShaderNodeOutputMaterial'); bs = n.new('ShaderNodeBsdfPrincipled')
tc = n.new('ShaderNodeTexCoord'); mp = n.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (8.0, 8.0, 1)
mp.inputs['Rotation'].default_value = (0, 0, 0)
l.new(tc.outputs['UV'], mp.inputs[0])
def tex(nome, col=True):
    t = n.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(LEGNO + nome + ".jpg")
    if not col: t.image.colorspace_settings.name = 'Non-Color'
    l.new(mp.outputs[0], t.inputs[0]); return t
c = tex("Color"); r = tex("Roughness", False); nm = tex("NormalGL", False)
hs = n.new('ShaderNodeHueSaturation'); hs.inputs['Value'].default_value = 0.95; hs.inputs['Saturation'].default_value = 0.85
l.new(c.outputs[0], hs.inputs['Color']); l.new(hs.outputs[0], bs.inputs['Base Color'])
rm = n.new('ShaderNodeMapRange'); rm.inputs['To Min'].default_value = 0.35; rm.inputs['To Max'].default_value = 0.65
l.new(r.outputs[0], rm.inputs[0]); l.new(rm.outputs[0], bs.inputs['Roughness'])
bs.inputs['Coat Weight'].default_value = 0.15; bs.inputs['Coat Roughness'].default_value = 0.25
nmn = n.new('ShaderNodeNormalMap'); nmn.inputs['Strength'].default_value = 0.6
l.new(nm.outputs[0], nmn.inputs['Color']); l.new(nmn.outputs[0], bs.inputs['Normal'])
l.new(bs.outputs[0], o.inputs[0]); tav.data.materials.append(mt)

# ---------- sfondo: foto vera del locale su un pannello lontano (sfocato dalla profondita' di campo) ----------
bg = bpy.data.images.load(SFONDO); ar = bg.size[0] / bg.size[1]
Hb = 0.75; bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0.75, Hb / 2 - 0.02), rotation=(math.radians(90), 0, 0))
pan = bpy.context.object; pan.scale = (Hb * ar, Hb, 1)
mb = bpy.data.materials.new("sfondo"); nt, n, l = nodes(mb)
o = n.new('ShaderNodeOutputMaterial'); em = n.new('ShaderNodeEmission'); ti = n.new('ShaderNodeTexImage'); ti.image = bg
em.inputs['Strength'].default_value = 0.9
l.new(ti.outputs[0], em.inputs[0]); l.new(em.outputs[0], o.inputs[0]); pan.data.materials.append(mb)
pan.visible_shadow = False

# ---------- luci ----------
def area(loc, size, energy, col, tgt=(0, 0, 0.05)):
    ld = bpy.data.lights.new("a", 'AREA'); ld.size = size; ld.energy = energy; ld.color = col
    ob = bpy.data.objects.new("a", ld); sc.collection.objects.link(ob); ob.location = loc
    d = Vector(tgt) - Vector(loc); ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler(); return ob
area((-0.35, -0.25, 0.35), 0.35, 38, (1.0, 0.86, 0.68))   # chiave calda da sinistra
area((0.40, -0.30, 0.12), 0.4, 5, (0.9, 0.93, 1.0))      # riempimento
area((0.25, 0.35, 0.45), 0.25, 10, (1.0, 0.78, 0.5))      # controluce dal bar
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (0.09, 0.06, 0.04, 1); w.node_tree.nodes['Background'].inputs[1].default_value = 0.6

# ---------- camera ----------
cd = bpy.data.cameras.new("cam"); cd.lens = 112; cd.sensor_width = 36
cd.dof.use_dof = True; cd.dof.aperture_fstop = 4.0
cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
cam.location = (0.0, -0.62, 0.25)
tgt = Vector((0.006, 0, 0.050)); d = tgt - cam.location
cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
cd.dof.focus_distance = (Vector((0, -R, 0.05)) - cam.location).length
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print("ok", out)
