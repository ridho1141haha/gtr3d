"""K56F / FS150FG V1 reference reconstruction. Blender 4.5+, metres.
Run: blender --background --factory-startup --python build_k56f.py
All coordinates are authored at full scale; +X right, +Y front, +Z up.
See REFERENCES.md for scope, evidence and unresolved dimensional estimates.
"""
import bpy, math, json, sys, bmesh
from pathlib import Path
from mathutils import Vector, Matrix
from math import sin, cos, pi

OUT = Path(__file__).resolve().parent
RENDER = '--no-render' not in sys.argv
WB = 1.284
RF, RR = .2159 + .090*.80, .2159 + .120*.70
FRONT, REAR = Vector((0, WB/2, RF)), Vector((0, -WB/2, RR))
PIVOT = Vector((0, -.105, .390))
HEAD_LOW, HEAD_HIGH = Vector((0,.433,.740)), Vector((0,.368,.900))

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name != 'Collection': bpy.data.collections.remove(c)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
scene.unit_settings.length_unit = 'MILLIMETERS'
scene['vehicle'] = 'Honda Supra GTR 150 K56F / FS150FG V1'
scene['generation_lock'] = '2016 K56F reference geometry. No K56W / RS150R / Winner / Sonic donor geometry.'
scene['status'] = 'Reference-informed editable reconstruction; estimated surfaces, not OEM CAD or metrology certified.'
scene['baseline_mm'] = json.dumps(dict(length=2025,width=725,height=1102,wheelbase=1284,seat=780,clearance=150))
scene['engine_spec'] = '149.16 cc; DOHC 4 valve; liquid-cooled; PGM-FI; 57.3 x 57.8 mm; 11.3:1; 6 speed'
scene['reference_empty_mass_kg'] = 119.0
scene['reference_tank_litres'] = 4.5
COL = {}
for name in ['00_DATUMS','01_CHASSIS','02_FRONT_RUNNING_GEAR','03_REAR_RUNNING_GEAR','04_ENGINE_COOLING','05_DRIVETRAIN_EXHAUST','06_BODY_K56F','07_CONTROLS_LIGHTS','08_HARDWARE','09_REFERENCE_IMAGES','90_STUDIO']:
    c=bpy.data.collections.new(name); scene.collection.children.link(c); COL[name]=c

def empty(name,loc=(0,0,0),parent=None,size=.04):
    o=bpy.data.objects.new(name,None);COL['00_DATUMS'].objects.link(o)
    o.location=loc;o.empty_display_type='PLAIN_AXES';o.empty_display_size=size;o.parent=parent
    return o
ROOT=empty('REF_ORIGIN',size=.2)
GROUND=empty('GROUND_PLANE',parent=ROOT,size=.3)
GROUND.empty_display_type='CUBE';GROUND.scale=(1,1,0)

def finish(o,name,mat=None,col='08_HARDWARE',note='Estimated geometry; nominal mounting arrangement inferred from K56F catalog.',parent=ROOT):
    o.name=name
    for c in list(o.users_collection):c.objects.unlink(o)
    COL[col].objects.link(o)
    o.parent=parent
    if mat:o.data.materials.append(mat)
    o['geometry_confidence']=note
    o['reference_family']='K56F / FS150FG'
    return o

def material(name,color,metal=0,rough=.4):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    return m
RED=material('PAINT_Candy_prominence_red_approx',(.29,.003,.008),.18,.28)
BLACK=material('ABS_black',(.014,.019,.025),.05,.39)
RUBBER=material('Tire_rubber',(.012,.014,.017),0,.82)
SEATMAT=material('Seat_vinyl',(.018,.020,.023),0,.67)
SILVER=material('Cast_aluminium',(.34,.38,.42),.8,.3)
STEEL=material('Machined_steel',(.51,.55,.60),.9,.23)
DARK=material('Frame_satin_black',(.022,.028,.035),.65,.33)
DISC=material('Brake_rotor_steel',(.38,.40,.43),.88,.38)
LENS=material('Headlamp_optic',(.30,.36,.39),.22,.24)
AMBER=material('Amber_indicator_optic',(.9,.19,.006),.25,.24)
TAIL=material('Red_tail_optic',(.5,.006,.010),.3,.21)
MIRROR=material('Mirror_glass',(.58,.65,.7),.98,.065)
BLACK.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.22
SEATMAT.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.20

def bevel(o,w=.002,segments=3):
    b=o.modifiers.new('Manufactured_edge_radius','BEVEL');b.width=w;b.segments=segments
    b=o.modifiers.new('Weighted_corner_normals','WEIGHTED_NORMAL');b.keep_sharp=True
    return o

def mesh(name,verts,faces,mat,col='08_HARDWARE',smooth=False,bev=0):
    m=bpy.data.meshes.new(name+'_mesh');m.from_pydata(verts,[],faces);m.update()
    o=bpy.data.objects.new(name,m);COL[col].objects.link(o);o.parent=ROOT
    if mat:m.materials.append(mat)
    o['geometry_confidence']='Reference-informed estimate, no manufacturing dimensions available.'
    o['reference_family']='K56F / FS150FG'
    for p in m.polygons:p.use_smooth=smooth
    if bev:bevel(o,bev)
    return o

def box(name,loc,size,mat,col='08_HARDWARE',bev=.003):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=finish(bpy.context.object,name,mat,col);o.scale=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bev:bevel(o,bev)
    return o

def rod(name,a,b,r,mat,col='08_HARDWARE',vertices=40,r2=None):
    a,b=Vector(a),Vector(b)
    bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=r,radius2=r if r2 is None else r2,depth=(b-a).length,location=(a+b)/2)
    o=finish(bpy.context.object,name,mat,col);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
    for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
    return bevel(o,.0007,2)

def tube(name,points,r,mat,col='08_HARDWARE',cyclic=False):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=16
    c.bevel_depth=r;c.bevel_resolution=3
    s=c.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
    for p,co in zip(s.bezier_points,points):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    s.use_cyclic_u=cyclic
    o=bpy.data.objects.new(name,c);COL[col].objects.link(o);o.parent=ROOT;c.materials.append(mat)
    o['geometry_confidence']='Estimated route and section; control points editable.'
    return o

def ring(name,center,profile,mat,col,segments=128):
    # Revolve X/radius cross-section around the wheel axle (X).
    x,y,z=center;v=[];f=[];n=len(profile)
    for i in range(segments):
        a=2*pi*i/segments
        v += [(x+dx,y+r*sin(a),z+r*cos(a)) for dx,r in profile]
    for i in range(segments):
        for j in range(n):f.append((i*n+j,((i+1)%segments)*n+j,((i+1)%segments)*n+(j+1)%n,i*n+(j+1)%n))
    return mesh(name,v,f,mat,col,True)

def panel(name,points,mat=RED,col='06_BODY_K56F',thick=.0025):
    # A panel cage with explicit facets; thickness stays non-destructive.
    o=mesh(name,points,[tuple(range(len(points)))],mat,col)
    t=o.modifiers.new('Surface_triangulation','TRIANGULATE')
    t=o.modifiers.new('Panel_thickness','SOLIDIFY');t.thickness=thick;t.offset=-1
    bevel(o,.0015,3)
    return o

def bracket(name,points,mat=SILVER):
    center=sum((Vector(p) for p in points),Vector())/3
    inner=[center+(Vector(p)-center)*.51 for p in points]
    o=mesh(name,points+inner,[(0,1,4,3),(1,2,5,4),(2,0,3,5)],mat,'08_HARDWARE')
    m=o.modifiers.new('Cast_bracket_thickness','SOLIDIFY');m.thickness=.008
    bevel(o,.002,3);return o

def loft(name,stations,mat,col='06_BODY_K56F',segments=24):
    # Stations: longitudinal Y, half-width, bottom Z, top Z.
    v=[];f=[]
    for y,w,lo,hi in stations:
        for i in range(segments):
            a=2*pi*i/segments
            v.append((w*cos(a),y,(hi+lo)/2+(hi-lo)/2*sin(a)))
    for j in range(len(stations)-1):
        for i in range(segments):f.append((j*segments+i,j*segments+(i+1)%segments,(j+1)*segments+(i+1)%segments,(j+1)*segments+i))
    f+=[tuple(reversed(range(segments))),tuple((len(stations)-1)*segments+i for i in range(segments))]
    return mesh(name,v,f,mat,col,True,bev=.0015)

def swept(name,a,b,half_w,half_h,profile,mat,col,steps=12,end_scale=1.0):
    # Non-circular constant/tapered section swept between two arbitrary points.
    a,b=Vector(a),Vector(b)
    ax=(b-a).normalized()
    side=ax.cross(Vector((0,0,1)))
    if side.length<.1:side=Vector((1,0,0))
    side.normalize()
    vup=side.cross(ax).normalized()
    v=[];f=[];n=len(profile)
    for k in range(steps+1):
        base=a.lerp(b,k/steps);s=(1+(end_scale-1)*k/steps)
        for w,hh in profile:
            v.append(tuple(base+side*(w*half_w*s)+vup*(hh*half_h*s)))
    for k in range(steps):
        for j in range(n):f.append((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j))
    f+=[tuple(reversed(range(n))),tuple(steps*n+i for i in range(n))]
    return mesh(name,v,f,mat,col,False,bev=.0015)

def _proto(name,builder,mat):
    # One authored mesh datablock; every fastener is a linked duplicate.
    if name in PROTO_CACHE:return PROTO_CACHE[name]
    bm=bmesh.new()
    R=Matrix.Rotation(pi/2,4,'Y')  # author along +Z, convert to +X; head at +X.
    builder(lambda matrix,**kw:bmesh.ops.create_cone(bm,cap_ends=True,matrix=R@matrix,**kw))
    me=bpy.data.meshes.new(name+'_mesh');bm.to_mesh(me);bm.free()
    me.materials.append(mat)
    PROTO_CACHE[name]=me
    return me
PROTO_CACHE={}
def _flange_builder(add):
    add(Matrix.Translation((.0006,0,0)),segments=16,radius1=.0086,radius2=.0086,depth=.0012)   # integral flange/washer face
    add(Matrix.Translation((.0037,0,0)),segments=6,radius1=.0046,radius2=.0046,depth=.0050)    # small hex head
    add(Matrix.Translation((-.0060,0,0)),segments=12,radius1=.0040,radius2=.0040,depth=.0120)  # shank
    for i in range(5):
        add(Matrix.Translation((-.0018-i*.0021,0,0)),segments=10,radius1=.0040,radius2=.0047,depth=.0009)  # stylised thread ridge
def _push_builder(add):
    add(Matrix.Translation((.0008,0,0)),segments=16,radius1=.0052,radius2=.0052,depth=.0016)   # panel flange
    add(Matrix.Translation((.0033,0,0)),segments=12,radius1=.0028,radius2=.0023,depth=.0034)   # expanding centre button
def bolt(name,x,y,z,r=.004):
    o=bpy.data.objects.new(name,_proto('PROTO_flange_bolt',_flange_builder,STEEL))
    COL['08_HARDWARE'].objects.link(o);o.parent=ROOT
    m=Matrix.Translation((x,y,z))@Matrix.Scale(r/.0040,4)
    if x<0:m=m@Matrix.Rotation(pi,4,'Z')  # head seats on the outboard face
    o.matrix_world=m
    o['geometry_confidence']='JIS-style flange bolt visual form; no OEM grade or thread pitch is claimed.'
    return o
def push_pin(name,x,y,z):
    o=bpy.data.objects.new(name,_proto('PROTO_push_pin',_push_builder,BLACK))
    COL['08_HARDWARE'].objects.link(o);o.parent=ROOT
    m=Matrix.Translation((x,y,z))
    if x<0:m=m@Matrix.Rotation(pi,4,'Z')
    o.matrix_world=m
    o['geometry_confidence']='Plastic push-pin rivet visual form; clip engagement not modelled.'
    return o

def datum(name,loc,status):
    o=empty(name,loc,ROOT);o['evidence']=status;return o
datum('REF_FRONT_AXLE',FRONT,'Baseline wheelbase + nominal tire radius')
datum('REF_REAR_AXLE',REAR,'Baseline wheelbase + nominal tire radius')
datum('REF_FRONT_CONTACT',(0,WB/2,0),'Nominal unladen tire envelope')
datum('REF_REAR_CONTACT',(0,-WB/2,0),'Nominal unladen tire envelope')
datum('REF_SEAT_780',(0,-.190,.780),'User supplied seat-height datum')
datum('REF_CLEARANCE_150',(0,.060,.150),'User supplied lower-envelope datum')
datum('REF_SWINGARM_PIVOT',PIVOT,'Estimated; not dimensioned by exploded catalog')
datum('REF_STEERING_HEAD_LOWER',HEAD_LOW,'Estimated; silhouette and mechanical coherence')
datum('REF_STEERING_HEAD_UPPER',HEAD_HIGH,'Estimated; silhouette and mechanical coherence')

