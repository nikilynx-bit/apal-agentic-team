"""BRAWN offline assurance core. This is NOT a deployed LLM or engineering solver.
All case records and approvals in this module are synthetic unit-test fixtures.
"""
from __future__ import annotations
import csv, hashlib, json, math, os, re, struct
from datetime import datetime, timezone
from pathlib import Path

POLICY_VERSION = 'brawn-pep-1.1.0'
SCHEMA_VERSION = 'brawn-case-1.0'
FORBIDDEN = {'audit_delete', 'modify_regulation', 'disable_monitoring', 'override_safety'}
OUTPUT_STATES = {'SANDBOX_CONCEPT', 'HOLD_FOR_EVIDENCE', 'HUMAN_REVIEW', 'RELEASED_BY_AUTHORITY'}

class ControlledError(ValueError):
    def __init__(self, code, detail):
        self.code, self.detail = code, detail
        super().__init__(f'{code}: {detail}')

def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def image_intake(media_type, filename, size_bytes, header, attested, synthetic, gps=None):
    if size_bytes > 15 * 1024 * 1024 or size_bytes <= 0:
        raise ControlledError('SIZE_LIMIT', 'File exceeds 15 MiB or is empty')
    ext = Path(filename).suffix.lower()
    allowed = {'.jpg': ('image/jpeg', b'\xff\xd8\xff'), '.jpeg': ('image/jpeg', b'\xff\xd8\xff'), '.png': ('image/png', b'\x89PNG\r\n\x1a\n')}
    if ext not in allowed:
        raise ControlledError('TYPE_BLOCKED', 'Unsupported extension')
    mt, signature = allowed[ext]
    if media_type != mt or not header.startswith(signature):
        raise ControlledError('MIME_SIGNATURE_MISMATCH', 'Header does not match declared image')
    if synthetic is True:
        raise ControlledError('UNVERIFIED_IMAGE', 'Synthetic image cannot become field evidence')
    if not attested:
        raise ControlledError('ATTESTATION_REQUIRED', 'Field origin not confirmed')
    if gps is not None:
        valid_gps(gps)
    return 'QUARANTINE_PENDING_SECONDARY_VALIDATION'

def valid_gps(coords):
    try:
        lat, lon = float(coords['lat']), float(coords['lon'])
    except (ValueError, KeyError, TypeError):
        raise ControlledError('GEO_INVALID', 'Missing or invalid coordinates')
    if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180):
        raise ControlledError('GEO_INVALID', 'Coordinates must be finite and in WGS84 bounds')
    return lat, lon

def validate_case(case):
    required = {'case_id', 'country', 'location', 'photo_state', 'evidence_state', 'design_state', 'source_ids'}
    if not isinstance(case, dict) or required - set(case):
        raise ControlledError('SCHEMA_MISSING', f'Missing fields {sorted(required-set(case)) if isinstance(case,dict) else "not an object"}')
    lat, lon = valid_gps(case['location'])
    if case['country'] not in ('Indonesia', 'Philippines'):
        raise ControlledError('PROFILE_NOT_ADMITTED', 'Only two pilot profiles admitted in demo')
    if case['country'] == 'Indonesia' and not (-11 <= lat <= 6.5 and 94 <= lon <= 141.1):
        raise ControlledError('JURISDICTION_MISMATCH', 'Coordinates incompatible with declared pilot country')
    if case['country'] == 'Philippines' and not (4 <= lat <= 22 and 116 <= lon <= 127):
        raise ControlledError('JURISDICTION_MISMATCH', 'Coordinates incompatible with declared pilot country')
    if case['photo_state'] != 'VERIFIED_FIELD_EVIDENCE':
        return 'HOLD_FOR_EVIDENCE'
    if case['evidence_state'] != 'CURRENT_CONFIRMED':
        return 'HOLD_FOR_EVIDENCE'
    return 'HUMAN_REVIEW'

def citation_guard(source_id, source_registry):
    src = source_registry.get(source_id)
    if not src or src.get('status') != 'CURRENT_CONFIRMED' or not src.get('supports_claim'):
        raise ControlledError('CITATION_UNVERIFIED', 'Source missing, unconfirmed or not claim-supporting')
    return True

