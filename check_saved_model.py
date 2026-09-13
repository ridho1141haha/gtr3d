"""Read-only acceptance checks on the saved Blender file; writes QA report."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(out/'Honda_Supra_GTR150_K56F_V1.blend'))
s=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get()
checks={};details={}
checks['metres']=s.unit_settings.system=='METRIC' and s.unit_settings.scale_length==1
checks['origin_identity']=all(abs(v)<1e-9 for v in bpy.data.objects['REF_ORIGIN'].location)
checks['ground_z_zero']=abs(bpy.data.objects['GROUND_PLANE'].matrix_world.translation.z)<1e-9
f=bpy.data.objects['REF_FRONT_AXLE'].matrix_world.translation
r=bpy.data.objects['REF_REAR_AXLE'].matrix_world.translation
checks['actual_axle_wheelbase_1284mm']=abs(f.y-r.y-1.284)<1e-7 and abs(f.x)<1e-7 and abs(r.x)<1e-7
for name,width,diameter in [('FR_TIRE_90_80_17',.09,.5758),('RR_TIRE_120_70_17',.12,.5998)]:
    o=bpy.data.objects[name];e=o.evaluated_get(deps)
    points=[e.matrix_world@v.co for v in e.data.vertices]
    lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)])
    size=hi-lo
    checks[name+'_ground_contact']=abs(lo.z)<1e-7
    checks[name+'_width_OD']=abs(size.x-width)<1e-7 and abs(size.y-diameter)<1e-7 and abs(size.z-diameter)<1e-7
    checks[name+'_centred']=abs((lo.x+hi.x)/2)<1e-7
    details[name]={'width_m':size.x,'diameter_m':size.z,'ground_contact_z':lo.z}
seat=bpy.data.objects['SEAT_77200_K56_N10']
seat_points=[seat.matrix_world@v.co for v in seat.data.vertices]
station=[p.z for p in seat_points if abs(p.y+.190)<1e-6]
checks['actual_rider_seat_cage_780mm']=bool(station) and abs(max(station)-.780)<1e-6
checks['all_reference_images_packed']=all(i.packed_file is not None for i in bpy.data.images if i.name not in {'Render Result','Viewer Node'} and i.source=='FILE')
meshes=[o for o in s.objects if o.type=='MESH' and o.users_collection[0].name!='90_STUDIO']
checks['all_vehicle_meshes_have_uv']=all(len(o.data.uv_layers)>0 for o in meshes)
checks['all_vehicle_meshes_have_material']=all(len(o.data.materials)>0 for o in meshes)
# Fastener instances share prototype meshes and carry one uniform size scale;
# any non-uniform or negative scale is still rejected (no arbitrary component rescaling).
checks['all_vehicle_meshes_unit_scale']=all(len({round(v,9) for v in o.scale})==1 and o.scale[0]>0 for o in meshes)
checks['no_prohibited_donor_object_names']=not any(any(t in o.name.lower() for t in ['rs150','winner','sonic','k56w','mx king']) for o in s.objects)
checks['script_embedded']='build_k56f.py' in bpy.data.texts
checks['evidence_embedded']='REFERENCES.md' in bpy.data.texts
checks['six_review_cameras']=len([o for o in s.objects if o.type=='CAMERA'])==6
# Sample actual body shell triangles against conservative central tire envelopes.
# Static pose only; wheel annulus test, not complete moving-part certification.
suspects=[]
for o in meshes:
    if o.users_collection[0].name!='06_BODY_K56F':continue
    ob=o.evaluated_get(deps);me=ob.to_mesh();me.calc_loop_triangles()
    for axle,halfwidth,outer in [(f,.038,.5758/2),(r,.052,.5998/2)]:
        hit=False
        for tri in me.loop_triangles:
            points=[ob.matrix_world@me.vertices[i].co for i in tri.vertices]
            samples=points+[(points[0]+points[1]+points[2])/3]
            for p in samples:
                radial=math.hypot(p.y-axle.y,p.z-axle.z)
                if abs(p.x)<halfwidth and .222<radial<outer-.005:
                    hit=True;break
            if hit:break
        if hit:suspects.append(o.name)
    ob.to_mesh_clear()
checks['no_sampled_body_tire_penetration']=not suspects
details['body_tire_sampling_suspects']=suspects
report={'checks':checks,'details':details,'mesh_objects':len(meshes),'base_mesh_vertices':sum(len(o.data.vertices) for o in meshes),'failed':[k for k,v in checks.items() if not v]}
(out/'saved_model_QA.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2),flush=True)
assert all(checks.values()),report['failed']