def wheel(label,center,width,height):
    col='02_FRONT_RUNNING_GEAR' if label=='FR' else '03_REAR_RUNNING_GEAR'
    x,y,z=center;r=.2159+height;hw=width/2
    profile=[(-hw*.72,.211),(-hw,.230),(-hw,.2159+height*.45),(-hw*.84,r-.012),(-hw*.4,r-.002),(0,r),(hw*.4,r-.002),(hw*.84,r-.012),(hw,.2159+height*.45),(hw,.230),(hw*.72,.211)]
    o=ring(label+'_TIRE_'+('90_80_17' if label=='FR' else '120_70_17'),center,profile,RUBBER,col,segments=768)
    # Recess the real tire mesh; leave the centre crown at the exact nominal radius.
    for vert in o.data.vertices:
        dx=abs(vert.co.x);dy=vert.co.y-y;dz=vert.co.z-z;rad=math.hypot(dy,dz)
        if dx>hw*.10 and rad>.232:
            phase=(math.atan2(dy,dz)-.07*(dx/hw-.12)/.72)%(2*pi/48)
            if phase<.014:
                vert.co.y=y+dy*(rad-.0016)/rad;vert.co.z=z+dz*(rad-.0016)/rad
    o['geometry_confidence']='Nominal envelope from user tire designation; carcass and tread estimated.'
    o['nominal_outer_diameter_m']=2*r
    rw=hw*.73
    ring(label+'_Cast_rim_17inch',center,[(-rw,.202),(-rw,.223),(-rw+.004,.226),(-rw+.009,.219),(rw-.009,.219),(rw-.004,.226),(rw,.223),(rw,.202)],DARK,col)
    for side in [-1,1]:
        ring(label+'_Rim_lip_'+str(side),(side*(rw-.003),y,z),[(-.0015,.221),(-.0015,.224),(.0015,.224),(.0015,.221)],STEEL,col)
        ring(label+'_Sidewall_bead_'+str(side),(side*(hw*.97),y,z),[(-.0006,r-.048),(-.0006,r-.046),(.0006,r-.046),(.0006,r-.048)],RUBBER,col)
    rod(label+'_Hub',(-hw,y,z),(hw,y,z),.037,DARK,col)
    # Split-Y cast spoke architecture: thick roots, paired branches, web gussets.
    ring(label+'_Hub_web',center,[(-hw*.55,.036),(-hw*.55,.060),(hw*.55,.060),(hw*.55,.036)],DARK,col,48)
    for i in range(5):
        a=2*pi*i/5
        def pos(rad,angle):return (0,y+rad*sin(angle),z+rad*cos(angle))
        node=pos(.115,a+.11)
        rod(label+'_Spoke_root_'+str(i),pos(.050,a),node,.014,DARK,col,vertices=10,r2=.017)
        for s in [-1,1]:
            rod(label+'_Spoke_branch_'+str(i)+'_'+str(s),node,pos(.206,a+.11+s*.155),.0085,DARK,col,vertices=8,r2=.0065)
            rod(label+'_Spoke_gusset_'+str(i)+'_'+str(s),pos(.155,a+.11+s*.080),pos(.082,a+.018),.005,DARK,col,vertices=8,r2=.0038)
    rod(label+'_Axle',(-.114,y,z),(.114,y,z),.007,STEEL,col)
    for s in [-1,1]:bolt(label+'_Axle_nut_'+str(s),s*.116,y,z,.011)

wheel('FR',FRONT,.090,.072)
wheel('RR',REAR,.120,.084)

# Braking: six-lobed inner perimeter, drilled braking track, separate calipers.
def brake(label,center,x,radius):
    col='02_FRONT_RUNNING_GEAR' if label=='FR' else '03_REAR_RUNNING_GEAR'
    y,z=center.y,center.z
    rotor=ring(label+'_Brake_disc',(x,y,z),[(-.002,radius*.65),(-.002,radius),(.002,radius),(.002,radius*.65)],DISC,col,120)
    # Staggered vent dots instead of a heavy boolean drill; pattern is visual, not the OEM spiral.
    for i in range(24):
        a=i*2*pi/24
        rad=radius*(.91 if i%2==0 else .79)
        bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=.0026,depth=.0016,location=(x+.0022,y+rad*sin(a),z+rad*cos(a)),rotation=(0,pi/2,0))
        finish(bpy.context.object,label+'_Rotor_vent_%02d'%i,BLACK,col)
    for face in rotor.data.polygons:face.use_smooth=False
    bevel(rotor,.00025,2)
    for i in range(5):
        a=i*2*pi/5
        rod(label+'_Rotor_carrier_'+str(i),(x,y+.040*sin(a),z+.040*cos(a)),(x,y+radius*.68*sin(a+.14),z+radius*.68*cos(a+.14)),.010,DISC,col,vertices=8)
        bolt(label+'_Disc_bolt_'+str(i),x,y+.050*sin(a),z+.050*cos(a),.0038)
    ca=box(label+'_Brake_caliper',(x+.013,y-radius*.68,z+radius*.65),(.035,.059,.078),DARK,col,.009)
    for k in [-1,1]:bolt(label+'_Caliper_fastener_'+str(k),x+.035,y-radius*.68,z+radius*.65+k*.022)
    return ca
front_cal=brake('FR',FRONT,.073,.128)
rear_cal=brake('RR',REAR,.085,.110)

# Telescopic fork, rigid at nominal ride position; steering axis tilted back.
for side in [-1,1]:
    x=side*.091
    low=(x,.639,.300);mid=(x,.545,.543);top=(x,.389,.920)
    rod('Fork_slider_'+str(side),low,mid,.022,DARK,'02_FRONT_RUNNING_GEAR')
    rod('Fork_stanchion_'+str(side),mid,top,.016,STEEL,'02_FRONT_RUNNING_GEAR')
    rod('Fork_dust_seal_'+str(side),(x,.551,.529),(x,.539,.558),.025,RUBBER,'02_FRONT_RUNNING_GEAR')
    bolt('Fork_pinch_'+str(side),side*.117,.629,.321,.005)
for y,z in [(.440,.790),(.393,.900)]:
    box('Fork_yoke',(0,y,z),(.225,.055,.024),DARK,'02_FRONT_RUNNING_GEAR',.009)
rod('Steering_head',HEAD_LOW,HEAD_HIGH,.033,DARK,'01_CHASSIS')

# Twin tubular steel frame and triangulated rear subframe, based on F-39.
for side in [-1,1]:
    s=side
    tube('Main_frame_tube_'+str(s),[(s*.029,.435,.776),(s*.065,.310,.655),(s*.076,.060,.545),(s*.080,-.106,.437)],.021,DARK,'01_CHASSIS')
    tube('Subframe_upper_'+str(s),[(s*.079,-.100,.459),(s*.102,-.310,.668),(s*.115,-.710,.756),(s*.083,-.839,.768)],.014,DARK,'01_CHASSIS')
    tube('Subframe_lower_'+str(s),[(s*.078,-.102,.415),(s*.119,-.420,.608),(s*.115,-.735,.746)],.012,DARK,'01_CHASSIS')
    panel('Pivot_plate_'+str(s),[(s*.094,.005,.491),(s*.094,-.160,.482),(s*.094,-.182,.332),(s*.094,-.072,.325)],DARK,'01_CHASSIS',.008)
    bolt('Pivot_through_bolt_'+str(s),s*.103,PIVOT.y,PIVOT.z,.012)
    # Tapered welded swingarm section, slimmer toward the axle dropouts.
    a=Vector((s*.107,PIVOT.y,PIVOT.z));b=Vector((s*.109,REAR.y,REAR.z))
    swept('Swingarm_box_section_'+str(s),a,b,.020,.027,[(-1,-1),(1,-1),(1,1),(-1,1)],DARK,'03_REAR_RUNNING_GEAR',10,end_scale=.78)
    box('Axle_adjuster_'+str(s),(s*.111,REAR.y,REAR.z),(.049,.081,.040),DARK,'03_REAR_RUNNING_GEAR',.002)
    rod('Adjuster_screw_'+str(s),(s*.111,-.658,REAR.z),(s*.111,-.702,REAR.z),.003,STEEL,'03_REAR_RUNNING_GEAR',vertices=12)
for y,z in [(-.700,.752),(-.840,.766)]:
    panel('Subframe_gusset_'+str(y),[(-.052,y-.030,z),(.052,y-.030,z),(.056,y+.030,z+.014),(-.056,y+.030,z+.014)],DARK,'01_CHASSIS',.006)
bracket('Battery_cage_bracket_R',[(.076,-.187,.600),(.078,-.244,.560),(.076,-.200,.512)])
bracket('Battery_cage_bracket_L',[(-.076,-.187,.600),(-.078,-.244,.560),(-.076,-.200,.512)])
rod('Swingarm_crossbrace',(-.11,-.25,.366),(.11,-.25,.366),.023,DARK,'03_REAR_RUNNING_GEAR')
# Direct-mount monoshock anchored to a welded arch on the swingarm, clear of the tire envelope.
rod('Swingarm_shock_arch',(-.095,-.282,.392),(.095,-.282,.392),.017,DARK,'03_REAR_RUNNING_GEAR')
shock_a=Vector((0,-.282,.415));shock_b=Vector((0,-.200,.645))
rod('Monoshock_damper',shock_a,shock_b,.018,SILVER,'03_REAR_RUNNING_GEAR')
axis=(shock_b-shock_a).normalized();u=Vector((1,0,0));v=axis.cross(u)
pts=[]
for i in range(301):
    t=i/300;a=2*pi*8*t
    pts.append(shock_a.lerp(shock_b,.13+.75*t)+.031*(u*cos(a)+v*sin(a)))
tube('Monoshock_coil',pts,.0045,DARK,'03_REAR_RUNNING_GEAR')
for p in [shock_a,shock_b]:rod('Shock_eye',p+Vector((-.020,0,0)),p+Vector((.020,0,0)),.019,DARK,'03_REAR_RUNNING_GEAR')

# Engine external assemblies. No invented internal gears or cooling fins.
col='04_ENGINE_COOLING'
case=loft('Crankcase_core',[(-.215,.075,.253,.411),(-.165,.105,.230,.457),(-.045,.116,.224,.456),(.067,.093,.261,.419),(.112,.060,.306,.403)],SILVER,col,32)
rod('Clutch_cover_R',(.099,-.051,.344),(.132,-.051,.344),.099,DARK,col,vertices=64)
rod('Clutch_cover_outer_R',(.132,-.051,.344),(.141,-.051,.344),.078,DARK,col,vertices=64)
# Stepped clutch-cover profile: raised step, cap-bolted filter dome position and sight glass.
rod('Clutch_cover_step_R',(.141,-.051,.344),(.149,-.051,.344),.060,DARK,col,vertices=48,r2=.062)
for i in range(3):
    a=i*2*pi/3+pi/2
    bolt('Clutch_cover_cap_bolt_R',.152,-.051+.040*sin(a),.344+.040*cos(a),.0035)
rod('Oil_sight_glass_R',(.150,-.108,.300),(.153,-.108,.300),.013,STEEL,col,vertices=24)
rod('Generator_cover_L',(-.137,-.025,.347),(-.101,-.025,.347),.090,DARK,col,vertices=64)
for i in range(3):
    a=i*2*pi/3+pi/3
    rod('Generator_cover_rib_L',(-.137,-.025,.347),(-.143,-.025+.064*sin(a),.347+.064*cos(a)),.006,DARK,col,vertices=12)
for side in [-1,1]:
    for i in range(10):
        a=i*2*pi/10
        bolt('Crankcase_cover_bolt',side*.138,-.043+.089*sin(a),.348+.089*cos(a),.004)
cyl_a=Vector((0,.045,.381));cyl_b=Vector((0,.185,.520))
o=box('Cylinder_water_jacket',(cyl_a+cyl_b)/2,(.121,.119,(cyl_b-cyl_a).length),SILVER,col,.010)
o.rotation_euler=(cyl_b-cyl_a).to_track_quat('Z','Y').to_euler()
o=box('DOHC_cylinder_head',(0,.199,.528),(.174,.147,.106),SILVER,col,.015);o.rotation_euler.x=-.63
o=box('DOHC_cam_cover',(0,.231,.568),(.177,.147,.031),DARK,col,.012);o.rotation_euler.x=-.63
rod('Spark_plug_cap',(0,.205,.600),(0,.178,.648),.0125,RUBBER,col,vertices=16)
tube('Spark_HT_lead',[(0,.180,.650),(0,.110,.696),(0,.010,.708)],.0025,RUBBER,col)
rod('Water_pump_R',(.101,.090,.372),(.143,.090,.372),.035,SILVER,col)
rod('Oil_filler_R',(.139,-.120,.402),(.153,-.120,.425),.013,BLACK,col)
rod('Starter_motor',(-.082,-.042,.480),(.070,-.042,.480),.034,SILVER,col)
rod('Throttle_body',(0,.150,.555),(0,.052,.608),.027,SILVER,col)
tube('Intake_duct',[(0,.052,.608),(0,.028,.606)],.026,RUBBER,col)
box('Air_cleaner_box',(0,-.046,.603),(.158,.145,.131),BLACK,col,.019)
box('Battery',(0,-.187,.564),(.072,.108,.095),BLACK,col,.005)
loft('Underseat_fuel_tank',[(-.625,.065,.624,.690),(-.520,.100,.600,.690),(-.360,.096,.600,.681),(-.283,.066,.627,.682)],DARK,col)
rod('Fuel_filler_cap',(0,-.480,.686),(0,-.480,.696),.033,STEEL,col)
rad=box('Radiator_core',(0,.332,.532),(.199,.041,.173),DARK,col,.003);rad.rotation_euler.x=-.12
for s in [-1,1]:box('Radiator_side_tank_'+str(s),(s*.105,.332,.535),(.025,.051,.186),DARK,col,.006)
for i in range(28):box('Radiator_fin_%02d'%i,(0,.355,.454+i*.0056),(.190,.0018,.0019),SILVER,col,.0004)
tube('Coolant_upper_hose',[(.093,.286,.614),(.136,.255,.583),(.112,.183,.530)],.010,RUBBER,col)
tube('Coolant_lower_hose',[(.111,.314,.460),(.153,.226,.385),(.145,.104,.378)],.010,RUBBER,col)
for ci,(pnt,q) in enumerate([((.093,.286,.614),(.136,.255,.583)),((.112,.183,.530),(.153,.226,.385)),((.111,.314,.460),(.153,.226,.385)),((.145,.104,.378),(.153,.226,.385))]):
    p,qv=Vector(pnt),Vector(q);d=(qv-p).normalized()
    rod('Coolant_hose_clamp_'+str(ci),p-.002*d,p+.002*d,.0125,STEEL,col,vertices=14)
