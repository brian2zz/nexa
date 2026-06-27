class Analyzer:
    def analyze_stats(self, project_framework, project_language, files_list):
        framework = project_framework.lower()
        
        summary = {
            "total_files": len(files_list),
            "pages": 0, "components": 0, "hooks": 0, "services": 0, "contexts": 0,
            "screens": 0, "widgets": 0, "controllers": 0, "models": 0, "views": 0,
            "serializers": 0, "repositories": 0, "modules": 0, "entities": 0,
            "jsx_files": 0
        }
        
        for f in files_list:
            path = f['path'].lower().replace("\\", "/")
            
            if path.endswith('.jsx') or path.endswith('.tsx'):
                summary['jsx_files'] += 1
            
            # JS/TS ecosystem counting
            if framework in ['reactjs', 'nextjs', 'vuejs', 'react_native', 'nuxtjs']:
                if '/pages/' in path or '/app/' in path: summary['pages'] += 1
                if '/components/' in path: summary['components'] += 1
                if '/hooks/' in path or path.startswith('use'): summary['hooks'] += 1
                if '/services/' in path: summary['services'] += 1
                if '/context/' in path: summary['contexts'] += 1
                
            # Flutter counting
            elif framework == 'flutter':
                if '/screens/' in path: summary['screens'] += 1
                if '/widgets/' in path: summary['widgets'] += 1
                if '/controllers/' in path: summary['controllers'] += 1
                if '/services/' in path: summary['services'] += 1
                
            # Django counting
            elif 'django' in framework:
                if 'models.py' in path: summary['models'] += 1
                if 'views.py' in path: summary['views'] += 1
                if 'serializers.py' in path: summary['serializers'] += 1
                if 'services.py' in path or '/services/' in path: summary['services'] += 1
                if 'repositories.py' in path or '/repositories/' in path: summary['repositories'] += 1
                
            # NexaPHP / Laravel counting
            elif framework in ['nexaphp', 'laravel']:
                if '/modules/' in path: summary['modules'] += 1
                if '/controllers/' in path: summary['controllers'] += 1
                if '/services/' in path: summary['services'] += 1
                if '/repositories/' in path: summary['repositories'] += 1
                if '/entities/' in path or '/models/' in path: summary['entities'] += 1
                
            # Generic
            else:
                if '/controllers/' in path: summary['controllers'] += 1
                if '/models/' in path: summary['models'] += 1
                if '/views/' in path: summary['views'] += 1
                if '/services/' in path: summary['services'] += 1
                
        # Clean up empty stats
        cleaned_summary = {k: v for k, v in summary.items() if v > 0 or k == 'total_files'}
        
        # Architecture detection
        architecture = []
        if summary.get('components', 0) > 0: architecture.append("Component Based")
        if summary.get('hooks', 0) > 0: architecture.append("Custom Hooks")
        if summary.get('contexts', 0) > 0: architecture.append("Context API")
        if summary.get('services', 0) > 0: architecture.append("Service Layer")
        if summary.get('repositories', 0) > 0: architecture.append("Repository Pattern")
        if framework in ['reactjs', 'vuejs', 'svelte']: architecture.append("SPA (Single Page Application)")
        
        return {
            "framework": framework,
            "language": project_language,
            "architecture": architecture,
            "statistics": cleaned_summary
        }
        
    def analyze_rules(self, files_list):
        warnings = []
        has_tests = False
        ignore_large_files = ["package-lock.json", "yarn.lock", "pnpm-lock.yaml", "composer.lock", "poetry.lock", "database.sqlite"]
        
        for f in files_list:
            path = f['path'].lower().replace("\\", "/")
            filename = path.split("/")[-1]
            size = f['size']
            
            if 'test' in path or 'spec.' in path:
                has_tests = True
                
            if size > 30000 and filename not in ignore_large_files:
                warnings.append({
                    "type": "warning",
                    "message": f"Large file detected (>30KB): {f['path']}"
                })
                
        if not has_tests:
            warnings.append({
                "type": "warning",
                "message": "Project has no tests"
            })
            
        risk_score = len(warnings) * 5
        health = "good"
        if risk_score >= 10: health = "warning"
        if risk_score >= 20: health = "critical"
            
        return {
            "warnings": warnings,
            "risk_score": risk_score,
            "project_health": health
        }
