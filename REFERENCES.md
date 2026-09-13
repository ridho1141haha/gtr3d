# Honda Supra GTR 150 K56F / FS150FG V1 reconstruction

## V1.1 architectural and geometric revision

A second review pass corrected silhouette, proportion and mechanism errors without changing the generation anchor or evidence base. All corrections are authored estimates; no OEM dimensions were invented. Catalog-block items added by part family: radiator reserve tank (F-35), chain slider/buffer (F-38), rear brake master cylinder and reservoir (F-11), handlebar balancers (F-7), O2 sensor boss and lead (F-30), license plate lamp (F-29).

Key changes, by area:
- Nose: beak tip extended forward (sharp underbone wedge, tip near Y=+0.75), headlamp module recessed rearward behind the beak leading edge, multi-tier winker housing with the clear lens set deeper and a separate position-light bar.
- Tail: increased upward rake of the tail cover and subframe; rear lamp/winkers follow; license lamp added.
- Layered cowl: side fairing flared wider (approx. +40 mm span) and a black inner duct panel added with standoff spacers, forming an open air channel ahead of the radiator.
- Wheels: split-Y cast spoke architecture with hub web and branch gussets (visual, not an OEM casting section).
- Brakes: 5-bolt rotor carrier arrangement; heavy boolean drilling replaced with staggered vent dots; rear master cylinder, pushrod, remote reservoir, hose and clamps added.
- Suspension: monoshock lower anchor raised onto a welded swingarm arch, clear of the rear tire envelope; swingarm section now tapers toward the dropouts.
- Engine: throttle body re-oriented rearward-upward with an intake duct to the airbox; clutch cover stepped profile, cap bolts and sight glass added; generator cover ribs; spark plug cap and HT lead; coolant hose clamps.
- Exhaust: silencer rebuilt as a flattened asymmetric swept section with flat inner clearance face; O2 sensor boss added.
- Fasteners: generic hex-prism bolts replaced by an instanced JIS-style flange-bolt library (integral flange, small hex head, stylised thread ridges) and push-pin rivets with dark countersink dishes at body panels. The thread is a visual representation; no grade or pitch is claimed.
- Removed: invented frame crossmembers (replaced with gusset plates and battery cage brackets), seat welt piping; front fender now drops toward an arrowhead tip; backbone cover extended to meet the seat nose.

Internal engine components remain omitted (optional cutaway scope). Confidence notes on each object still mark estimated geometry.

## Deliverable and accuracy boundary

Editable, full-scale Blender external reconstruction, anchored to the 2016 K56F generation. This is not Honda CAD, a measured scan, or a fabrication-ready replacement-part model. Exploded drawings establish part identity and relationships, but do not dimension the exterior surfaces or mounting coordinates. Unmeasured geometry is explicitly marked in object custom properties. No donor motorcycle geometry was used.

The user requested the 2016-2019 V1 family. The geometric anchor is **2016 FS150FG**, not an assertion that every 2019/FS150FL machine is V1. Later color/decal variants are not reproduced. The red finish is a visual approximation of the 2016 red option; OEM decals are omitted rather than fabricated.

## Accepted evidence

1. Honda/AHM **Supra GTR 150 (FS150F)** parts catalog, issued **01 March 2016**. Catalog text identifies 2016 FS150FG. Locally retained as `references/K56F_2016_AHM_parts.pdf` (107 PDF pages).
   - Discovery: https://www.hondacengkareng.com/catalogs/katalog-suku-cadang-honda-supra-gtr-150-k56f/
   - Indexed Honda document: https://www.hondacengkareng.com/wp-content/uploads/2016/02/Katalog-Suku-Cadang-Honda-Supra-GTR-K56F-1.pdf
   - Successful download of the 2016 Honda document from dealer mirror: https://nambomotor.com/katalog/CUB/SUPRA%20GTR%20150%20%28K56F%29%20MEI%202016-2018.pdf
   - Visually inspected F-1, F-7, F-14-40, F-23, F-23-10, F-29, F-39, F-44, F-49 and F-50. Extracted other running-gear sheets for review. PDF page numbers are not printed catalog page numbers.
   - Parts metadata names are identity references, not guarantees of dimensionally exact replicas.
2. Honda's official 2016MY publication index: https://www.hondamotopub.com/model/AHJ/K56161/
3. 2016 FS150FG model/color identification: https://www.bike-parts-honda.com/honda-motorcycle/150-MOTO/GTR/2016/FS150FG/39021
4. Original-generation launch image set, published May 2016, visually cross-checked against the Honda catalog. These are perspective product images, not calibrated orthographic photographs. Red, white and dark-color images show the same camera angle, so they do not independently constrain unseen surfaces.
   - Context: https://paultan.org/2016/05/31/2016-honda-supra-gtr-150-in-indonesia-rm6400/
   - Main red image: https://paultan.org/image/2016/05/2016-Honda-Supra-GTR-150-1-e1464665050191.jpg
   - Color images: `2016-Honda-Supra-GTR-150-2.jpg`, `-3.jpg`, `-4.jpg` under the same URL directory.
   - Only visible photographs are used as shape evidence; no secondary article technical claims are used as engineering dimensions.