# Radiator reserve tank, catalog block F-35.
box('Radiator_reserve_tank',(.132,.300,.440),(.038,.062,.098),BLACK,col,.006)
rod('Reserve_tank_cap',(.132,.300,.494),(.132,.300,.512),.014,STEEL,col,vertices=16)
rod('Radiator_fan_housing',(0,.293,.530),(0,.309,.530),.068,BLACK,col)
for i in range(4):
    a=.008+i*.027
    rod('Engine_mount_stud',(-.108,a,.470),(.108,a,.470),.004,STEEL,col,vertices=12)
    bolt('Engine_mount_bolt',-.109,a,.470,.0058)
    bolt('Engine_mount_bolt',.109,a,.470,.0058)

# Left chain drive, right stock-style silencer. No donor mesh.
col='05_DRIVETRAIN_EXHAUST'
chain_x=-.094
rear_sprocket=Vector((chain_x,REAR.y,REAR.z));front_sprocket=Vector((chain_x,-.126,.363))
for label,c,r,teeth in [('RR',rear_sprocket,.080,44),('FR',front_sprocket,.027,15)]:
    ring(label+'_Drive_sprocket',c,[(-.002,r*.45),(-.002,r-.004),(.002,r-.004),(.002,r*.45)],STEEL,col,88)
    for i in range(teeth):
        a=i*2*pi/teeth
        tooth=box(label+'_Sprocket_tooth',c+Vector((0,r*sin(a),r*cos(a))),(.006,.006,.009),STEEL,col,.0005);tooth.rotation_euler.x=-a
    for i in range(5):
        a=i*2*pi/5
        rod(label+'_Sprocket_web',c+Vector((0,.018*sin(a),.018*cos(a))),c+Vector((0,r*.56*sin(a),r*.56*cos(a))),.008,STEEL,col,vertices=8)
# External tangents between unequal pitch circles, joined by exposed arcs.
c1,c2=front_sprocket,rear_sprocket;r1,r2=.0305,.084
d=(c2-c1).length;direction=(c2-c1)/d;perp=Vector((0,-direction.z,direction.y))
k=(r1-r2)/d;h=math.sqrt(1-k*k)
n1=direction*k+perp*h;n2=direction*k-perp*h
p1,p2,p3,p4=c1+n1*r1,c2+n1*r2,c2+n2*r2,c1+n2*r1
def arc(c,start,end,r,steps):
    a=math.atan2(start.z-c.z,start.y-c.y);b=math.atan2(end.z-c.z,end.y-c.y)
    while b<a:b+=2*pi
    return [c+Vector((0,r*cos(a+(b-a)*i/steps),r*sin(a+(b-a)*i/steps))) for i in range(steps)]
path=[p1.lerp(p2,i/50) for i in range(50)]+arc(c2,p2,p3,r2,30)+[p3.lerp(p4,i/50) for i in range(50)]+arc(c1,p4,p1,r1,14)
tube('Drive_chain_roller_path',path,.004,DARK,col,True)
for i in range(0,len(path),2):
    p=path[i];rod('Chain_pin_%03d'%i,p+Vector((-.006,0,0)),p+Vector((.006,0,0)),.003,STEEL,col,vertices=8)
box('Upper_chain_guard',(-.105,-.376,.419),(.034,.449,.026),BLACK,col,.008)
# Chain slider/buffer atop the swingarm, catalog block F-38.
panel('Chain_slider_buffer_52170_K56_N10',[(-.097,-.180,.404),(-.097,-.430,.400),(-.097,-.442,.376),(-.097,-.192,.382)],BLACK,'05_DRIVETRAIN_EXHAUST',.005)
tube('Exhaust_header',[(.026,.230,.488),(.027,.284,.429),(.027,.254,.256),(.088,.127,.194),(.150,-.191,.300),(.184,-.372,.418)],.017,DARK,col)
# O2 sensor boss on the downpipe, catalog block F-30.
rod('O2_sensor_36532_K56_N11',(.027,.254,.228),(.027,.254,.272),.011,SILVER,col,vertices=12)
tube('O2_sensor_lead',[(.027,.254,.272),(.020,.230,.330),(.010,.205,.400)],.0018,RUBBER,col)
# Stock canister: flattened asymmetric section rising alongside the swingarm, header joins the inlet.
sil_profile=[(0,1.0),(.62,.62),(1.0,-.05),(.72,-.85),(0,-.95),(-.72,-.85),(-1.0,-.05),(-.62,.62)]
cap_profile=[(0,.9),(.55,.55),(.9,-.05),(.65,-.78),(0,-.88),(-.65,-.78),(-.9,-.05),(-.55,.55)]
sil_a=(.183,-.345,.408);sil_b=(.198,-.815,.520)
swept('Muffler_stock_body_R',sil_a,sil_b,.076,.052,sil_profile,DARK,col,12)
swept('Muffler_end_cap_R',sil_b,(.201,-.840,.528),.076,.052,cap_profile,SILVER,col,4,end_scale=.88)
rod('Muffler_outlet_R',(.201,-.840,.528),(.202,-.854,.534),.022,BLACK,col)
rod('Muffler_hanger',(.191,-.760,.480),(.183,-.742,.680),.008,STEEL,col)
panel('Muffler_heatshield_R',[(.240,-.345,.410),(.262,-.470,.452),(.276,-.790,.552),(.260,-.818,.492),(.245,-.610,.442),(.240,-.440,.376)],BLACK,col,.004)
for y,z in [(-.430,.440),(-.760,.505)]:bolt('Heatshield_bolt',.272,y,z,.005)

# Rider/passenger steps, rear brake, gear selector and folded kick starter.
for s in [-1,1]:
    bracket('Rider_step_bracket_'+str(s),[(s*.144,-.113,.428),(s*.153,-.244,.357),(s*.151,-.131,.300)])
    rod('Rider_footpeg_'+str(s),(s*.145,-.175,.319),(s*.250,-.175,.319),.013,RUBBER)
    bracket('Pillion_step_bracket_'+str(s),[(s*.135,-.401,.606),(s*.144,-.514,.511),(s*.156,-.308,.490)])
    rod('Pillion_bracket_stay_'+str(s),(s*.135,-.401,.606),(s*.117,-.408,.612),.008,DARK,'08_HARDWARE')
    rod('Pillion_bracket_stay2_'+str(s),(s*.156,-.308,.490),(s*.119,-.398,.600),.008,DARK,'08_HARDWARE')
    rod('Pillion_peg_'+str(s),(s*.146,-.401,.496),(s*.222,-.401,.496),.012,DARK)
    for y,z in [(-.401,.593),(-.316,.503)]:bolt('Pillion_bracket_bolt',s*.148,y,z,.006)
tube('Gear_change_lever_L',[(-.161,-.151,.319),(-.173,-.080,.283),(-.188,.045,.292)],.006,STEEL)
rod('Gear_toe_rubber_L',(-.181,.045,.292),(-.225,.045,.292),.012,RUBBER)
tube('Rear_brake_pedal_R',[(.161,-.164,.312),(.189,-.027,.290),(.209,.064,.310)],.006,STEEL)
box('Rear_brake_toe_pad_R',(.208,.068,.313),(.041,.038,.009),DARK)
# Rear brake master cylinder, pushrod, remote reservoir and hose, catalog block F-11.
box('Rear_brake_master_cylinder_43510_K56_N11',(.166,-.298,.352),(.036,.078,.038),DARK,'08_HARDWARE',.006)
tube('Master_pushrod_R',[(.170,-.258,.340),(.182,-.120,.300)],.0035,STEEL)
box('Brake_fluid_reservoir_R',(.150,-.392,.446),(.030,.058,.052),DARK,'08_HARDWARE',.005)
rod('Reservoir_stay_R',(.150,-.392,.470),(.117,-.415,.600),.006,DARK)
rod('Reservoir_cap_R',(.150,-.392,.474),(.150,-.392,.486),.012,BLACK)
tube('Reservoir_hose_R',[(.152,-.362,.430),(.160,-.330,.385),(.166,-.312,.370)],.0022,RUBBER)
tube('Rear_brake_hose',[(.150,-.330,.360),(.140,-.500,.332),(.112,-.650,.345),(.100,-.714,.364)],.0028,RUBBER)
tube('Kick_starter_folded_R',[(.148,-.132,.383),(.167,-.107,.439),(.166,-.022,.486)],.008,STEEL)
rod('Kick_starter_rubber_R',(.161,-.022,.486),(.207,-.022,.486),.012,RUBBER)
tube('Side_stand_stowed_L',[(-.136,-.119,.264),(-.167,-.271,.228),(-.171,-.379,.230)],.009,DARK)
box('Side_stand_foot_stowed',(-.171,-.382,.230),(.036,.044,.008),DARK)

