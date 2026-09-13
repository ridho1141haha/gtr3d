"""Audit-only inspection of the existing K56F V1 scene. Read-only; saves nothing."""
import bpy, json, math
from mathutils import Vector

blend = bpy.path.abspath("//Honda_Supra_GTR150_K56F_V1.blend")
bpy.ops.wm.open_mainfile(filepath=blend)
s = bpy.context.scene
rep = {"scene": s.name, "unit_scale": s.unit_settings.scale_length,
       "unit_system": s.unit_settings.system, "collections": {}, "objects": [],
       "empties": [], "cameras": [], "materials": [], "modifiers": {}}

def bbox(o):
    if o.type != 'MESH':
        return None
    ws = [o.matrix_world @ Vector(c) for c in o.bound_box]
    mn = Vector((min(v.x for v in ws), min(v.y for v in ws), min(v.z for v in ws)))
    mx = Vector((max(v.x for v in ws), max(v.y for v in ws), max(v.z for v in ws)))
    return {"min": [round(v, 4) for v in mn], "max": [round(v, 4) for v in mx],
            "size": [round(v, 4) for v in (mx - mn)]}

def walk(coll):
    for c in coll.children:
        if c.name in done:
            continue
        done.add(c.name)
        rep["collections"][c.name] = {"objects": len(c.objects), "children": [ch.name for ch in c.children], "names": [o.name for o in c.objects]}
        walk(c)

done = set()
walk(bpy.context.scene.collection)

for o in bpy.data.objects:
    entry = {"name": o.name, "type": o.type, "colls": [c.name for c in o.users_collection],
             "verts": len(o.data.vertices) if o.type == 'MESH' else None,
             "hidden": o.hide_render, "parent": o.parent.name if o.parent else None,
             "loc": [round(v, 4) for v in o.location]}
    if o.type == 'MESH':
        entry["bbox"] = bbox(o)
        entry["mods"] = [(m.name, m.type) for m in o.modifiers]
        key = tuple(sorted(m.type for m in o.modifiers))
        rep["modifiers"][str(key)] = rep["modifiers"].get(str(key), 0) + 1
        entry["mats"] = [m.name for m in o.data.materials]
    elif o.type == 'EMPTY':
        rep["empties"].append(entry)
    elif o.type == 'CAMERA':
        rep["cameras"].append(entry["name"])
    rep["objects"].append(entry)

rep["materials"] = [m.name for m in bpy.data.materials]
rep["texts"] = [t.name for t in bpy.data.texts]
rep["images_packed"] = sorted({i.name for i in bpy.data.images if i.packed_file})

# chassis QA from known key objects
def gb(n):
    o = bpy.data.objects.get(n)
    return bbox(o) if o else None

rep["qa"] = {}
for key in ["FR_TIRE_90_80_17", "RR_TIRE_120_70_17", "FR_WHEEL", "RR_WHEEL",
            "ENGINE_BLOCK", "ENGINE_CASE_L", "ENGINE_CASE_R", "SEAT", "SWINGARM", "FRAME"]:
    m = gb(key)
    if m:
        rep["qa"][key] = m

rep["counts"] = {"mesh": sum(1 for o in bpy.data.objects if o.type == 'MESH'),
                 "total": len(bpy.data.objects)}

with open(bpy.path.abspath("//audit_scene.json"), "w", encoding="utf-8") as f:
    json.dump(rep, f, indent=1)
print("AUDIT_OK objects=%d mesh=%d" % (len(bpy.data.objects), rep["counts"]["mesh"]))