def material_choice(items, need):
    compliant = [x for x in items if x.get('certified') is True and x.get('suitable') is True and x.get('quantity', 0) >= need and x.get('unit_price', 0) > 0]
    if not compliant:
        raise ControlledError('NO_COMPLIANT_MATERIAL', 'No verified technical option; never relax safety for cost')
    return sorted(compliant, key=lambda x: (x['unit_price'], x['supplier_id']))[0]

def takeoff(unit_qty, unit_price, budget):
    for x in (unit_qty, unit_price, budget):
        if not isinstance(x, (int, float)) or not math.isfinite(x) or x < 0:
            raise ControlledError('NUMERIC_INVALID', 'Negative or nonfinite cost/quantity')
    total = round(unit_qty * unit_price, 2)
    if total > budget:
        raise ControlledError('BUDGET_INFEASIBLE', 'Cannot commit expenditure beyond approved amount')
    return total

def pep(action, actor, case, approvals=None):
    """External action gate - authority is never inferred from natural-language text."""
    approvals = approvals or {}
    role = actor.get('role', 'anonymous')
    if action in FORBIDDEN:
        return ('DENY', 'HARD_DENY')
    if action == 'read_evidence':
        return ('ALLOW', 'SCOPED_READ') if role in {'designer','reviewer','inspector','authority','auditor','orchestrator'} else ('DENY','ROLE')
    if action == 'draft_concept':
        return ('ALLOW', 'SANDBOX_ONLY') if role in {'designer','orchestrator'} else ('DENY','ROLE')
    if action == 'export_concept_stl':
        return ('ALLOW','CONCEPT_LABEL_ONLY') if role == 'designer' and case.get('design_state') == 'CONCEPT' else ('DENY','CONCEPT_ONLY')
    if action in {'release_design','print_production','send_external','approve_procurement'}:
        target_role = 'finance' if action == 'approve_procurement' else 'authority'
        if role != target_role:
            return ('DENY','ROLE')
        if case.get('origin') == 'SYNTHETIC_FIXTURE':
            return ('DENY','SYNTHETIC_DATA_BLOCK')
        if case.get('evidence_state') != 'CURRENT_CONFIRMED' or case.get('photo_state') != 'VERIFIED_FIELD_EVIDENCE':
            return ('DENY','EVIDENCE_HOLD')
        if not approvals.get('engineer_signed') or not approvals.get('reviewer_signed'):
            return ('DENY','TWO_REVIEWS_REQUIRED')
        if approvals.get('engineer_id') == approvals.get('reviewer_id') or not approvals.get('engineer_id') or not approvals.get('reviewer_id'):
            return ('DENY','INDEPENDENCE_REQUIRED')
        if action in {'print_production','approve_procurement'} and not approvals.get('authority_signed'):
            return ('DENY','AUTHORITY_REQUIRED')
        if action == 'approve_procurement' and not approvals.get('supplier_certified'):
            return ('DENY','SUPPLIER_VERIFICATION_REQUIRED')
        return ('ALLOW','HUMAN_SIGNOFF_VERIFIED')
    return ('DENY','UNKNOWN_ACTION')

def vulnerable_pep(action, actor, case, approvals=None):
    """Deliberately defective historical-style fixture for controlled red-team reproduction."""
    if action == 'audit_delete' and actor.get('role') == 'admin':
        return ('ALLOW','BAD_ADMIN_RULE')
    return pep(action, actor, case, approvals)

def csv_safe(value):
    txt = str(value)
    return "'" + txt if txt.startswith(('=', '+', '-', '@', '\t', '\r')) else txt

def make_audit_events(events):
    prev = '0'*64; out=[]
    for i,event in enumerate(events):
        obj = {'seq':i+1,'previous_hash':prev, 'event':event, 'policy_version':POLICY_VERSION}
        obj['hash'] = digest(obj)
        prev = obj['hash']; out.append(obj)
    return out