# K56F body: polygon cages follow F-44/F-44-10/F-23-10 and 2016 press photos.
# Long stepped seat and U-shaped grab rail; fairing uses connected faceted patches.
seat_stations=[(-.858,.044,.772,.802),(-.812,.099,.750,.830),(-.690,.127,.727,.829),(-.480,.128,.702,.806),(-.344,.124,.698,.779),(-.190,.115,.701,.780),(-.071,.107,.714,.788),(-.031,.082,.731,.785)]
seat=loft('SEAT_77200_K56_N10',seat_stations,SEATMAT)
seat['catalog_block']='F-23';seat['oem_reference_part']='77200-K56-N10'
loft('Seat_pan',[(y,w*.93,lo-.008,lo+.009) for y,w,lo,hi in seat_stations],BLACK)
loft('Underseat_inner_support',[(-.390,.098,.654,.703),(-.215,.093,.626,.703),(-.094,.086,.637,.717),(-.054,.069,.685,.733)],BLACK)
box('Seat_front_hinge',(0,-.078,.694),(.099,.043,.023),DARK,'01_CHASSIS',.005)
tube('Grab_rail_50400_K56_N10',[(-.143,-.603,.772),(-.138,-.776,.826),(-.087,-.895,.846),(0,-.920,.845),(.087,-.895,.846),(.138,-.776,.826),(.143,-.603,.772)],.014,DARK,'06_BODY_K56F')
loft('TAIL_COVER_83510_K56_N10',[(-.948,.020,.742,.782),(-.907,.076,.740,.808),(-.820,.110,.708,.800),(-.650,.128,.672,.756),(-.380,.122,.619,.714),(-.254,.077,.649,.697)],RED)
for s in [-1,1]:
    def pts(seq):return [(s*x,y,z) for x,y,z in seq]
    # Dark inset below the red tail, silver rear cover blade documented in F-23-10.
    panel('Rear_body_inset_'+str(s),pts([(.074,-.882,.724),(.112,-.675,.674),(.115,-.419,.629),(.078,-.174,.601),(.070,-.134,.672),(.103,-.430,.701)]),BLACK)
    blade=panel('Rear_body_blade_'+str(s),pts([(.077,-.913,.757),(.116,-.696,.713),(.126,-.433,.654),(.097,-.307,.641),(.115,-.599,.725),(.090,-.878,.786)]),SILVER)
    blade['catalog_block']='F-23-10';blade['oem_reference_part']='64480-K56-N10 / 64490-K56-N10'
    panel('Main_pipe_side_cover_'+str(s),pts([(.111,-.090,.672),(.113,.064,.629),(.113,.256,.681),(.101,.337,.680),(.097,.230,.576),(.103,-.051,.520),(.101,-.172,.570)]),BLACK)
    panel('Pivot_cover_'+str(s),pts([(.102,-.112,.524),(.106,-.189,.565),(.105,-.251,.443),(.100,-.153,.394),(.102,-.093,.405)]),BLACK)
    # Side cover: upper blade, long descending fairing leg and lower return.
    # Flared layered-wing width; outer shell separated from a black inner duct panel.
    upper=[(.132,.015,.650),(.200,.226,.709),(.212,.520,.716),(.166,.590,.686),(.196,.392,.604),(.192,.245,.570),(.132,.182,.623)]
    panel('SIDE_COVER_upper_'+str(s),pts(upper),RED)
    panel('SIDE_COVER_outer_leg_'+str(s),pts([(.196,.392,.604),(.192,.245,.570),(.166,.201,.456),(.115,.355,.168),(.172,.445,.158),(.196,.423,.366)]),RED)
    panel('SIDE_COVER_inner_recess_'+str(s),pts([(.196,.423,.366),(.172,.445,.158),(.112,.476,.165),(.126,.451,.366),(.132,.476,.562),(.196,.392,.604)]),BLACK)
    panel('SIDE_COVER_duct_inner_'+str(s),pts([(.150,.195,.500),(.158,.545,.700),(.134,.560,.650),(.126,.470,.540),(.126,.215,.460),(.146,.185,.470)]),BLACK)
    for dy,dz in [(.255,.548),(.510,.662)]:
        rod('Duct_standoff',(s*.152,dy,dz),(s*.168,dy,dz+.008),.0035,BLACK)
    panel('LOWER_COVER_return_'+str(s),pts([(.172,.445,.158),(.115,.355,.168),(.094,.041,.194),(.100,.090,.231),(.128,.272,.263)]),RED)
    panel('Side_blade_crease_'+str(s),pts([(.132,.015,.650),(.200,.226,.709),(.212,.520,.716),(.205,.391,.684),(.161,.199,.645)]),DARK)
    # Original integrated front winker surround. Front cowl slopes to a sharp forward beak.
    panel('FRONT_COVER_winker_surround_'+str(s),pts([(.188,.379,.831),(.231,.402,.786),(.201,.555,.706),(.063,.736,.620),(.033,.688,.672),(.154,.471,.789)]),BLACK)
    panel('FRONT_TOP_wing_'+str(s),pts([(.079,.378,.847),(.188,.379,.831),(.231,.402,.786),(.181,.452,.788),(.075,.660,.688),(.022,.690,.680)]),RED)
    panel('FRONT_TOP_center_'+str(s),pts([(0,.397,.856),(.079,.378,.847),(.022,.690,.680),(0,.732,.662)]),RED)
    panel('Front_beak_lower_'+str(s),pts([(0,.752,.606),(.063,.736,.620),(.201,.555,.706),(.166,.590,.686),(.056,.740,.600),(0,.762,.596)]),BLACK)
    # Multi-tier recessed lighting module: dark housing behind, lens set deeper, position bar on top.
    panel('FR_Winker_housing_'+str(s),pts([(.188,.441,.790),(.205,.454,.767),(.164,.563,.711),(.055,.687,.655),(.119,.567,.714)]),BLACK,'06_BODY_K56F',.004)
    panel('FR_Winker_lens_'+str(s),pts([(.188,.431,.790),(.205,.444,.767),(.164,.553,.711),(.055,.677,.655),(.119,.557,.714)]),LENS,'07_CONTROLS_LIGHTS',.003)
    panel('FR_position_light_bar_'+str(s),pts([(.186,.438,.788),(.198,.449,.769),(.148,.542,.722),(.140,.548,.727)]),LENS,'07_CONTROLS_LIGHTS',.002)
    for i in range(3):
        panel('FR_Winker_optic_'+str(s)+'_'+str(i),pts([(.159-i*.031,.505+i*.043,.754-i*.026),(.171-i*.031,.513+i*.043,.737-i*.026),(.153-i*.031,.538+i*.043,.724-i*.026),(.143-i*.031,.527+i*.043,.739-i*.026)]),AMBER,'07_CONTROLS_LIGHTS',.001)
    for y,z,x in [(.369,.185,.145),(.236,.629,.180),(-.398,.654,.143)]:
        push_pin('Body_panel_fastener',s*x,y,z)
        rod('Body_panel_recess',(s*x-.0005,y,z),(s*x+.0005,y,z),.0062,BLACK,'08_HARDWARE',vertices=16)
    for px,py,pz in [(.199,.300,.712),(.204,.450,.710),(.140,-.560,.688),(.052,-.900,.770)]:
        push_pin('Panel_push_pin',s*px,py,pz)
    # Three open-looking dark inset vents; no fabricated Honda graphics.
    for i in range(3):
        y=.148+i*.049
        panel('Lower_cover_vent_'+str(s)+'_'+str(i),pts([(.116+i*.004,y,.218),(.128+i*.004,y+.052,.212),(.123+i*.004,y+.056,.201)]),BLACK)
panel('LOWER_COVER_center',[(0,.320,.150),(.115,.355,.168),(.094,.041,.194),(-.094,.041,.194),(-.115,.355,.168)],BLACK)
loft('Main_pipe_top_cover',[(-.026,.070,.690,.736),(-.141,.088,.654,.705),(-.050,.087,.632,.683),(.047,.090,.621,.671),(.197,.086,.674,.706),(.310,.065,.710,.749),(.360,.059,.748,.785)],BLACK)

# Front fender: swept crown, separate descending fork skirts, adequate tire gap.
v=[];f=[]
for i in range(25):
    a=-.73+1.76*i/24
    for j in range(13):
        u=-1+2*j/12
        r=RF+.022+.010*(1-u*u)-.016*max(0.0,u)**3  # arrowhead drop toward the front tip
        v.append((.069*u,FRONT.y+r*sin(a),FRONT.z+r*cos(a)))
for i in range(24):
    for j in range(12):f.append((i*13+j,i*13+j+1,(i+1)*13+j+1,(i+1)*13+j))
fen=mesh('FENDER_A_FR_61100_K56_N10',v,f,RED,'06_BODY_K56F',True)
mod=fen.modifiers.new('Fender_shell_2mm','SOLIDIFY');mod.thickness=.002
for s in [-1,1]:
    panel('Fender_fork_skirt_'+str(s),[(s*.065,.573,.581),(s*.073,.622,.561),(s*.072,.650,.329),(s*.068,.614,.330),(s*.070,.540,.531)],RED)
    bolt('Fender_mount',s*.076,.615,.362,.004)

# Tail lamp with integrated V1 rear winkers; not facelift stalk indicators.
panel('TAIL_LAMP_upper', [(-.086,-.920,.767),(0,-.956,.783),(.086,-.920,.767),(.063,-.947,.722),(0,-.972,.715),(-.063,-.947,.722)],TAIL,'07_CONTROLS_LIGHTS',.008)
for s in [-1,1]:
    panel('RR_Winker_lens_'+str(s),[(s*.063,-.947,.722),(s*.102,-.915,.749),(s*.111,-.894,.716),(s*.083,-.933,.700)],LENS,'07_CONTROLS_LIGHTS',.004)
    panel('RR_Winker_bulb_'+str(s),[(s*.084,-.938,.721),(s*.103,-.916,.730),(s*.099,-.922,.709)],AMBER,'07_CONTROLS_LIGHTS',.002)
# License plate lamp housing, catalog block F-29.
box('License_lamp_33720_K56_N10',(0,-.948,.738),(.070,.026,.022),BLACK,'07_CONTROLS_LIGHTS',.003)
panel('License_lamp_lens',[(0,-.962,.748),(.030,-.957,.744),(.030,-.957,.732),(0,-.962,.728),(-.030,-.957,.732),(-.030,-.957,.744)],LENS,'07_CONTROLS_LIGHTS',.002)
panel('Rear_fender_lower',[(-.075,-.870,.712),(.075,-.870,.712),(.065,-1.0951,.359),(-.065,-1.0951,.359)],BLACK,'06_BODY_K56F',.004)
box('Rear_plate_bracket',(0,-1.015,.491),(.202,.010,.095),BLACK,'08_HARDWARE',.003)
box('Rear_reflector',(0,-1.069,.410),(.047,.012,.021),TAIL,'07_CONTROLS_LIGHTS',.003)

# Handle cowl, tall dual-layer headlamp, analogue tachometer + LCD.
loft('Handle_rear_cover',[(.268,.112,.871,.958),(.334,.181,.855,.982),(.404,.152,.850,1.007),(.481,.092,.866,1.000),(.536,.051,.865,.930)],BLACK,'07_CONTROLS_LIGHTS')
rod('Steering_neck_cover',(0,.408,.785),(0,.367,.875),.059,BLACK,'06_BODY_K56F',vertices=32,r2=.073)
for s in [-1,1]:
    panel('Handle_top_cover_'+str(s),[(s*.041,.382,1.012),(s*.127,.307,.984),(s*.207,.326,.948),(s*.164,.445,.919),(s*.099,.464,.959)],RED,'07_CONTROLS_LIGHTS')
    tube('Handle_pipe_'+str(s),[(0,.351,.908),(s*.117,.321,.923),(s*.240,.293,.924),(s*.352,.273,.923)],.011,DARK,'07_CONTROLS_LIGHTS')
    rod('Grip_'+str(s),(s*.241,.292,.924),(s*.352,.273,.923),.015,RUBBER,'07_CONTROLS_LIGHTS')
    rod('Bar_end_'+str(s),(s*.352,.273,.923),(s*.359,.272,.923),.015,DARK,'07_CONTROLS_LIGHTS')
    # Handlebar balancer weight inside the bar end, catalog block F-7.
    rod('Handlebar_balancer_'+str(s),(s*.342,.2737,.923),(s*.357,.2727,.923),.0095,STEEL,'07_CONTROLS_LIGHTS')
    for i in range(12):
        x=s*(.247+i*.008)
        rod('Grip_rib', (x-.001,.291-i*.0014,.924),(x+.001,.291-i*.0014,.924),.0155,RUBBER,'07_CONTROLS_LIGHTS',vertices=24)
    box('Switch_housing_'+str(s),(s*.222,.296,.923),(.039,.049,.043),BLACK,'07_CONTROLS_LIGHTS',.009)
    box('Switch_button_'+str(s),(s*.222,.270,.932),(.015,.008,.011),DARK,'07_CONTROLS_LIGHTS',.002)
    tube(('Brake_lever_R' if s>0 else 'Clutch_lever_L'),[(s*.218,.312,.909),(s*.255,.340,.904),(s*.315,.328,.901),(s*.354,.316,.902)],.0045,DARK,'07_CONTROLS_LIGHTS')
    tube('Mirror_stalk_'+str(s),[(s*.219,.323,.950),(s*.248,.353,1.010),(s*.290,.361,1.068)],.0045,DARK,'07_CONTROLS_LIGHTS')
    # Rounded polygon rather than a box silhouette, using an elliptical loft along Y.
    mirror=loft('Mirror_shell_'+str(s),[(.345,.044,1.046,1.091),(.356,.061,1.036,1.100),(.374,.056,1.041,1.096),(.380,.041,1.052,1.088)],BLACK,'07_CONTROLS_LIGHTS',24)
    for vert in mirror.data.vertices:vert.co.x+=s*.299
    glass_points=[(s*.299+.045*cos(i*2*pi/32),.342,1.068+.023*sin(i*2*pi/32)) for i in range(32)]
    panel('Mirror_reflector_'+str(s),glass_points,MIRROR,'07_CONTROLS_LIGHTS',.001)
# Headlamp module sits recessed behind the beak leading edge (raked cowl relationship).
panel('Headlight_black_bezel',[(-.061,.485,.997),(.061,.485,.997),(.064,.519,.936),(.042,.536,.861),(-.042,.536,.861),(-.064,.519,.936)],BLACK,'07_CONTROLS_LIGHTS',.004)
panel('HEADLIGHT_33100_K56_N11',[(-.053,.489,.989),(.053,.489,.989),(.057,.522,.935),(.034,.540,.872),(-.034,.540,.872),(-.057,.522,.935)],LENS,'07_CONTROLS_LIGHTS',.003)
panel('Headlight_centre_divider',[(-.057,.523,.936),(.057,.523,.936),(.053,.527,.927),(-.053,.527,.927)],SILVER,'07_CONTROLS_LIGHTS',.002)
for s in [-1,1]:
    for z,y,w in [(.964,.507,.043),(.901,.535,.029)]:
        panel('Headlamp_reflector_facet',[(s*.005,y,z+.015),(s*w,y-.002,z+.016),(s*w*.92,y+.006,z-.009),(s*.005,y+.007,z-.013)],STEEL,'07_CONTROLS_LIGHTS',.002)
box('Front_brake_master',(.194,.317,.949),(.054,.057,.029),DARK,'07_CONTROLS_LIGHTS',.005)
tube('Front_brake_hose',[(.183,.322,.931),(.112,.370,.815),(.094,.443,.641),(.112,.493,.471),(.094,.555,.381)],.003,RUBBER,'07_CONTROLS_LIGHTS')
tube('Clutch_cable',[(-.216,.302,.914),(-.095,.310,.818),(-.120,.225,.646),(-.137,-.046,.448)],.003,RUBBER,'07_CONTROLS_LIGHTS')
tube('Throttle_cable',[(.226,.290,.921),(.153,.311,.839),(.089,.296,.695),(.063,.067,.584)],.0027,RUBBER,'07_CONTROLS_LIGHTS')
cluster=box('Meter_37100_K56_N11',(0,.286,.960),(.170,.093,.034),BLACK,'07_CONTROLS_LIGHTS',.018)
cluster.rotation_euler.x=.50
rod('Analogue_tachometer_face',(-.033,.280,.971),(-.033,.273,.985),.036,BLACK,'07_CONTROLS_LIGHTS',vertices=64)
for i in range(11):
    a=-2.1+i*.41
    rod('Tachometer_tick',(-.033+.027*sin(a),.271+.0241*cos(a),.986+.0121*cos(a)),(-.033+.031*sin(a),.271+.0277*cos(a),.986+.0139*cos(a)),.0008,SILVER,'07_CONTROLS_LIGHTS',vertices=8)
