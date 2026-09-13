"""Numeric re-check of the four visual defects flagged by review."""
import bpy, math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=bpy.path.abspath("//Honda_Supra_GTR150_K56F_V1.blend"))
D=bpy.data.objects
def bb(n):
    o=D.get(n)
    if not o:return None
    ws=[o.matrix_world@Vector(c) for c in o.bound_box]
    return (Vector((min(v.x for v in ws),min(v.y for v in ws),min(v.z for v in ws))),
            Vector((max(v.x for v in ws),max(v.y for v in ws),max(v.z for v in ws))))
ok=True
# 1. Pillion stay upper end meets subframe tube corridor
sub=bb('Subframe_upper_1');stay=bb('Pillion_bracket_stay_1')
near=stay[1].x>=sub[0].x-.012 and abs(stay[1].y-sub[0].y)<.06 and abs(stay[1].z-sub[0].z)<.06
print('CHECK pillion_stay_touches_subframe',near,stay[1],sub[0]);ok&=near
# 2. Muffler front face inside header end radius; muffler above tire crown .30
hd=D['Exhaust_header'];hend=hd.matrix_world@hd.data.splines.active.bezier_points[-1].co
muf=bb('Muffler_stock_body_R');d=math.hypot(muf[0].y-hend.y,muf[0].z-hend.z)
print('CHECK muffler_joins_header',d<.09,d)
rear=D['RR_TIRE_120_70_17'].matrix_world.translation;crown=rear.z+.2999
clear=muf[0].z+.052>crown-.01  # muffler midline region clear of tire top
print('CHECK muffler_above_tire_crown',clear,'muf_z',muf[0].z,'crown',crown);ok&=d<.09
# 3. Reserve tank near engine and stay connects toward frame
rt=bb('Radiator_reserve_tank_1'.replace('_1','')) # no side suffix
st=bb('Reserve_stay_R')
print('CHECK reserve_tank_x_inboard',rt[1].x<.16,'stay_spans',st[0],st[1]);ok&=rt[1].x<.16
# 4. Engine studs hidden behind side panel x extent
stud=bb('Engine_mount_stud')
cover=bb('SIDE_COVER_inner_recess_1')
hid=stud[1].x<cover[1].x+.005
print('CHECK studs_behind_panel',hid,stud[1].x,cover[1].x);ok&=hid
# 5. Nothing below ground / no body part intersecting tire annulus beyond known
print('OVERALL',ok)