def verify_audit(events):
    previous = '0'*64
    for n, rec in enumerate(events):
        if rec.get('seq') != n+1 or rec.get('previous_hash') != previous:
            return False
        body={k:v for k,v in rec.items() if k != 'hash'}
        if digest(body) != rec.get('hash'):
            return False
        previous=rec['hash']
    return True

def cube_triangles(x0,y0,z0,x1,y1,z1):
    a=(x0,y0,z0); b=(x1,y0,z0); c=(x1,y1,z0); d=(x0,y1,z0)
    e=(x0,y0,z1); f=(x1,y0,z1); g=(x1,y1,z1); h=(x0,y1,z1)
    return [(a,c,b),(a,d,c),(e,f,g),(e,g,h),(a,b,f),(a,f,e),(b,c,g),(b,g,f),(c,d,h),(c,h,g),(d,a,e),(d,e,h)]

def make_concept_stl(path):
    """Visual concept only: separate touching/intersecting shells, no engineering validation."""
    tris=[]
    # Dimensions represent generic tabletop scale and are NOT building dimensions.
    for x in (0.4, 5.0):
        for y in (0.4, 7.0):
            tris.extend(cube_triangles(x,y,0,x+0.5,y+0.5,3.0))
    tris.extend(cube_triangles(0,0,3,6,8,3.35))  # elevated deck
    tris.extend(cube_triangles(0.3,0.3,3.35,5.7,7.7,5.75)) # 3-room volume conceptual
    tris.extend(cube_triangles(-0.3,-0.3,5.75,6.3,8.3,6.0)) # roof diagram slab
    tris.extend(cube_triangles(1.9,0.3,3.35,2.0,7.7,5.75))
    tris.extend(cube_triangles(3.9,0.3,3.35,4.0,7.7,5.75))
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='ascii') as f:
        f.write('solid BRAWN_CONCEPT_ONLY_NOT_FOR_CONSTRUCTION\n')
        for triangle in tris:
            for vertex in triangle:
                assert all(math.isfinite(x) for x in vertex)
            f.write('facet normal 0 0 0\nouter loop\n')
            for v in triangle: f.write('vertex %g %g %g\n'%v)
            f.write('endloop\nendfacet\n')
        f.write('endsolid BRAWN_CONCEPT_ONLY_NOT_FOR_CONSTRUCTION\n')
    return {'facets':len(tris),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}

GOOD_CASE={'case_id':'IDN-ACEH-DEMO-001','country':'Indonesia','location':{'lat':5.54,'lon':95.32},'photo_state':'VERIFIED_FIELD_EVIDENCE','evidence_state':'CURRENT_CONFIRMED','design_state':'CONCEPT','source_ids':['IDN-PP16-2021'],'origin':'MOCK_VERIFIED_UNIT_TEST_ONLY'}
GOOD_APPROVALS={'engineer_signed':True,'reviewer_signed':True,'engineer_id':'ENG_A','reviewer_id':'REV_B','authority_signed':True,'supplier_certified':True}

def demo_pipeline(case, actor, approvals):
    result=validate_case(case)
    release=pep('release_design',actor,case,approvals)
    state='RELEASED_BY_AUTHORITY' if release[0]=='ALLOW' and result=='HUMAN_REVIEW' else ('HOLD_FOR_EVIDENCE' if result=='HOLD_FOR_EVIDENCE' else 'HUMAN_REVIEW')
    return {'case_id':case['case_id'], 'input_hash':digest(case), 'origin':'MOCK_VERIFIED_UNIT_TEST_ONLY', 'workflow_labels_not_executed_agents':['intake','image_provenance','geolocation','brain_handoff','constraints','concept','independent_review','pep','registry'], 'executed_agent_decision':{'agent_id':'B37','actor_role':actor.get('role'),'requested_action':'release_design','result':release[0],'reason':release[1]}, 'status':state,'policy_version':POLICY_VERSION,'design': 'CONCEPT_ONLY_NOT_ENGINEERING_CERTIFICATE','limitation':'No specialised LLM/engineer was dispatched; authority and evidence are mock fixtures.'}
