#!/usr/bin/env python3
"""
Generate mhm_parameter.nml from recommended_params.csv

This script:
1. Reads recommended_params.csv from DDS analysis
2. For GLOBAL parameters: Uses recommended_value (mean across catchments)
3. For CATCHMENT_SPECIFIC: Uses value from best-performing catchment
4. Generates a valid mhm_parameter.nml file
5. Copies to all 6 catchment run directories

Usage: python generate_recommended_param_nml.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
import shutil
from datetime import datetime

# Configuration
WORKSPACE = Path("/data/.openclaw/workspace/open_claw_vibe_coding")
CSV_PATH = WORKSPACE / "dashboard_saxony" / "utils" / "recommended_params.csv"
RUNS_DIR = WORKSPACE / "code" / "mhm_re_crit" / "runs"

CATCHMENTS = [
    "parthe_0p0625",
    "goeltzsch2_0p0625",
    "chemnitz2_0p0625",
    "wesenitz2_0p0625",
    "wyhra_0p0625",
    "zwoenitz1_0p0625"
]

# DDS parameter mapping (param_id -> name in mhm_parameter.nml)
PARAM_NAMES = {
    1: "param_01", 2: "param_02", 3: "param_03", 4: "param_04",
    5: "param_05", 6: "param_06", 7: "param_07", 8: "param_08",
    9: "param_09", 10: "param_10", 11: "param_11", 12: "param_12",
    13: "param_13", 14: "param_14", 15: "param_15", 16: "param_16",
    17: "param_17", 18: "param_18", 19: "param_19", 20: "param_20",
    21: "param_21", 22: "param_22", 23: "param_23", 24: "param_24",
    25: "param_25", 26: "param_26", 27: "param_27", 28: "param_28",
    29: "param_29", 30: "param_30", 31: "param_31", 32: "param_32",
    33: "param_33", 34: "param_34", 35: "param_35", 36: "param_36",
    37: "param_37", 38: "param_38", 39: "param_39", 40: "param_40",
    41: "param_41", 42: "param_42", 43: "param_43", 44: "param_44",
    45: "param_45", 46: "param_46", 47: "param_47", 48: "param_48",
    49: "param_49", 50: "param_50", 51: "param_51", 52: "param_52",
    53: "param_53", 54: "param_54",
}

def read_dds_results():
    """Read final parameters from all 6 DDS runs."""
    all_params = {}
    objectives = {}
    
    for ch in CATCHMENTS:
        dds_file = RUNS_DIR / ch / "dds_results.out"
        if dds_file.exists():
            with open(dds_file, 'r') as f:
                lines = [l for l in f.readlines() if not l.strip().startswith('#')]
            
            data = []
            for line in lines:
                parts = line.split()
                if len(parts) >= 56:
                    try:
                        iter_num = int(parts[0])
                        obj = float(parts[1])
                        params = [float(x) for x in parts[2:56]]
                        data.append({'iteration': iter_num, 'objective': obj, 'params': params})
                    except (ValueError, IndexError):
                        continue
            
            if len(data) > 0:
                final = data[-1]
                all_params[ch] = final['params']
                objectives[ch] = final['objective']
                print(f"✅ {ch}: {len(data)} iterations, obj = {final['objective']:.4f}")
    
    return all_params, objectives

def generate_recommended_params(csv_path, all_params, objectives):
    """
    Generate recommended parameter values.
    
    Strategy:
    - GLOBAL (CV < 0.1): Use recommended_value from CSV
    - GLOBAL_WITH_UNCERTAINTY (CV 0.1-0.3): Use recommended_value
    - CATCHMENT_SPECIFIC (CV > 0.3): Use value from best-performing catchment
    """
    if not csv_path.exists():
        print(f"❌ CSV not found: {csv_path}")
        return None
    
    df = pd.read_csv(csv_path)
    
    # Find best catchment (lowest objective)
    best_catchment = min(objectives, key=objectives.get)
    print(f"\n🏆 Best performing catchment: {best_catchment} (obj = {objectives[best_catchment]:.4f})")
    
    recommended = {}
    for _, row in df.iterrows():
        param_id = int(row['param_id'])
        param_name = PARAM_NAMES.get(param_id, f"param_{param_id:02d}")
        
        rec = row['recommendation']
        
        if pd.isna(row['recommended_value']) or rec == 'CATCHMENT_SPECIFIC':
            # Use value from best catchment
            value = all_params[best_catchment][param_id - 1]
            source = f"{best_catchment}"
        else:
            # Use recommended value (GLOBAL or GLOBAL_WITH_UNCERTAINTY)
            value = float(row['recommended_value'])
            source = "mean(6 catchments)"
        
        recommended[param_name] = {
            'value': value,
            'source': source,
            'cv': row['cv'],
            'recommendation': rec
        }
    
    return recommended

def read_template_nml():
    """Read template mhm_parameter.nml from first catchment."""
    template_path = RUNS_DIR / CATCHMENTS[0] / "nml" / "mhm_parameter.nml"
    if not template_path.exists():
        print(f"❌ Template not found: {template_path}")
        return None
    
    with open(template_path, 'r') as f:
        return f.read()

def generate_nml_file(recommended, template_content):
    """Replace parameter values in template."""
    lines = template_content.split('\n')
    new_lines = []
    
    replaced = 0
    for line in lines:
        stripped = line.strip()
        
        # Check if line contains parameter definition
        if stripped.startswith('param_') and '=' in stripped:
            parts = stripped.split('=')
            param_name = parts[0].strip()
            
            if param_name in recommended:
                value = recommended[param_name]['value']
                new_line = f"{param_name} = {value:.8f}"
                new_lines.append(new_line)
                replaced += 1
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    print(f"✅ Replaced {replaced} parameter values")
    return '\n'.join(new_lines)

def add_header(nml_content, recommended):
    """Add header comment with metadata."""
    header = f"""!******************************************************************************************
