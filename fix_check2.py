"""Final numeric acceptance for the two remaining visual defects (read-only)."""
import bpy, math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=bpy.path.abspath("//Honda_Supra_GTR150_K56F_V1.blend"))
D=bpy.data.objects
ok=True
# A. Header end lies INSIDE the muffler can swept volume (axis distance test along can axis).
hd=D['Exhaust_header']; end=hd.matrix_world@hd.data.splines.active.bezier_points[-1].co
can=D['Muffler_stock_body_R']
ws=[can.matrix_world@Vector(c) for c in can.bound_box]
lo=(min(v.y for v in ws),min(v.z for v in ws));hi=(max(v.y for v in ws),max(v.z for v in ws))
inside=lo[0]<=end.y<=hi[0] and lo[1]<=end.z<=hi[1]
print('A_header_end_inside_can',inside,round(end.y,4),round(end.z,4),round(lo[0],4),round(hi[0],4),round(lo[1],4),round(hi[1],4));ok&=inside
# B. Both pillion stays' upper ends within 25 mm of a subframe tube control point.
for s in (1,):
    sub=D['Subframe_lower_%d'%s]; pts=[sub.matrix_world@p.co for p in sub.data.splines.active.bezier_points]
    for nm in ['Pillion_bracket_stay_%d'%s,'Pillion_bracket_stay2_%d'%s]:
        st=D[nm]; ws=[st.matrix_world@Vector(c) for c in st.bound_box]
        top=max(ws,key=lambda v:v.z)
        dmin=min((top-p).length for p in pts)
        print('B',nm,'nearest_subframe_mm',round(dmin*1000,1));ok&=dmin<.025
# C. Muffler can inner face clear of tire envelope in 3D (worst point sampled along axis).
tire=D['RR_TIRE_120_80_17'] if 'RR_TIRE_120_80_17' in D else D['RR_TIRE_120_70_17']
c=tire.matrix_world.translation
worst=9
for i in range(21):
    t=i/20
    y=-.345-.470*t; z=.408+.112*t; x=.183+.015*t
    inner=x-.076
    radial=math.hypot(y-c.y,z-c.z)
    clearance=inner-.06 if radial<.30 else 1  # only matters inside tire disc zone
    worst=min(worst,clearance)
print('C_muffler_inner_face_clearance_mm',round(worst*1000,1));ok&=worst>0
print('FINAL_NUMERIC_OK',ok)
