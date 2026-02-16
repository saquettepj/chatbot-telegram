"""Script para exportar workflows do N8N e organizá-los por nome."""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

class C:
    G, R, Y, B, CY, NC = '\033[0;32m', '\033[0;31m', '\033[1;33m', '\033[0;34m', '\033[0;36m', '\033[0m'

def pc(text: str, color: str = C.NC, end: str = "\n"): print(f"{color}{text}{C.NC}", end=end)

def check_container(container: str = "n8n_editor") -> bool:
    try: return container in subprocess.run(["docker", "ps"], capture_output=True, text=True, check=True).stdout
    except: return False

def docker_exec(container: str, cmd: str) -> Tuple[bool, str, str]:
    try:
        r = subprocess.run(["docker", "exec", container, "sh", "-c", cmd], capture_output=True, text=True, encoding='utf-8', errors='replace', check=True)
        return True, r.stdout, r.stderr
    except subprocess.CalledProcessError as e:
        stdout = getattr(e, 'stdout', '') or ''
        stderr = getattr(e, 'stderr', '') or ''
        return False, stdout.decode('utf-8', errors='replace') if isinstance(stdout, bytes) else stdout, stderr.decode('utf-8', errors='replace') if isinstance(stderr, bytes) else stderr

def find_name_recursive(obj, depth=0, max_depth=3) -> Optional[str]:
    if depth > max_depth or not isinstance(obj, dict): return None
    for k, v in obj.items():
        if (k.lower() == "name" or k.lower().endswith("name")) and v:
            if isinstance(v, str) and v.strip(): return v.strip()
            if not isinstance(v, (dict, list)) and (s := str(v).strip()) and s not in ("null", "undefined"): return s
        if isinstance(v, dict) and (found := find_name_recursive(v, depth + 1, max_depth)): return found
        if isinstance(v, list):
            for item in v:
                if isinstance(item, dict) and (found := find_name_recursive(item, depth + 1, max_depth)): return found
    return None

def extract_name(data: Dict) -> str:
    paths = [("name",), ("settings", "name"), ("meta", "name"), ("workflow", "name"), ("info", "name"), ("data", "name"), ("workflowData", "name")]
    name = None
    for p in paths:
        if len(p) == 1: name = data.get(p[0])
        else: name = data.get(p[0], {}).get(p[1])
        if name: break
    name = name or find_name_recursive(data)
    name = name.strip() if isinstance(name, str) else (str(name).strip() if name else "")
    return "" if name in ("null", "undefined", "") else name

def sanitize(name: str) -> str:
    safe = re.sub(r'^[._-]+|[._-]+$', '', re.sub(r'[^a-zA-Z0-9._-]', '_', name))
    return safe if safe else 'unnamed'

def compare_dates(d1: str, d2: str) -> Optional[bool]:
    try:
        if not d1 or not d2: return None
        dt1, dt2 = datetime.fromisoformat(d1.replace('Z', '+00:00')), datetime.fromisoformat(d2.replace('Z', '+00:00'))
        return dt2 > dt1
    except: return None