tube('Tachometer_needle',[(-.033,.271,.986),(-.057,.263,.982)],.0009,RED,'07_CONTROLS_LIGHTS')
LCDMAT=material('LCD_unlit',(.23,.32,.29),.12,.31)
lcd=box('LCD_speed_display',(.046,.271,.982),(.063,.039,.002),LCDMAT,'07_CONTROLS_LIGHTS',.003);lcd.rotation_euler.x=.50
rod('Ignition_barrel',(0,.337,.825),(0,.319,.835),.014,STEEL,'07_CONTROLS_LIGHTS')

# Procedural material grain avoids missing external textures.
for m,scale,strength,distance in [(SEATMAT,380,.23,.00045),(RUBBER,220,.15,.0003),(SILVER,180,.12,.00022)]:
    n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=2
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=strength;bump.inputs['Distance'].default_value=distance
    l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],p.inputs['Normal'])

# Reference cards are packed into .blend, hidden for normal display/render.
for i,n in enumerate(['2016-Honda-Supra-GTR-150-1-e1464665050191.jpg','page_089.png','page_058.png','page_072.png','page_094.png']):
    path=OUT/'references'/n
    if path.exists():
        img=bpy.data.images.load(str(path),check_existing=True);img.pack()
        o=bpy.data.objects.new('REFERENCE_'+path.stem,None);COL['09_REFERENCE_IMAGES'].objects.link(o)
        o.empty_display_type='IMAGE';o.data=img;o.empty_display_size=1.5;o.location=(2+i*.01,0,1);o.rotation_euler=(pi/2,0,pi/2)
        o.hide_render=True;o['source_file']=n;o['calibration']='Uncalibrated perspective/diagram. Not an orthographic blueprint.'
COL['09_REFERENCE_IMAGES'].hide_viewport=True;COL['09_REFERENCE_IMAGES'].hide_render=True

# Studio is independent of REF_ORIGIN and excluded from vehicle measurements.
STUDIOMAT=material('Studio_floor',(.055,.070,.084),.05,.60)
box('Studio_floor',(0,0,-.026),(200,200,.05),STUDIOMAT,'90_STUDIO',0).parent=None
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def camera(name,loc,target,ortho=2.5):
    bpy.ops.object.camera_add(location=loc);o=finish(bpy.context.object,name,col='90_STUDIO',parent=None)
    o.data.type='ORTHO';o.data.ortho_scale=ortho;aim(o,target);return o
hero=camera('CAM_HERO_RIGHT_FRONT',(3.3,3.7,2.1),(0,-.03,.52),2.55)
right=camera('CAM_RIGHT',(4,0,.56),(0,0,.56),2.40)
left=camera('CAM_LEFT',(-4,0,.56),(0,0,.56),2.40)
front=camera('CAM_FRONT',(0,4,.56),(0,0,.56),1.70)
rear=camera('CAM_REAR',(0,-4,.56),(0,0,.56),1.70)
top=camera('CAM_TOP',(0,0,4),(0,0,0),3.10)
for name,loc,energy,size,target in [('Key',(2,1,4),650,4,(0,0,.5)),('Fill',(-2,1,2),450,3,(0,0,.5)),('Rim',(1,-3,3),850,3,(0,0,.5))]:
    bpy.ops.object.light_add(type='AREA',location=loc);o=finish(bpy.context.object,name,col='90_STUDIO',parent=None);o.data.energy=energy;o.data.shape='DISK';o.data.size=size;aim(o,target)
scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(.13,.17,.22,1)
scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.4
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=1500;scene.render.resolution_y=1125;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.camera=hero
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.render.filepath=str(OUT/'preview_hero.png')

# ============================================================================
# V7 ENHANCEMENT (V2+V3+V4+V5+V6+V7 combined) — Honda Supra GTR 150 1:1 detail
# Adds: PBR materials, Honda Wing emblems (5 locations), text decals (GTR/SUPRA/
# 150/HONDA/PGM-FI/DOHC/NISSIN/DOT4/LIQUID COOLED/SPORT), white racing stripes,
# LED headlight with DRL + projector lens, gold anodized USD fork, titanium brake
# calipers with gold piston caps, chrome exhaust tip, license plate with text,
# reflectors (amber/red), tire tread blocks (street sport pattern), cooling fins
# (gold anodized), side stand switch, bank angle sensor, coolant sight, bar-end
# weights with Honda wing, frame rail protectors, engine skid plate, chain guard
# extension, sprocket dampers, carbon-look inner duct, seat ribs, brake hose
# routing, tail lamp LED segments, fork gaiters, wheel hub chrome, battery label,
# regulator/rectifier, main wiring harness, starter relay, rear axle nuts, mud
# flap, exhaust port flange, engine mount plates, cables (throttle/clutch/brake).
# ============================================================================

# --- V7 Material library ---
CHROME  = material('Chrome_plated_steel',  (.78,.80,.82), .98, .06)
GOLD    = material('Anodized_gold_fork',   (.62,.48,.20), .85, .28)
TITANI  = material('Titanium_caliper',     (.42,.38,.36), .72, .34)
WDECAL  = material('White_paint_decal',    (.95,.95,.95), .06, .34)
PLATEBG = material('License_plate_white',  (.92,.92,.92), .03, .50)
PLATETX = material('License_plate_text',   (.05,.05,.05), .03, .55)
AMBREF  = material('Amber_reflector',      (.95,.45,.05), .15, .20)
REDREF  = material('Red_reflector',        (.85,.05,.05), .15, .20)
LEDHUE  = material('LED_DRL_bright',       (.92,.96,1.0), .10, .12)
CARBON  = material('Carbon_weave',         (.05,.06,.07), .35, .42)
DARKSTK = material('Dark_sticker',         (.08,.08,.08), .15, .45)
CHROME.node_tree.nodes.get('Principled BSDF').inputs['Coat Weight'].default_value = 1.0
GOLD.node_tree.nodes.get('Principled BSDF').inputs['Coat Weight'].default_value = .65

# --- V7 Helper functions ---
def text_decal(name, text, loc, rot, size=.020, mat=None, ext=.0006, col='06_BODY_K56F'):
    """3D extruded text for emblems/decals. Cleans up zero-area faces."""
    if mat is None: mat = WDECAL
    bpy.ops.object.text_add(location=loc, rotation=rot)
    o=bpy.context.object
    o.data.body=text; o.data.size=size; o.data.extrude=ext
    o.data.align_x='CENTER'; o.data.align_y='CENTER'
    o.data.bevel_depth=.0003; o.data.bevel_resolution=2
    bpy.ops.object.convert(target='MESH')
    # Cleanup degenerate geometry
    bm=bmesh.new(); bm.from_mesh(o.data)
    bad_faces=[f for f in bm.faces if f.calc_area()<1e-10]
    if bad_faces: bmesh.ops.delete(bm, geom=bad_faces, context='FACES')
    loose_verts=[v for v in bm.verts if not v.link_faces]
    if loose_verts: bmesh.ops.delete(bm, geom=loose_verts, context='VERTS')
    bm.to_mesh(o.data); bm.free(); o.data.update()
    finish(o,name,mat,col)
    o['geometry_confidence']='Text decal "%s"; visual logo, not OEM typography.'%text
    o['reference_family']='K56F / FS150FG'
    return o

def cooling_fin(name,center,axis,length,width,thickness=.0018,count=14,pitch=.006,mat=None,col='04_ENGINE_COOLING'):
    """Stack of thin cooling fins as proper 3D thin box slabs."""
    if mat is None: mat = GOLD
    axis=Vector(axis).normalized()
    perp=axis.cross(Vector((0,0,1)))
    if perp.length<.1: perp=Vector((1,0,0))
    perp.normalize()
    up=perp.cross(axis).normalized()
    fins=[]
    for i in range(count):
        t=(i-(count-1)/2)*pitch
        c=Vector(center)+axis*t
        hw=width*(1-.05*i/count)/2
        ht=thickness/2; hl=length/2
        local_verts=[(-hw,-ht,-hl),(hw,-ht,-hl),(hw,ht,-hl),(-hw,ht,-hl),
                     (-hw,-ht,hl),(hw,-ht,hl),(hw,ht,hl),(-hw,ht,hl)]
        world_verts=[(c+perp*cl[0]+axis*cl[1]+up*cl[2]).to_tuple() for cl in local_verts]
        faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(2,3,7,6),(0,4,7,3),(1,2,6,5)]
        m=bpy.data.meshes.new(name+'_%02d_mesh'%i); m.from_pydata(world_verts,[],faces); m.update()
        o=bpy.data.objects.new(name+'_%02d'%i,m); COL[col].objects.link(o); o.parent=ROOT
        if mat: m.materials.append(mat)
        o['geometry_confidence']='Gold anodized cooling fin V7; visual, not Honda casting drawing.'
        o['reference_family']='K56F / FS150FG'
        fins.append(o)
    return fins

def tread_block(name,center,w,l,h,mat,col):
    """Single tread block on tire surface."""
    x,y,z=center
    bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y,z))
    o=finish(bpy.context.object,name,mat,col)
    o.scale=(w,l,h)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return o

