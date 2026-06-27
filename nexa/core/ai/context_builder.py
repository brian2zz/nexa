class ContextBuilder:
    def build(self, project_framework, files_list):
        important_files = []
        framework = project_framework.lower()
        
        for f in files_list:
            path = f['path'].replace("\\", "/")
            path_lower = path.lower()
            
            # React / Next / Vue Ecosystem
            if framework in ['react_native', 'nextjs', 'nuxtjs', 'vuejs', 'reactjs']:
                if ('src/app.' in path_lower or 'src/index.' in path_lower or 
                    '/services/' in path_lower or '/context/' in path_lower or 
                    '/components/' in path_lower or '/hooks/' in path_lower):
                    important_files.append(path)
                    
            # Flutter
            elif framework == 'flutter':
                if ('lib/main.dart' in path_lower or '/screens/' in path_lower or 
                    '/controllers/' in path_lower or '/widgets/' in path_lower or
                    '/services/' in path_lower):
                    important_files.append(path)
                    
            # Django
            elif 'django' in framework:
                if ('models.py' in path_lower or 'views.py' in path_lower or 
                    'urls.py' in path_lower or 'serializers.py' in path_lower or
                    'services.py' in path_lower):
                    important_files.append(path)
                    
            # PHP (NexaPHP / Laravel / CI3)
            elif framework in ['nexaphp', 'laravel', 'codeigniter3']:
                if ('routes/' in path_lower or 'controllers/' in path_lower or 
                    'modules/' in path_lower or 'models/' in path_lower or
                    'services/' in path_lower):
                    important_files.append(path)
                    
            # Generic fallback
            else:
                if ('main.' in path_lower or 'app.' in path_lower or 'index.' in path_lower or
                    'routes' in path_lower or 'controllers' in path_lower or 'models' in path_lower):
                    important_files.append(path)
                    
        return {
            "framework": framework,
            "important_files": important_files
        }