def export_workflows():
    script_dir, project_dir = Path(__file__).parent.resolve(), Path(__file__).parent.resolve().parent
    workflows_dir, archived_dir = project_dir / "workflows", project_dir / "workflows" / "archived"
    
    pc("=== Exporting Workflows from N8N ===", C.B)
    if not check_container(): pc("Error: Container n8n_editor is not running", C.R); sys.exit(1)
    
    cmd = "cd /tmp && rm -rf workflows_export workflows_renamed workflows_archived && mkdir -p workflows_export workflows_renamed workflows_archived && n8n export:workflow --all --output=/tmp/workflows_export --backup > /dev/null 2>&1"
    if not docker_exec("n8n_editor", cmd)[0]: pc("Error exporting workflows from n8n", C.R); sys.exit(1)
    
    _, stdout, _ = docker_exec("n8n_editor", "ls /tmp/workflows_export/*.json 2>/dev/null || true")
    if not stdout.strip(): pc("No workflows found to export", C.Y); return
    
    success_count, no_name_errors, duplicate_errors, processed = 0, [], [], {}
    
    for wf_file in [f.strip() for f in stdout.strip().split('\n') if f.strip()]:
        temp_file = f"/tmp/workflow_temp_{os.path.basename(wf_file)}"
        docker_exec("n8n_editor", f"cp {wf_file} {temp_file}")
        
        success, json_content, _ = docker_exec("n8n_editor", f"cat {temp_file}")
        if not success or not json_content: success, json_content, _ = docker_exec("n8n_editor", f"cat {wf_file}")
        if not success or not json_content: continue
        
        try: workflow_data = json.loads(json_content.strip() or json_content)
        except: continue
        
        wf_id = workflow_data.get("id", os.path.basename(wf_file).replace(".json", ""))
        wf_name = extract_name(workflow_data)
        is_archived = workflow_data.get("isArchived", False)
        updated_at = workflow_data.get("updatedAt", "")
        
        if not wf_name: no_name_errors.append({"id": wf_id, "name": wf_name, "status": "arquivado" if is_archived else "ativo"}); continue
        
        safe_name = sanitize(wf_name)
        
        if safe_name in processed:
            ex = processed[safe_name]
            should_replace = (ex["is_archived"] and not is_archived) or (updated_at and ex["updated_at"] and compare_dates(ex["updated_at"], updated_at))
            
            if should_replace:
                duplicate_errors.append({"name": wf_name, "kept_id": wf_id, "ignored_id": ex["id"], "kept_status": "arquivado" if is_archived else "ativo", "ignored_status": "arquivado" if ex["is_archived"] else "ativo"})
                docker_exec("n8n_editor", f"rm -f /tmp/workflows_renamed/{safe_name}.json /tmp/workflows_archived/{safe_name}.json")
            else:
                duplicate_errors.append({"name": wf_name, "kept_id": ex["id"], "ignored_id": wf_id, "kept_status": "arquivado" if ex["is_archived"] else "ativo", "ignored_status": "arquivado" if is_archived else "ativo"})
                continue
        
        dest_dir = "/tmp/workflows_archived" if is_archived else "/tmp/workflows_renamed"
        docker_exec("n8n_editor", f"cp {wf_file} {dest_dir}/{safe_name}.json")
        processed[safe_name] = {"id": wf_id, "name": wf_name, "safe_name": safe_name, "is_archived": is_archived, "updated_at": updated_at}
        
        pc(f"[OK]", C.G, end=" ")
        print(f"{wf_name} -> {safe_name}.json{f' [{C.Y}archived{C.NC}]' if is_archived else ''}")
        success_count += 1
        docker_exec("n8n_editor", f"rm -f {temp_file}")
    
    workflows_dir.mkdir(parents=True, exist_ok=True)
    archived_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(["docker", "cp", "n8n_editor:/tmp/workflows_renamed/.", str(workflows_dir)], capture_output=True)
    subprocess.run(["docker", "cp", "n8n_editor:/tmp/workflows_archived/.", str(archived_dir)], capture_output=True)
    
    error_count = 0
    if no_name_errors or duplicate_errors:
        print(); pc("=== Export with errors ===", C.B)
        for e in no_name_errors:
            wf_id, wf_name, status = e["id"] or "(unknown)", e["name"], e["status"]
            if wf_name and wf_name not in ("undefined", "null", ""):
                print(f"Workflow: {C.Y}{wf_name}{C.NC} (ID: {C.Y}{wf_id}{C.NC})")
                pc("  Reason: Workflow name field is empty or invalid", C.R)
            else:
                print(f"Workflow ID: {C.Y}{wf_id}{C.NC}")
                pc("  Reason: Workflow without name field", C.R)
                pc("  Tip: Execute './scripts/debug-workflow-name.sh' para mais detalhes sobre este workflow", C.CY)
            print(f"  Status: [{C.Y}archived{C.NC}]" if status == "arquivado" else f"  Status: [{C.G}active{C.NC}]")
            print(); error_count += 1
        
        groups = {}
        for e in duplicate_errors:
            if e["name"] not in groups: groups[e["name"]] = {"kept_id": e["kept_id"], "kept_status": e["kept_status"], "ignored": []}
            groups[e["name"]]["ignored"].append({"id": e["ignored_id"], "status": e["ignored_status"]})
        
        for name, g in groups.items():
            print(f"Name: '{C.Y}{name}{C.NC}'")
            pc("  Reason: Multiple workflows with the same name", C.Y)
            kept_display = f"[{C.Y}archived{C.NC}]" if g["kept_status"] == "arquivado" else f"[{C.G}active{C.NC}]"
            pc("  Workflow kept:", C.G, end=" ")
            print(f"ID {g['kept_id']} {kept_display}")
            for ign in g["ignored"]:
                ign_display = f"[{C.Y}archived{C.NC}]" if ign["status"] == "arquivado" else f"[{C.G}active{C.NC}]"
                pc("  Workflow ignored:", C.R, end=" ")
                print(f"ID {ign['id']} {ign_display}")
            print(); error_count += 1
    
    pc("=== Summary ===", C.B)
    pc(f"Exported successfully: {success_count}", C.G)
    if error_count > 0: pc(f"Export with errors: {error_count}", C.R)

if __name__ == "__main__": export_workflows()