5. User-provided baseline: length 2025 mm; width 725 mm; height 1102 mm; wheelbase 1284 mm; seat 780 mm; clearance 150 mm; tires 90/80-17 and 120/70-17; empty mass reference 119 kg; tank nominal capacity 4.5 L; supplied engine data.

## Rejected / quarantined references

- Existing workspace `make_supra_gtr.py`, `SupraGTR_RS150.blend`, and `RS150_Custom_Realistic.blend`: mixed model identities and dimensions. Not imported, modified, or reused as geometry.
- K56W catalog and September 2019 street-sport facelift imagery: excluded from modeling.
- The 2019 Honda catalog lists **FS150FL** with **KB22** engine/frame series. This is evidence of a generation-identification conflict, not permission to import its body design. https://2rom-prd-data.hondamotopub.com/pc/AHJ/SUPRA%20GTR150/2019/PC_SUPRA%20GTR150.pdf
- Current dealer product page dimensions 2025 x 705 x 1105 mm are not substituted for the user's V1 baseline. The current page mixes later products and cannot establish the requested generation.
- Winner, Winner X, RS150R, Sonic, aftermarket bodywork and adventure-show-bike photographs are not accepted geometry references.

## Dimensions, datums and confidence

Blender: metric, `scale_length=1.0`, one unit = one metre. X is right/left, +Y front, +Z up. The motorcycle is centered at X=0; intentional asymmetries include left chain drive and right exhaust. `REF_ORIGIN` is the vehicle master; `GROUND_PLANE` is an Empty at Z=0. Studio objects are independent.

| Quantity | Model basis | Confidence |
|---|---|---|
| Wheelbase | Front Y=+0.642, rear Y=-0.642 m | Exact supplied baseline |
| Front nominal tire OD | 431.8 + 2 x 72 = 575.8 mm | Exact designation arithmetic; no tire load deformation |
| Rear nominal tire OD | 431.8 + 2 x 84 = 599.8 mm | Exact designation arithmetic; no tire load deformation |
| Axle Z | Front 0.2879, rear 0.2999 m | Derived from nominal tire envelope |
| Seat datum | Rider station Y=-0.190, Z=0.780 m | Baseline-constrained; no foam compression |
| Clearance datum | Lower fairing center Z=0.150 m | Baseline target; evaluated envelope reported separately |
| Swingarm pivot | Y=-0.105, Z=0.390 m | Estimate, not Honda dimension |
| Steering head | Lower (0,0.433,0.740); upper (0,0.368,0.900) m | Estimate, not Honda rake/trail data |
| Body surface widths and curvature | Catalog + perspective silhouette | Moderate/low; no orthographic survey |
| Case castings, brackets, hose paths | External shapes and plausible connections | Moderate/low; no manufacturing detail |
| Overall L/W/H | Recorded from evaluated scene in validation.json | Never used to arbitrarily rescale individual components |

119 kg and 4.5 L are metadata only. Mesh densities do not simulate mass and the estimated tank surface does not certify internal capacity. Bore, stroke and compression are metadata; internal moving engine/transmission parts are not modeled.

## Editing and regeneration

- Open `Honda_Supra_GTR150_K56F_V1.blend` in Blender 4.5 or newer.
- Major systems are named collections. Geometry is separated into parts; panel thickness and edge radii remain modifiers. Mesh parts have initial UV islands. Materials are procedural and reference images are packed.
- The scene includes six orthographic review cameras; the hero camera is also orthographic to reduce perspective distortion during review.
- Reference cards are in the hidden `09_REFERENCE_IMAGES` collection. They are explicitly **uncalibrated** and must not be treated as scale blueprints.
- `build_k56f.py` and this file are also embedded in Blender Text datablocks. The script rebuilds a new scene; run it in a separate Blender process, not in an unsaved working scene.
- Regenerate with `blender --background --factory-startup --python build_k56f.py`. Append `-- --no-render` to skip image rendering.
- Rebuilding overwrites this generated model and its outputs. Preserve manual edits under a new filename first.
- The script needs Blender only. `.tools/` was used solely to inspect PDF references and is not required to build the model.

## Verification and remaining limitations

`validation.json` records evaluated vertex bounds, unit settings, nominal wheel/contact arithmetic, object inventory, non-finite vertices and zero-area base faces. `saved_model_QA.json` independently checks the saved file, including tire mesh dimensions, UVs, packed references, unit transforms and sampled static body/tire clearance. These checks do not certify fitment, moving suspension clearance, manifold solids, quad-only topology, or CAD tolerances. Modifier-based panel shells and tubing are visualization geometry. Tread is recessed into the tire mesh as an estimated pattern; an exact tire mold pattern is not reconstructed.

No hidden mounting measurements, structural analysis, exact OEM decals, animation rig, collision model, suspension sag, or material certification is claimed. External mechanical assemblies are editable approximations. Manufacturing-ready reconstruction would need measured orthographic views or a scan, casting details, tolerances and systematic interference checks.