! GENERATED PARAMETER FILE - RECOMMENDED VALUES FROM DDS ANALYSIS
!******************************************************************************************
! Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
! Source: recommended_params.csv (6 catchments DDS analysis)
!
! Strategy:
!   - GLOBAL parameters (CV < 0.1): Mean across all 6 catchments
!   - GLOBAL_WITH_UNCERTAINTY (CV 0.1-0.3): Mean with uncertainty
!   - CATCHMENT_SPECIFIC (CV > 0.3): Value from best-performing catchment
!
! Statistics:
!   - GLOBAL: {sum(1 for v in recommended.values() if v['recommendation']=='GLOBAL')} parameters
!   - GLOBAL_WITH_UNCERTAINTY: {sum(1 for v in recommended.values() if v['recommendation']=='GLOBAL_WITH_UNCERTAINTY')} parameters
!   - CATCHMENT_SPECIFIC: {sum(1 for v in recommended.values() if v['recommendation']=='CATCHMENT_SPECIFIC')} parameters
!
! Best catchment (for CATCHMENT_SPECIFIC): Lowest objective function value
!******************************************************************************************

"""
    return header + nml_content

def main():
    print("="*80)
    print("🔧 Generate mhm_parameter.nml from recommended_params.csv")
    print("="*80)
    print()
    
    # Step 1: Read CSV
    print("📊 Step 1: Reading recommended_params.csv...")
    if not CSV_PATH.exists():
        print(f"❌ Error: {CSV_PATH} not found")
        print("   Run DDS analysis first or check path.")
        return 1
    print(f"✅ Found: {CSV_PATH}")
    print()
    
    # Step 2: Read DDS results from all catchments
    print("📊 Step 2: Reading DDS results from all catchments...")
    all_params, objectives = read_dds_results()
    
    if not all_params:
        print("❌ No DDS results found!")
        return 1
    print()
    
    # Step 3: Generate recommended parameters
    print("📊 Step 3: Generating recommended parameter values...")
    recommended = generate_recommended_params(CSV_PATH, all_params, objectives)
    
    if not recommended:
        print("❌ Failed to generate recommendations")
        return 1
    print()
    
    # Step 4: Read template
    print("📊 Step 4: Reading template mhm_parameter.nml...")
    template = read_template_nml()
    if not template:
        return 1
    print()
    
    # Step 5: Generate NML content
    print("📊 Step 5: Generating mhm_parameter.nml content...")
    nml_content = generate_nml_file(recommended, template)
    nml_content = add_header(nml_content, recommended)
    print()
    
    # Step 6: Write to all catchment directories
    print("📊 Step 6: Writing to all catchment directories...")
    
    output_files = []
    for ch in CATCHMENTS:
        output_dir = RUNS_DIR / ch / "nml"
        output_file = output_dir / "mhm_parameter.nml"
        
        # Backup existing file
        if output_file.exists():
            backup_file = output_dir / f"mhm_parameter.nml.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy(output_file, backup_file)
            print(f"   💾 Backed up: {backup_file.name}")
        
        # Write new file
        with open(output_file, 'w') as f:
            f.write(nml_content)
        
        output_files.append(str(output_file))
        print(f"   ✅ {ch}/nml/mhm_parameter.nml")
    
    print()
    print("="*80)
    print("✅ SUCCESS!")
    print("="*80)
    print()
    print(f"Generated mhm_parameter.nml for {len(CATCHMENTS)} catchments:")
    for f in output_files:
        print(f"  - {f}")
    print()
    print("📋 Next steps:")
    print("  1. Verify time period in mhm.nml (should be 1991-2020)")
    print("  2. Run: bash ops/bin/run_all_6_catchments_1991_2020.sh")
    print()
    
    return 0

if __name__ == "__main__":
    exit(main())
