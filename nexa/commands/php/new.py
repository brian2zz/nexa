import os
import shutil
import subprocess
import sys

def handle(args):
    if not args:
        print('Project name required')
        return

    # Extract args
    project_name = None
    frontend = None
    for arg in args:
        if arg.startswith('--frontend='):
            frontend = arg.split('=')[1].lower()
        elif not arg.startswith('--'):
            if not project_name:
                project_name = arg

    if not project_name:
        print('Project name required')
        return

    # Prompt if frontend not provided
    if not frontend:
        print("Pilih Frontend Framework untuk NexaPHP:")
        print("1) Vue.js")
        print("2) React.js")
        try:
            choice = input("Pilih (1/2): ").strip()
            if choice == '1':
                frontend = 'vue'
            elif choice == '2':
                frontend = 'react'
            else:
                print("Pilihan tidak valid, default ke Vue.js")
                frontend = 'vue'
        except KeyboardInterrupt:
            print("\nDibatalkan.")
            return

    if frontend not in ['vue', 'react']:
        print(f"Error: Frontend '{frontend}' not supported. Use 'vue' or 'react'.")
        return

    print(f'Creating NexaPHP project: {project_name} with {frontend.capitalize()}')

    project_path = os.path.join(os.getcwd(), project_name)

    if os.path.exists(project_path):
        print(f"Error: Directory '{project_name}' already exists.")
        return

    nexa_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    skeleton_path = os.path.join(nexa_root, 'templates', 'php_skeleton')

    if not os.path.exists(skeleton_path):
        print(f"Error: Skeleton template not found at {skeleton_path}")
        return

    try:
        shutil.copytree(skeleton_path, project_path)
        # Setup initial .env file
        env_example = os.path.join(project_path, '.env.example')
        env_file = os.path.join(project_path, '.env')
        if os.path.exists(env_example) and not os.path.exists(env_file):
            shutil.copy2(env_example, env_file)
    except Exception as e:
        print(f"Error copying skeleton: {e}")
        return

    # Scaffold frontend
    scaffold_frontend(project_path, frontend)

    print("Project scaffolded. Installing dependencies via Composer & NPM...")
    
    try:
        subprocess.run(['composer', 'install'], cwd=project_path, check=True)
        subprocess.run(['npm', 'install'], cwd=project_path, check=True, shell=(os.name == 'nt'))
    except FileNotFoundError:
        print("Warning: command not found. Please run 'composer install' and 'npm install' manually.")
    except subprocess.CalledProcessError:
        print("Warning: install failed. Please run manually.")

    print(f"\nNexaPHP project '{project_name}' created successfully!")
    
    print(f"Run 'cd {project_name}' and then 'nexa php run' to start the server.")

def scaffold_frontend(project_path, frontend):
    resources_dir = os.path.join(project_path, 'resources', 'js')
    public_dir = os.path.join(project_path, 'public')
    os.makedirs(resources_dir, exist_ok=True)
    
    script_dir = os.path.dirname(os.path.realpath(__file__))
    scaffold_dir = os.path.join(script_dir, '..', '..', 'templates', 'scaffold')
    
    # Generate router regardless of frontend (assuming user has router for React too, though tpl might be vue specific)
    with open(os.path.join(scaffold_dir, 'vite_router.tpl'), 'r', encoding='utf-8') as f:
        router_tpl = f.read()
    router_dir = os.path.join(resources_dir, 'router')
    os.makedirs(router_dir, exist_ok=True)
    with open(os.path.join(router_dir, 'index.js'), 'w', encoding='utf-8') as f:
        f.write(router_tpl.replace('// NEXA_ROUTE_IMPORTS', '').replace('// NEXA_ROUTES', ''))

    if frontend == 'vue':
        # package.json
        pkg = '''{
  "name": "nexaphp-vue",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build"
  },
  "dependencies": {
    "vue": "^3.5.0",
    "vue-router": "^4.2.0",
    "nprogress": "^0.2.0",
    "axios": "^1.0.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.4.0"
  }
}'''
        # vite.config.js
        vite = '''import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000',
      '/nexa-admin/api': 'http://127.0.0.1:8000'
    }
  }
})'''
        # index.html
        html = '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>NexaPHP x Vue</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="http://localhost:5173/@vite/client"></script>
    <script type="module" src="http://localhost:5173/resources/js/app.js"></script>
  </body>
