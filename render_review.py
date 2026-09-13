"""Render the saved reconstruction with unclipped review cameras."""
import bpy
from pathlib import Path
out=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(out/'Honda_Supra_GTR150_K56F_V1.blend'))
s=bpy.context.scene
for name,scale in [('CAM_FRONT',1.70),('CAM_REAR',1.70),('CAM_TOP',3.10)]:bpy.data.objects[name].data.ortho_scale=scale
for name,value in [('ABS_black',.22),('Seat_vinyl',.20)]:bpy.data.materials[name].node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=value
for filename in ['build_k56f.py','REFERENCES.md']:
    t=bpy.data.texts.get(filename) or bpy.data.texts.new(filename);t.clear();t.write((out/filename).read_text(encoding='utf-8'))
s.camera=bpy.data.objects['CAM_HERO_RIGHT_FRONT'];bpy.data.objects['Studio_floor'].hide_render=False
s.render.filepath=str(out/'preview_hero.png')
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'Honda_Supra_GTR150_K56F_V1.blend'))
for camera,filename in [('CAM_HERO_RIGHT_FRONT','preview_hero'),('CAM_RIGHT','view_right'),('CAM_LEFT','view_left'),('CAM_FRONT','view_front'),('CAM_REAR','view_rear'),('CAM_TOP','view_top')]:
    s.camera=bpy.data.objects[camera];bpy.data.objects['Studio_floor'].hide_render=camera!='CAM_HERO_RIGHT_FRONT'
    s.render.filepath=str(out/(filename+'.png'));bpy.ops.render.render(write_still=True)
print('FINAL_REVIEW_RENDER_COMPLETE',flush=True)
