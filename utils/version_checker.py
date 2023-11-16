def compare_versions(version1, version2):

    v1 = [int(x) for x in version1.split('.')]
    v2 = [int(x) for x in version2.split('.')]
    
    # Compare each component
    for component1, component2 in zip(v1, v2):
        if component1 < component2:
            return -1
        elif component1 > component2:
            return 1
    
    if len(v1) < len(v2):
        return -1  
    elif len(v1) > len(v2):
        return 1   
    
    return 0 
