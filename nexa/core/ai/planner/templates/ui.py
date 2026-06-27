from .base import BaseTemplate

class UITemplate(BaseTemplate):
    def generate(self, goal, context):
        framework = context.get('framework', 'unknown').lower()
        important_files = context.get('important_files', [])
        component_name = goal.title().replace('Add ', '').replace('Create ', '').replace(' ', '')
        
        goal_words = set(goal.lower().split())
        steps = []
        
        # Heuristic: Find important files that might be related to the goal
        related_files = []
        for file_path in important_files:
            file_name_lower = file_path.lower()
            if any(word in file_name_lower for word in goal_words if len(word) > 3):
                related_files.append(file_path.split('/')[-1].split('\\')[-1])
                
        if related_files:
            for file in related_files:
                if '.vue' in file or '.jsx' in file or '.tsx' in file or '.html' in file or '.blade.php' in file or '.tpl' in file:
                    steps.append({"title": f"Update Layout {file}", "description": "Place the new UI component inside this layout file."})
                elif 'Store' in file or 'Context' in file or 'Provider' in file:
                    steps.append({"title": f"Update State in {file}", "description": "Manage the state for the new UI component here."})
                elif 'Style' in file or 'Theme' in file or 'css' in file:
                    steps.append({"title": f"Update Styling in {file}", "description": "Add CSS classes or tokens for the new component."})
        
        if framework in ['reactjs', 'nextjs', 'vuejs', 'nuxtjs', 'react_native']:
            ext = ".vue" if "vue" in framework else ".jsx"
            steps = [
                {"title": f"Create {component_name}{ext}", "description": "Create the new UI component file."},
                {"title": "Integrate with Layout", "description": "Place the component in the main layout or specific page."},
                {"title": "Add Interaction Elements", "description": "Add sub-components like switchers, buttons, or links."},
                {"title": "Update State/Store", "description": "Update relevant context, Vuex, or Redux store if interaction is needed."}
            ]
        elif framework == 'flutter':
            steps = [
                {"title": f"Create {component_name}Widget", "description": "Create the stateless or stateful widget."},
                {"title": "Integrate with Screen", "description": "Add widget to the target screen."},
                {"title": "Bind Controller", "description": "Connect UI interactions to state controller."}
            ]
        elif framework in ['nexaphp', 'laravel', 'django', 'fastapi']:
            steps = [
                {"title": "Create Template View", "description": "Create HTML/Blade/Twig/Django template file."},
                {"title": "Update Base Layout", "description": "Include the new UI element in the base layout."},
                {"title": "Pass Data from Controller", "description": "Ensure backend route passes necessary data to the view."}
            ]
        else:
            steps = [
                {"title": "Create UI Element", "description": "Write HTML and CSS for the new element."},
                {"title": "Add Interactivity", "description": "Write vanilla JS to handle events."}
            ]
            
        return self.response(goal, "low", "low", steps)