</html>'''
        # app.js
        app_js = '''import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(router)
app.mount('#app')'''
        # App.vue
        app_vue = '''<template>
  <router-view></router-view>
</template>'''
        
        write_file(os.path.join(project_path, 'package.json'), pkg)
        write_file(os.path.join(project_path, 'vite.config.js'), vite)
        write_file(os.path.join(public_dir, 'index.html'), html)
        write_file(os.path.join(resources_dir, 'app.js'), app_js)
        write_file(os.path.join(resources_dir, 'App.vue'), app_vue)
        
        # Scaffold pages
        pages_dir = os.path.join(resources_dir, 'pages')
        os.makedirs(pages_dir, exist_ok=True)
        with open(os.path.join(scaffold_dir, 'vite_home.tpl'), 'r', encoding='utf-8') as f:
            home_tpl = f.read()
        write_file(os.path.join(pages_dir, 'Home.vue'), home_tpl)
        
        # Scaffold admin-nexa Dashboard
        admin_dir = os.path.join(resources_dir, 'admin-nexa', 'pages')
        components_dir = os.path.join(resources_dir, 'admin-nexa', 'components')
        os.makedirs(admin_dir, exist_ok=True)
        os.makedirs(components_dir, exist_ok=True)
        
        with open(os.path.join(scaffold_dir, 'vite_main_layout.tpl'), 'r', encoding='utf-8') as f:
            layout_tpl = f.read()
        write_file(os.path.join(components_dir, 'MainLayout.vue'), layout_tpl)
        
        with open(os.path.join(scaffold_dir, 'vite_admin_dashboard_php.tpl'), 'r', encoding='utf-8') as f:
            admin_tpl = f.read()
        write_file(os.path.join(admin_dir, 'Dashboard.vue'), admin_tpl.replace('<!-- ADMIN_MODULE_LINKS -->', ''))

    elif frontend == 'react':
        # package.json
        pkg = '''{
  "name": "nexaphp-react",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "axios": "^1.0.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.0",
    "vite": "^5.4.0"
  }
}'''
        # vite.config.js
        vite = '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
})'''
        # index.html
        html = '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>NexaPHP x React</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="http://localhost:5173/@vite/client"></script>
    <script type="module">
      import RefreshRuntime from 'http://localhost:5173/@react-refresh'
      RefreshRuntime.injectIntoGlobalHook(window)
      window.$RefreshReg$ = () => {}
      window.$RefreshSig$ = () => (type) => type
      window.__vite_plugin_react_preamble_installed__ = true
    </script>
    <script type="module" src="http://localhost:5173/resources/js/app.jsx"></script>
  </body>
</html>'''
        # app.jsx
        app_jsx = '''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)'''
        # App.jsx
        app_jsx_comp = '''export default function App() {
  return (
    <div style={{ fontFamily: 'sans-serif', textAlign: 'center', marginTop: '50px' }}>
      <h1>Welcome to NexaPHP x React ⚛️</h1>
      <p>Your modular ERP framework is ready.</p>
    </div>
  )
}'''
        
        write_file(os.path.join(project_path, 'package.json'), pkg)
        write_file(os.path.join(project_path, 'vite.config.js'), vite)
        write_file(os.path.join(public_dir, 'index.html'), html)
        write_file(os.path.join(resources_dir, 'app.jsx'), app_jsx)
        write_file(os.path.join(resources_dir, 'App.jsx'), app_jsx_comp)

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