def honda_wing_emblem_v7(name, center, side, scale=1.0, mat=None):
    """Honda Wing emblem (7 chrome feathers + center body).
    Flat on fairing surface. Wing extends in Y, feathers stacked in Z,
    thickness in X (outward from fairing)."""
    if mat is None: mat = CHROME
    cx, cy, cz = center
    s = side
    wing_span = 0.045 * scale
    wing_height = 0.025 * scale
    wing_thick = 0.0020 * scale
    feathers = []
    for i in range(7):
        feather_len = wing_span * (1.0 - abs(i - 3) * 0.12)
        z_off = (i - 3) * wing_height / 7
        y_root = cy - 0.002 * scale
        y_tip = cy + feather_len * (1 if i % 2 == 0 else 0.85)
        x_out = cx + s * wing_thick
        fw = wing_height / 8
        verts = [
            (x_out, y_root, cz + z_off + fw),
            (x_out, y_tip,  cz + z_off + fw * 0.7),
            (x_out, y_tip,  cz + z_off - fw * 0.7),
            (x_out, y_root, cz + z_off - fw),
        ]
        o = mesh(name+'_feather_%02d'%i, verts, [(0,1,2,3)], mat, '06_BODY_K56F')
        m = o.modifiers.new('Emblem_thickness','SOLIDIFY'); m.thickness = wing_thick * 0.6; m.offset = 1.0
        bevel(o, .0002 * scale, 2)
        o['geometry_confidence'] = 'Honda Wing emblem V7; stylised chrome logo, not OEM artwork.'
        o['reference_family'] = 'K56F / FS150FG'
        feathers.append(o)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.004 * scale, location=(cx + s*wing_thick*0.5, cy, cz))
    body = finish(bpy.context.object, name+'_center_body', mat, '06_BODY_K56F')
    body.scale = (0.4, 1.2, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    body['reference_family'] = 'K56F / FS150FG'
    return feathers

def honda_wing_nose_v7(name, center, scale=1.0, mat=None):
    """Honda Wing emblem yang menghadap ke depan (untuk nose fairing).
    Wing extends in X direction (left-right), thickness in Y (forward)."""
    if mat is None: mat = CHROME
    cx, cy, cz = center
    wing_span = 0.070 * scale
    wing_height = 0.030 * scale
    wing_thick = 0.0035 * scale
    normal = Vector((0, 0.7, 0.7)).normalized()
    feathers = []
    for i in range(7):
        feather_len = wing_span * (1.0 - abs(i - 3) * 0.10)
        z_off = (i - 3) * wing_height / 7
        if i < 3:
            x_tip = cx - feather_len; x_root = cx - 0.005 * scale
        elif i > 3:
            x_tip = cx + feather_len; x_root = cx + 0.005 * scale
        else:
            x_tip = cx + feather_len * 0.6; x_root = cx
        base_pos = Vector((x_root if i != 3 else cx, cy, cz + z_off))
        out_pos = base_pos + normal * wing_thick
        tip_pos = Vector((x_tip, cy + 0.005 * scale, cz + z_off))
        fw = wing_height / 7
        verts = [
            (out_pos.x, out_pos.y, out_pos.z + fw),
            (tip_pos.x, tip_pos.y + wing_thick, tip_pos.z + fw * 0.7),
            (tip_pos.x, tip_pos.y + wing_thick, tip_pos.z - fw * 0.7),
            (out_pos.x, out_pos.y, out_pos.z - fw),
        ]
        o = mesh(name+'_feather_%02d'%i, verts, [(0,1,2,3)], mat, '06_BODY_K56F')
        m = o.modifiers.new('Emblem_thickness','SOLIDIFY'); m.thickness = wing_thick * 0.4; m.offset = 1.0
        bevel(o, .0003 * scale, 2)
        o['geometry_confidence'] = 'Honda Wing nose emblem V7; stylised chrome logo on front fairing.'
        o['reference_family'] = 'K56F / FS150FG'
        feathers.append(o)
    center_pos = Vector((cx, cy, cz)) + normal * wing_thick * 1.2
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.006 * scale, location=center_pos)
    body = finish(bpy.context.object, name+'_center_body', mat, '06_BODY_K56F')
    body.scale = (1.3, 0.4, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    body['reference_family'] = 'K56F / FS150FG'
    return feathers

# ============================================================================
# 1. HONDA WING EMBLEMS — 5 locations
# ============================================================================
honda_wing_emblem_v7('Honda_Wing_side_R',  (0.198, 0.330, 0.680), +1, scale=1.6)
honda_wing_emblem_v7('Honda_Wing_side_L',  (-0.198, 0.330, 0.680), -1, scale=1.6)
honda_wing_nose_v7('Honda_Wing_nose',      (0, 0.650, 0.780), scale=1.5)
for side in [-1, 1]:
    honda_wing_emblem_v7('Honda_Wing_mirror_%s'%('R' if side>0 else 'L'),
                        (side*0.345, 0.343, 1.075), side, scale=0.35)
honda_wing_emblem_v7('Honda_Wing_fender_R',  (0.069, 0.620, 0.620), +1, scale=0.6)
honda_wing_emblem_v7('Honda_Wing_fender_L',  (-0.069, 0.620, 0.620), -1, scale=0.6)
for side in [-1, 1]:
    honda_wing_emblem_v7('Honda_Wing_barend_%s'%('R' if side>0 else 'L'),
                        (side*0.362, 0.272, 0.923), side, scale=0.25)

# ============================================================================
# 2. TEXT DECALS — GTR, SUPRA, 150, HONDA, PGM-FI, DOHC, NISSIN, DOT4, dll.
# ============================================================================
for side in [-1, 1]:
    s = side
    # "GTR" decal besar di tail cowl
    text_decal('GTR_decal_%s'%('R' if s>0 else 'L'), 'GTR',
               (s*0.118, -0.780, 0.775),
               (pi/2, 0, pi/2 if s<0 else -pi/2),
               size=0.060, mat=WDECAL, ext=0.0012)
    # "SUPRA" decal besar di side fairing
    text_decal('Supra_decal_%s'%('R' if s>0 else 'L'), 'SUPRA',
               (s*0.205, 0.350, 0.660),
               (pi/2, 0, pi/2 if s<0 else -pi/2),
               size=0.050, mat=WDECAL, ext=0.0015)
    # "150" decal di bawah SUPRA
    text_decal('Supra_150_%s'%('R' if s>0 else 'L'), '150',
               (s*0.210, 0.280, 0.620),
               (pi/2, 0, pi/2 if s<0 else -pi/2),
               size=0.040, mat=WDECAL, ext=0.0015)
    # "PGM-FI" badge di engine
    text_decal('PGMFI_%s'%('R' if s>0 else 'L'), 'PGM-FI',
               (s*0.078, 0.030, 0.690),
               (pi/2, 0, pi/2 if s<0 else -pi/2),
               size=0.018, mat=CHROME, ext=0.0006, col='04_ENGINE_COOLING')
    # "DOHC" badge di cam cover
    text_decal('DOHC_%s'%('R' if s>0 else 'L'), 'DOHC',
               (s*0.078, 0.235, 0.575),
               (pi/2, -0.63, pi/2 if s<0 else -pi/2),
               size=0.015, mat=CHROME, ext=0.0006, col='04_ENGINE_COOLING')
    # "150cc" decal di engine side
    text_decal('Engine_150cc_%s'%('R' if s>0 else 'L'), '150cc',
               (s*0.135, -0.040, 0.380),
               (pi/2, 0, pi/2 if s<0 else -pi/2),
               size=0.010, mat=CHROME, ext=0.0004, col='04_ENGINE_COOLING')
    # "LIQUID COOLED" decal di engine
    text_decal('Liquid_cooled_%s'%('R' if s>0 else 'L'), 'LIQUID COOLED',
               (s*0.115, 0.090, 0.370),
               (pi/2, 0, pi/2 if s<0 else -pi/2),
               size=0.006, mat=CHROME, ext=0.0003, col='04_ENGINE_COOLING')
    # "SPORT" decal di side cover bawah
    text_decal('Sport_decal_%s'%('R' if s>0 else 'L'), 'SPORT',
               (s*0.150, 0.150, 0.250),
               (pi/2, 0, pi/2 if s<0 else -pi/2),
               size=0.014, mat=WDECAL, ext=0.0006)

# "Honda" decal di rear fender bawah
text_decal('Honda_rear', 'Honda',
           (0, -1.055, 0.440), (pi/2, 0, 0),
           size=0.024, mat=WDECAL, ext=0.0008)
# "HONDA" di nose fairing (dekat wing emblem)
text_decal('Honda_nose', 'HONDA',
           (0, 0.580, 0.700), (1.2, 0, 0),
           size=0.020, mat=CHROME, ext=0.0008)
# "HONDA" di rear (atas tail lamp)
text_decal('Honda_rear_top', 'HONDA',
           (0, -0.910, 0.830), (pi/2, 0, 0),
           size=0.018, mat=CHROME, ext=0.0008)
# "Honda" di engine top
text_decal('Honda_engine', 'Honda',
           (0, 0.245, 0.580), (pi/2, -0.63, 0),
           size=0.012, mat=CHROME, ext=0.0005, col='04_ENGINE_COOLING')
# "HONDA" di fuel tank top
text_decal('Honda_tank', 'HONDA',
           (0, 0.235, 0.590), (0, 0, 0),
           size=0.018, mat=CHROME, ext=0.0008, col='04_ENGINE_COOLING')
# "Honda" di fuel tank under seat
text_decal('Honda_tank_under', 'Honda',
           (0, -0.450, 0.700), (pi/2, 0, 0),
           size=0.014, mat=CHROME, ext=0.0006, col='04_ENGINE_COOLING')
# "NISSIN" badge di brake caliper
text_decal('Nissin_badge', 'NISSIN',
           (0.110, FRONT.y - 0.060, FRONT.z + 0.060),
           (pi/2, 0, -pi/2),
           size=0.005, mat=WDECAL, ext=0.0002, col='02_FRONT_RUNNING_GEAR')
# "DOT4" di brake fluid reservoir
text_decal('DOT4_decal', 'DOT4',
           (0.150, -0.392, 0.460), (pi/2, 0, -pi/2),
           size=0.006, mat=WDECAL, ext=0.0003, col='08_HARDWARE')
# "START" label di kick starter
text_decal('Kick_start_label', 'START',
           (0.175, -0.080, 0.480), (pi/2, 0, -pi/2),
           size=0.008, mat=WDECAL, ext=0.0003, col='07_CONTROLS_LIGHTS')

# ============================================================================
# 3. WHITE RACING STRIPES / CHEVRONS pada bodywork merah
# ============================================================================
for side in [-1, 1]:
    s = side
    def spts(seq): return [(s*x, y, z) for x, y, z in seq]
    # Chevron stripe di side fairing (3 segitiga putih bersusun)
    for i in range(3):
        y0 = 0.220 + i*0.085
        verts = spts([
            (0.132, y0, 0.690),
            (0.165, y0 - 0.020, 0.700),
            (0.132, y0 - 0.040, 0.690),
            (0.132, y0, 0.680),
        ])
        panel('Chevron_stripe_%s_%d'%(('R' if s>0 else 'L'), i),
              verts, WDECAL, '06_BODY_K56F', thick=0.0004)
    # Stripe putih pada FRONT_TOP_wing (fairing depan atas)
    verts = spts([
        (0.079, 0.378, 0.851),
        (0.155, 0.380, 0.837),
        (0.150, 0.420, 0.820),
        (0.075, 0.420, 0.835),
    ])
    panel('Front_stripe_%s'%('R' if s>0 else 'L'), verts, WDECAL, '06_BODY_K56F', thick=0.0004)
    # Stripe putih pada TAIL_COVER
    verts = spts([
        (0.080, -0.820, 0.788),
        (0.115, -0.700, 0.770),
        (0.110, -0.650, 0.758),
        (0.075, -0.780, 0.778),
    ])
    panel('Tail_stripe_%s'%('R' if s>0 else 'L'), verts, WDECAL, '06_BODY_K56F', thick=0.0004)
    # Stripe pada SIDE_COVER_outer_leg
    verts = spts([
        (0.180, 0.380, 0.460),
        (0.170, 0.280, 0.380),
        (0.175, 0.270, 0.350),
        (0.185, 0.370, 0.430),
    ])
    panel('Side_leg_stripe_%s'%('R' if s>0 else 'L'), verts, WDECAL, '06_BODY_K56F', thick=0.0004)

# ============================================================================
# 4. HEADLIGHT LED — DRL strip + projector lens + reflector bowl
# ============================================================================
# DRL strips (bright LED accent)
for side in [-1, 1]:
    s = side
    verts = [
        (s*0.065, 0.485, 0.985),
        (s*0.005, 0.485, 0.990),
        (s*0.005, 0.495, 0.982),
        (s*0.065, 0.495, 0.977),
    ]
    panel('Headlight_DRL_%s'%('R' if s>0 else 'L'), verts, LEDHUE,
          '07_CONTROLS_LIGHTS', thick=0.0015)

# Chrome projector ring (lebih besar)
bpy.ops.mesh.primitive_torus_add(major_radius=0.024, minor_radius=0.0020,
                                  location=(0, 0.515, 0.920),
                                  rotation=(pi/2, 0, 0))
finish(bpy.context.object, 'Headlight_projector_ring', CHROME, '07_CONTROLS_LIGHTS')

# Inner projector lens dome
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.022, location=(0, 0.520, 0.920))
lens_dome = finish(bpy.context.object, 'Headlight_projector_lens', LENS, '07_CONTROLS_LIGHTS')
lens_dome.scale = (1.0, 0.45, 1.0)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Inner reflector (chrome bowl di belakang lens)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.020, location=(0, 0.530, 0.920))
reflector = finish(bpy.context.object, 'Headlight_reflector_bowl', CHROME, '07_CONTROLS_LIGHTS')
reflector.scale = (1.0, 0.5, 1.0)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# ============================================================================
# 5. FORK STANCHION GOLD (anodized USD look)
# ============================================================================
for side in [-1, 1]:
    x = side * 0.091
    rod('Fork_stanchion_gold_%s'%('R' if side>0 else 'L'),
        (x, 0.545, 0.543), (x, 0.389, 0.920),
        0.017, GOLD, '02_FRONT_RUNNING_GEAR')
    rod('Fork_seal_retainer_%s'%('R' if side>0 else 'L'),
        (x, 0.548, 0.540), (x, 0.543, 0.550),
        0.026, CHROME, '02_FRONT_RUNNING_GEAR', vertices=48)
    # Fork gaiter (rubber boot)
    rod('Fork_gaiter_%s'%('R' if side>0 else 'L'),
        (x, 0.580, 0.500), (x, 0.545, 0.560),
        0.028, RUBBER, '02_FRONT_RUNNING_GEAR', vertices=32)
    # Fork axle pinch bolts
    for z_off in [0.005, 0.020, 0.035]:
        bolt('Fork_axle_pinch_%s_%d'%(('R' if side>0 else 'L'), int(z_off*1000)),
             x*1.28, 0.625, 0.321+z_off, 0.0045)

# ============================================================================
# 6. BRAKE CALIPERS — Titanium body + gold piston caps + Nissin badge
# ============================================================================
# Front brake caliper (titanium, gold pistons, large & visible)
fr_cal_x = 0.094
fr_cal_y = FRONT.y - 0.060
fr_cal_z = FRONT.z + 0.060
box('FR_Caliper_main', (fr_cal_x, fr_cal_y, fr_cal_z),
    (0.040, 0.075, 0.090), TITANI, '02_FRONT_RUNNING_GEAR', 0.012)
for i in range(2):
    rod('FR_Caliper_piston_%d'%i,
        (fr_cal_x + 0.022, fr_cal_y + (i-0.5)*0.025, fr_cal_z),
        (fr_cal_x + 0.028, fr_cal_y + (i-0.5)*0.025, fr_cal_z),
        0.011, GOLD, '02_FRONT_RUNNING_GEAR', vertices=32)
box('FR_Caliper_pad_slot', (fr_cal_x - 0.005, fr_cal_y, fr_cal_z),
    (0.012, 0.060, 0.080), DARKSTK, '02_FRONT_RUNNING_GEAR', 0.002)
box('FR_Caliper_badge', (fr_cal_x + 0.021, fr_cal_y, fr_cal_z - 0.020),
    (0.005, 0.020, 0.008), CHROME, '02_FRONT_RUNNING_GEAR', 0)
for z_off in [-0.030, 0.030]:
    bolt('FR_Caliper_bolt', fr_cal_x - 0.015, fr_cal_y, fr_cal_z + z_off, 0.005)
rod('FR_Caliper_hose_nipple',
    (fr_cal_x, fr_cal_y, fr_cal_z + 0.050),
    (fr_cal_x + 0.010, fr_cal_y, fr_cal_z + 0.055),
    0.006, CHROME, '02_FRONT_RUNNING_GEAR', vertices=16)

# Rear brake caliper (titanium, smaller)
rr_cal_x = 0.106
rr_cal_y = REAR.y - 0.040
rr_cal_z = REAR.z + 0.045
box('RR_Caliper_main', (rr_cal_x, rr_cal_y, rr_cal_z),
    (0.030, 0.055, 0.060), TITANI, '03_REAR_RUNNING_GEAR', 0.008)
for i in range(2):
    rod('RR_Caliper_piston_%d'%i,
        (rr_cal_x + 0.018, rr_cal_y + (i-0.5)*0.018, rr_cal_z),
        (rr_cal_x + 0.023, rr_cal_y + (i-0.5)*0.018, rr_cal_z),
        0.008, GOLD, '03_REAR_RUNNING_GEAR', vertices=24)
