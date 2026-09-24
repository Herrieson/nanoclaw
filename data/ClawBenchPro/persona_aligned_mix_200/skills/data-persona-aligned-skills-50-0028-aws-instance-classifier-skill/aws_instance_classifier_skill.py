import json

def aws_instance_classifier_skill(instance_type: str) -> str:
    # 模拟内部硬件数据库
    gpu_families = ['p2', 'p3', 'p4d', 'p5', 'g3', 'g4dn', 'g5', 'g5g', 'inf1', 'inf2', 'trn1']
    
    if not instance_type:
        return json.dumps({"error": "instance_type is required."})
        
    family = instance_type.split('.')[0] if '.' in instance_type else instance_type
    
    is_gpu = family.lower() in gpu_families
    
    desc = "GPU Accelerated Instance" if is_gpu else "General Purpose / Compute Optimized / Other Instance"
    
    result = {
        "instance_type": instance_type,
        "is_gpu": is_gpu,
        "hardware_description": desc
    }
    
    return json.dumps(result, indent=2)