box('RR_Caliper_pad_slot', (rr_cal_x - 0.004, rr_cal_y, rr_cal_z),
    (0.010, 0.045, 0.055), DARKSTK, '03_REAR_RUNNING_GEAR', 0.001)

# ============================================================================
# 7. TIRE TREAD BLOCKS — Street sport pattern (sparser, thinner)
# ============================================================================
def add_tread_v7(label, center, width, height):
    col_name = '02_FRONT_RUNNING_GEAR' if label == 'FR' else '03_REAR_RUNNING_GEAR'
    x, y, z = center
    r = 0.2159 + height
    hw = width / 2
    num_blocks = 64 if label == 'FR' else 80
    for i in range(num_blocks):
        a = 2 * pi * i / num_blocks
        ang_dist = abs(((a - pi + pi) % (2*pi)) - pi)
        if ang_dist < 0.50: continue
        for x_off_frac in [-0.55, 0.0, 0.55]:
            bx = x + x_off_frac * hw
            by = y + (r - 0.001) * sin(a)
            bz = z + (r - 0.001) * cos(a)
            if bz < 0.020: continue
            chevron = 0.10 if (i % 2 == 0) else -0.10
            if x_off_frac == 0.0:
                block_size = (0.006, 0.012, 0.0020)
            else:
                block_size = (0.005, 0.008, 0.0025)
            if abs(x_off_frac) > 0.3 and i % 2 != 0: continue
            o = tread_block('%s_TreadV7_%s_%03d'%(label, '%.2f'%x_off_frac, i),
                           (bx, by, bz), *block_size, RUBBER, col_name)
            o.rotation_euler = (a + chevron, 0, 0)

add_tread_v7('FR', FRONT, 0.090, 0.072)
add_tread_v7('RR', REAR, 0.120, 0.084)

# ============================================================================
# 8. LICENSE PLATE — Visible di belakang rear wheel + side reflectors
# ============================================================================
# Plate background white
plate_bg = box('License_plate_BG', (0, -1.110, 0.380),
               (0.200, 0.005, 0.130), PLATEBG, '08_HARDWARE', 0.003)
# Plate text "GTR 150"
text_decal('License_plate_text', 'GTR 150',
           (0, -1.113, 0.380), (pi/2, 0, 0),
           size=0.045, mat=PLATETX, ext=0.0012, col='08_HARDWARE')
# Plate border frame
for side_y in [-1, 1]:
    box('License_plate_border_y_%d'%side_y,
        (0, -1.112, 0.380 + side_y*0.063),
        (0.200, 0.003, 0.003), DARKSTK, '08_HARDWARE', 0)
for side_z in [-1, 1]:
    box('License_plate_border_z_%d'%side_z,
        (side_z*0.100, -1.112, 0.380),
        (0.003, 0.003, 0.130), DARKSTK, '08_HARDWARE', 0)
# Side amber reflectors on plate
for side in [-1, 1]:
    s = side
    box('License_plate_side_reflector_%s'%('R' if s>0 else 'L'),
        (s*0.105, -1.110, 0.380),
        (0.005, 0.008, 0.080), AMBREF, '08_HARDWARE', 0)
    box('License_plate_side_bracket_%s'%('R' if s>0 else 'L'),
        (s*0.080, -1.100, 0.420),
        (0.005, 0.040, 0.080), DARK, '08_HARDWARE', 0.002)
# Plate mounting bracket
box('License_plate_bracket', (0, -1.080, 0.440),
    (0.060, 0.060, 0.005), DARK, '08_HARDWARE', 0.002)

# ============================================================================
# 9. REFLECTORS — Front amber, side amber, rear red
# ============================================================================
# Front amber reflectors on fork legs
for side in [-1, 1]:
    x = side * 0.091
    box('FR_Reflector_amber_%s'%('R' if side>0 else 'L'),
        (x, 0.580, 0.430),
        (0.020, 0.040, 0.012), AMBREF, '02_FRONT_RUNNING_GEAR', 0.003)
# Side amber reflectors (larger, more visible)
for side in [-1, 1]:
    s = side
    box('Side_reflector_amber_%s'%('R' if s>0 else 'L'),
        (s*0.140, 0.450, 0.200),
        (0.022, 0.080, 0.018), AMBREF, '06_BODY_K56F', 0.003)
# Rear red reflectors
for side in [-1, 1]:
    s = side
    box('RR_Reflector_red_%s'%('R' if s>0 else 'L'),
        (s*0.060, -1.060, 0.410),
        (0.018, 0.012, 0.040), REDREF, '07_CONTROLS_LIGHTS', 0.002)

# ============================================================================
# 10. CHROME EXHAUST TIP + HEAT SHIELD REFINEMENT
# ============================================================================
rod('Muffler_chrome_tip',
    (0.201, -0.854, 0.528),
    (0.202, -0.875, 0.534),
    0.025, CHROME, '05_DRIVETRAIN_EXHAUST', vertices=32)
rod('Muffler_tip_inner_sleeve',
    (0.202, -0.860, 0.530),
    (0.202, -0.875, 0.534),
    0.020, DARKSTK, '05_DRIVETRAIN_EXHAUST', vertices=32)
for y, z in [(-0.580, 0.480), (-0.680, 0.500)]:
    bolt('Heatshield_extra_bolt', 0.275, y, z, 0.004)
rod('Exhaust_hanger_rubber',
    (0.190, -0.760, 0.520),
    (0.186, -0.742, 0.680),
    0.012, RUBBER, '05_DRIVETRAIN_EXHAUST', vertices=16)

# ============================================================================
# 11. SIDE STAND SWITCH + BANK ANGLE SENSOR + WIRING
# ============================================================================
box('Side_stand_switch_L',
    (-0.140, -0.135, 0.260),
    (0.018, 0.024, 0.014), BLACK, '07_CONTROLS_LIGHTS', 0.002)
tube('Side_stand_switch_wire_L',
     [(-0.140, -0.135, 0.270), (-0.130, -0.150, 0.310), (-0.115, -0.180, 0.360)],
     0.0025, RUBBER, '07_CONTROLS_LIGHTS')
box('Bank_angle_sensor',
    (0.075, -0.250, 0.620),
    (0.022, 0.030, 0.014), DARK, '07_CONTROLS_LIGHTS', 0.002)
tube('Bank_angle_sensor_wire',
     [(0.075, -0.250, 0.615), (0.060, -0.230, 0.590), (0.040, -0.200, 0.575)],
     0.0022, RUBBER, '07_CONTROLS_LIGHTS')

# ============================================================================
# 12. COOLANT SIGHT WINDOW + OIL DRAIN BOLT + OIL LEVEL WINDOW
# ============================================================================
rod('Coolant_sight_window_R',
    (0.143, 0.332, 0.485), (0.146, 0.332, 0.485),
    0.008, LENS, '04_ENGINE_COOLING', vertices=24)
bolt('Oil_drain_bolt_R', 0.110, 0.020, 0.245, 0.006)
rod('Oil_sight_glass_ring_R',
    (0.153, -0.108, 0.300), (0.156, -0.108, 0.300),
    0.015, CHROME, '04_ENGINE_COOLING', vertices=32)
for z_off in [-0.010, 0.000, 0.010]:
    box('Reserve_tank_level_marker_%d'%int(z_off*1000),
        (0.158, 0.300, 0.440 + z_off),
        (0.002, 0.012, 0.001), DARKSTK, '04_ENGINE_COOLING', 0)

# ============================================================================
# 13. HANDLEBAR BAR-END WEIGHTS + SWITCH BUTTONS
# ============================================================================
for side in [-1, 1]:
    s = side
    rod('Bar_end_chrome_cap_%s'%('R' if s>0 else 'L'),
        (s*0.359, 0.272, 0.923), (s*0.362, 0.272, 0.923),
        0.014, CHROME, '07_CONTROLS_LIGHTS', vertices=32)
    box('Start_button_%s'%('R' if s>0 else 'L'),
        (s*0.222, 0.270, 0.940),
        (0.008, 0.006, 0.004), RED if s>0 else DARK, '07_CONTROLS_LIGHTS', 0)

# ============================================================================
# 14. FRAME RAIL PROTECTOR + ENGINE GUARD PLATE
# ============================================================================
for side in [-1, 1]:
    s = side
    tube('Frame_rail_protector_%s'%('R' if s>0 else 'L'),
         [(s*0.030, 0.435, 0.776), (s*0.065, 0.310, 0.655)],
         0.024, RUBBER, '01_CHASSIS')
box('Engine_skid_plate',
    (0, 0.020, 0.225),
    (0.220, 0.180, 0.008), DARK, '04_ENGINE_COOLING', 0.005)
for side in [-1, 1]:
    bolt('Skid_plate_bolt_%s'%('R' if side>0 else 'L'),
         side*0.090, 0.080, 0.225, 0.005)
    bolt('Skid_plate_bolt_rear_%s'%('R' if side>0 else 'L'),
         side*0.090, -0.040, 0.225, 0.005)

# ============================================================================
# 15. CHAIN GUARD EXTENSION + SPROCKET DETAIL
# ============================================================================
panel('Chain_guard_extension',
      [(-0.105, -0.450, 0.425), (-0.105, -0.580, 0.420),
       (-0.095, -0.580, 0.410), (-0.095, -0.450, 0.415)],
      BLACK, '05_DRIVETRAIN_EXHAUST', 0.004)
box('Front_sprocket_cover_L',
    (-0.110, -0.140, 0.360),
    (0.018, 0.060, 0.080), BLACK, '05_DRIVETRAIN_EXHAUST', 0.003)
for y_off in [-0.020, 0.020]:
    bolt('Sprocket_cover_bolt_L', -0.120, -0.140 + y_off, 0.395, 0.004)
# Rear sprocket rubber dampers
for i in range(5):
    a = i * 2 * pi / 5
    rad = 0.040
    rod('RR_Sprocket_damper_%d'%i,
        (-0.094, rear_sprocket.y + rad*sin(a), rear_sprocket.z + rad*cos(a)),
        (-0.090, rear_sprocket.y + rad*sin(a), rear_sprocket.z + rad*cos(a)),
        0.006, RUBBER, '05_DRIVETRAIN_EXHAUST', vertices=12)

# ============================================================================
# 16. CARBON-LOOK INNER DUCT PANEL
# ============================================================================
for side in [-1, 1]:
    s = side
    panel('Carbon_inner_duct_%s'%('R' if s>0 else 'L'),
          [(s*0.146, 0.195, 0.500), (s*0.158, 0.545, 0.700),
           (s*0.140, 0.560, 0.650), (s*0.130, 0.215, 0.460)],
          CARBON, '06_BODY_K56F', 0.0008)

# ============================================================================
# 17. SEAT RIBS + CENTER SEAM (ribbed vinyl texture)
# ============================================================================
for i in range(8):
    y_pos = -0.050 - i * 0.095
    tube('Seat_rib_%02d'%i,
         [(0, y_pos, 0.790), (0, y_pos - 0.040, 0.792)],
         0.0015, SEATMAT, '06_BODY_K56F')
tube('Seat_center_seam',
     [(0, -0.030, 0.792), (0, -0.780, 0.790)],
     0.0012, DARKSTK, '06_BODY_K56F')

# ============================================================================
# 18. BRAKE HOSE ROUTING + ABS SENSOR WIRE
# ============================================================================
box('FR_brake_hose_bracket',
    (0.105, 0.490, 0.520),
    (0.012, 0.018, 0.025), DARK, '02_FRONT_RUNNING_GEAR', 0.003)
tube('FR_wheel_speed_sensor_wire',
     [(0.090, 0.620, 0.310), (0.105, 0.580, 0.360), (0.108, 0.500, 0.430)],
     0.0020, RUBBER, '02_FRONT_RUNNING_GEAR')
box('RR_brake_hose_clip',
    (0.110, -0.450, 0.360),
    (0.010, 0.020, 0.012), DARK, '03_REAR_RUNNING_GEAR', 0.002)

# ============================================================================
# 19. TAIL LAMP LED SEGMENTS + CHROME RING
# ============================================================================
for i in range(3):
    z_off = 0.770 - i * 0.018
    panel('TAIL_LED_segment_%d'%i,
          [(-0.060, -0.945, z_off), (0.060, -0.945, z_off),
           (0.060, -0.948, z_off - 0.005), (-0.060, -0.948, z_off - 0.005)],
          LEDHUE, '07_CONTROLS_LIGHTS', 0.0010)
bpy.ops.mesh.primitive_torus_add(major_radius=0.045, minor_radius=0.0012,
                                  location=(0, -0.945, 0.745),
                                  rotation=(pi/2, 0, 0))
finish(bpy.context.object, 'Tail_lamp_chrome_ring', CHROME, '07_CONTROLS_LIGHTS')

# ============================================================================
# 20. WHEEL HUB DECALS + RIM EDGE DETAIL + VALVE STEM
# ============================================================================
for label, center in [('FR', FRONT), ('RR', REAR)]:
    col_name = '02_FRONT_RUNNING_GEAR' if label == 'FR' else '03_REAR_RUNNING_GEAR'
    width = 0.090 if label == 'FR' else 0.120
    rod('%s_Hub_center_cap'%label,
        (0, center.y, center.z), (0.005, center.y, center.z),
        0.020, CHROME, col_name, vertices=32)
    rod('%s_Hub_center_cap_L'%label,
        (0, center.y, center.z), (-0.005, center.y, center.z),
        0.020, CHROME, col_name, vertices=32)
    for side in [-1, 1]:
        s = side
        rod('%s_Axle_nut_cover_%s'%(label, 'R' if s>0 else 'L'),
            (s*0.115, center.y, center.z), (s*0.120, center.y, center.z),
            0.013, CHROME, col_name, vertices=24)
    # Rim lip chrome accent
    rw = (width/2) * 0.73
    ring('%s_Rim_lip_chrome'%label, center,
         [(-rw*.95, 0.225), (-rw*.95, 0.228), (-rw*.85, 0.228), (-rw*.85, 0.225)],
         CHROME, col_name, 96)
    # Hub chrome ring
    rod('%s_Hub_chrome_ring'%label,
        (0, center.y, center.z), (0.001, center.y, center.z),
        0.043, CHROME, col_name, vertices=64)
    rod('%s_Hub_chrome_ring_L'%label,
        (0, center.y, center.z), (-0.001, center.y, center.z),
        0.043, CHROME, col_name, vertices=64)
    # Valve stem
    rod('%s_Valve_stem'%label,
        (center.x + 0.045, center.y, center.z + 0.215),
        (center.x + 0.050, center.y, center.z + 0.218),
        0.003, CHROME, col_name, vertices=12)

# ============================================================================
# 21. BATTERY LABEL + REGULATOR RECTIFIER + MAIN WIRING HARNESS
# ============================================================================
box('Battery_label', (0, -0.187, 0.615),
    (0.060, 0.080, 0.001), DARKSTK, '04_ENGINE_COOLING', 0)
box('Regulator_rectifier',
    (-0.110, -0.180, 0.580),
    (0.030, 0.045, 0.020), SILVER, '04_ENGINE_COOLING', 0.005)
for i in range(5):
    box('Regulator_fin_%02d'%i,
        (-0.110, -0.180 + i*0.008, 0.590),
        (0.032, 0.001, 0.018), SILVER, '04_ENGINE_COOLING', 0)
tube('Main_harness',
     [(0.050, -0.180, 0.570), (0.040, -0.080, 0.590),
      (0.030, 0.020, 0.610), (0.020, 0.150, 0.640),
      (0.010, 0.280, 0.700), (0.005, 0.380, 0.780)],
     0.008, RUBBER, '07_CONTROLS_LIGHTS')
box('Starter_relay',
    (0.080, -0.210, 0.590),
    (0.022, 0.025, 0.018), BLACK, '07_CONTROLS_LIGHTS', 0.002)

# ============================================================================
# 22. SWINGARM CHAIN SLIDER + REAR AXLE NUTS
# ============================================================================
for side in [-1, 1]:
    s = side
    rod('RR_Axle_nut_%s'%('R' if s>0 else 'L'),
        (s*0.115, REAR.y, REAR.z), (s*0.125, REAR.y, REAR.z),
        0.018, CHROME, '03_REAR_RUNNING_GEAR', vertices=6)
    rod('RR_Axle_cotter_pin_%s'%('R' if s>0 else 'L'),
        (s*0.122, REAR.y + 0.012, REAR.z),
        (s*0.122, REAR.y + 0.012, REAR.z + 0.008),
        0.001, STEEL, '03_REAR_RUNNING_GEAR', vertices=8)
panel('Swingarm_chain_slider_L',
      [(-0.108, -0.200, 0.395), (-0.108, -0.350, 0.392),
       (-0.098, -0.350, 0.388), (-0.098, -0.200, 0.391)],
      RUBBER, '03_REAR_RUNNING_GEAR', 0.003)

# ============================================================================
# 23. TAIL TIDY + MUD FLAP
# ============================================================================
panel('Rear_mud_flap',
      [(-0.075, -1.095, 0.359), (0.075, -1.095, 0.359),
       (0.065, -1.180, 0.300), (-0.065, -1.180, 0.300)],
      BLACK, '06_BODY_K56F', 0.003)
box('License_lamp_bracket',
    (0, -0.960, 0.730),
    (0.090, 0.020, 0.015), DARK, '07_CONTROLS_LIGHTS', 0.002)

# ============================================================================
# 24. EXHAUST HEADER PORT + CYLINDER/HEAD COOLING FINS + ENGINE MOUNT PLATES
# ============================================================================
box('Exhaust_port_flange',
    (0.030, 0.230, 0.490),
    (0.022, 0.015, 0.025), DARK, '04_ENGINE_COOLING', 0.003)
for side in [-1, 1]:
    bolt('Exhaust_port_bolt_%s'%('R' if side>0 else 'L'),
         0.030 + side*0.010, 0.230, 0.490, 0.004)

# Cooling fins (gold anodized) on cylinder
cooling_fin('Cyl_cooling_fin', (0, 0.115, 0.450), (0, 1, 0),
            length=0.060, width=0.060, thickness=0.0015,
            count=8, pitch=0.007, mat=GOLD, col='04_ENGINE_COOLING')
# Cooling fins on cylinder head
cooling_fin('Head_cooling_fin', (0, 0.215, 0.540), (0, 1, 0),
            length=0.040, width=0.080, thickness=0.0012,
            count=5, pitch=0.006, mat=GOLD, col='04_ENGINE_COOLING')

# Engine mounting plates
for side in [-1, 1]:
    s = side
    box('Engine_mount_plate_%s'%('R' if s>0 else 'L'),
        (s*0.105, 0.020, 0.450),
        (0.010, 0.080, 0.060), DARK, '01_CHASSIS', 0.004)

# ============================================================================
# 25. THROTTLE / CLUTCH / BRAKE CABLES (thicker, visible)
# ============================================================================
tube('Throttle_cable_V7',
     [(0.226, 0.290, 0.921), (0.180, 0.310, 0.880),
      (0.130, 0.320, 0.820), (0.090, 0.290, 0.720),
      (0.060, 0.200, 0.650), (0.050, 0.090, 0.620)],
     0.0040, RUBBER, '07_CONTROLS_LIGHTS')
tube('Clutch_cable_V7',
     [(-0.216, 0.302, 0.914), (-0.150, 0.315, 0.860),
      (-0.110, 0.270, 0.770), (-0.130, 0.180, 0.660),
      (-0.140, 0.050, 0.580), (-0.137, -0.046, 0.448)],
     0.0040, RUBBER, '07_CONTROLS_LIGHTS')
tube('Front_brake_hose_V7',
     [(0.183, 0.322, 0.931), (0.150, 0.350, 0.870),
      (0.120, 0.380, 0.790), (0.100, 0.420, 0.680),
      (0.094, 0.480, 0.580), (0.094, 0.540, 0.480),
      (0.094, 0.580, 0.420)],
     0.0045, RUBBER, '07_CONTROLS_LIGHTS')
# Cable housings at handlebar end
box('Throttle_cable_housing_R',
    (0.215, 0.295, 0.920),
    (0.020, 0.012, 0.008), BLACK, '07_CONTROLS_LIGHTS', 0.002)
box('Clutch_cable_housing_L',
    (-0.210, 0.305, 0.915),
    (0.020, 0.012, 0.008), BLACK, '07_CONTROLS_LIGHTS', 0.002)

# ============================================================================
# 26. MIRROR GLASS (larger, with chrome trim)
# ============================================================================
for side in [-1, 1]:
    s = side
    # Remove existing mirror reflector if any
    name = 'Mirror_reflector_%s'%('R' if s>0 else 'L')
    if name in bpy.data.objects:
        old = bpy.data.objects[name]
        for c in list(old.users_collection): c.objects.unlink(old)
        bpy.data.objects.remove(old, do_unlink=True)
    # Larger mirror glass
    glass_points = [(s*0.299 + 0.050*cos(i*2*pi/32), 0.342, 1.068 + 0.028*sin(i*2*pi/32))
                    for i in range(32)]
    panel('Mirror_reflector_V7_%s'%('R' if s>0 else 'L'),
          glass_points, MIRROR, '07_CONTROLS_LIGHTS', 0.0010)

# ============================================================================
# 27. SUBDIVISION SURFACE untuk bodywork smoother
# ============================================================================
body_panel_prefixes = ['SIDE_COVER_upper_', 'SIDE_COVER_outer_leg_',
                       'FRONT_TOP_wing_', 'FRONT_TOP_center_',
                       'TAIL_COVER_', 'SEAT_', 'FENDER_A_FR_']
for o in list(bpy.data.objects):
    if o.type != 'MESH': continue
    if not any(o.name.startswith(p) for p in body_panel_prefixes): continue
    for p in o.data.polygons: p.use_smooth = True
    if 'Subsurf_V7' not in [m.name for m in o.modifiers]:
        m = o.modifiers.new('Subsurf_V7', 'SUBSURF')
        m.levels = 1
        m.render_levels = 2

print('V7_ENHANCEMENT_COMPLETE', flush=True)

# UVs per part, consistent normals and visible origin at each object's geometry centre.
# Panels retain solidify/bevel stacks; no destructive overall scaling.
bpy.ops.object.select_all(action='DESELECT')
for o in list(bpy.data.objects):
    if o.type!='MESH' or '90_STUDIO' in [c.name for c in o.users_collection]:continue
    bpy.context.view_layer.objects.active=o;o.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.uv.smart_project(angle_limit=1.15192,island_margin=.015)
    bpy.ops.object.mode_set(mode='OBJECT');bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY',center='BOUNDS');o.select_set(False)

# Keep all authoring/evidence in the project and the native blend.
for filename in ['build_k56f.py','REFERENCES.md']:
    path=OUT/filename
    if path.exists():
        t=bpy.data.texts.new(filename);t.write(path.read_text(encoding='utf-8'))

def validate():
    bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
    bounds=[];bad=[];zero=[];inventory=[];lowest=[]
    for o in scene.objects:
        if o.type not in {'MESH','CURVE'} or any(c.name in {'90_STUDIO','09_REFERENCE_IMAGES'} for c in o.users_collection):continue
        ob=o.evaluated_get(deps)
        evaluated_mesh=ob.to_mesh()
        bb=[ob.matrix_world@v.co for v in evaluated_mesh.vertices]
        ob.to_mesh_clear()
        bounds.extend(bb)
        if bb:lowest.append((min(v.z for v in bb),o.name))
        if any(not math.isfinite(v) for p in bb for v in p):bad.append(o.name)
        if o.type=='MESH' and any(p.area<1e-12 for p in o.data.polygons):zero.append(o.name)
        inventory.append(dict(name=o.name,type=o.type,collection=o.users_collection[0].name,vertices=len(o.data.vertices) if o.type=='MESH' else None,confidence=o.get('geometry_confidence','estimated')))
    lo=[min(v[i] for v in bounds) for i in range(3)];hi=[max(v[i] for v in bounds) for i in range(3)]
    report={'status':'reference reconstruction; not manufacturing CAD','units':'metres, scale_length=1','axes':{'X':'right','Y':'front','Z':'up'},'wheelbase_m':(FRONT-REAR).y,'front_tire_OD_m':2*RF,'rear_tire_OD_m':2*RR,'contact_z_m':[FRONT.z-RF,REAR.z-RR],'rider_seat_station_m':.780,'bounding_box_min_m':lo,'bounding_box_max_m':hi,'envelope_width_length_height_m':[hi[i]-lo[i] for i in range(3)],'nonfinite_geometry':bad,'zero_area_base_faces':zero,'objects':len(inventory),'known_limits':['External reconstruction; internal engine/transmission omitted.','Mount centres and hidden geometry inferred; not physically measured.','Unloaded nominal tire profile; no sag simulation.','No OEM decal artwork or mould tooling surfaces.','No suspension/steering motion clearance certification.'],'inventory':inventory}
    report['lowest_objects']=sorted(lowest)[:12]
    (OUT/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('LOWEST_GEOMETRY',sorted(lowest)[:12],flush=True)
    assert scene.unit_settings.scale_length==1.0
    assert abs(report['wheelbase_m']-1.284)<1e-6
    assert max(abs(x) for x in report['contact_z_m'])<1e-6
    assert not bad and not zero,(bad,zero)
    assert lo[2]>-1e-6,'Unexpected geometry below ground'
    (OUT/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('K56F_VALIDATION',json.dumps({k:v for k,v in report.items() if k!='inventory'}),flush=True)
    return report
validate()
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.region_3d.view_distance=3.0
        area.spaces.active.region_3d.view_location=(0,0,.55)
        area.spaces.active.clip_start=.001;area.spaces.active.clip_end=100
        area.spaces.active.shading.type='MATERIAL'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Honda_Supra_GTR150_K56F_V1.blend'))
if RENDER:
    for cam,name in [(hero,'preview_hero'),(right,'view_right'),(left,'view_left'),(front,'view_front'),(rear,'view_rear'),(top,'view_top')]:
        scene.camera=cam;scene.render.filepath=str(OUT/(name+'.png'))
        bpy.data.objects['Studio_floor'].hide_render=cam!=hero
        bpy.ops.render.render(write_still=True)
    scene.camera=hero;scene.render.filepath=str(OUT/'preview_hero.png');bpy.data.objects['Studio_floor'].hide_render=False
print('K56F_BUILD_COMPLETE',flush=True)
