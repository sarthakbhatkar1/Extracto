import asyncio
import platform
from nicegui import ui
import requests
import json
from datetime import datetime
from typing import Optional, Dict, Any
import mimetypes  

API_BASE_URL = "http://localhost:7777"
session = {
    'logged_in': False,
    'user_id': None,
    'username': None,
    'role': None,
    'token': None,
    'user_data': None
}


class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    async def upload_document(self, multipart_data: Dict, files) -> Dict:
        return await self._make_request('POST', '/api/v1/document', data=multipart_data, files=files)

    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, files: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
        url = f"{self.base_url}{endpoint}"
        default_headers = self.session.headers.copy()
        if headers:
            default_headers.update(headers)
        try:
            loop = asyncio.get_event_loop()
            if method.upper() == 'GET':
                response = await loop.run_in_executor(None, lambda: self.session.get(url, headers=default_headers, params=data))
            elif method.upper() == 'POST':
                if files is not None:
                    response = await loop.run_in_executor(None, lambda: self.session.post(url, data=data or {}, files=files, headers=default_headers))
                else:
                    response = await loop.run_in_executor(None, lambda: self.session.post(url, data=data, headers=default_headers))
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            result = response.json() if response.text else {"status": "success"}
            print(f"API Response ({url}): {result}")
            return result
        except requests.exceptions.RequestException as e:
            error_msg = {"error": str(e), "status": "failed", "detail": getattr(e.response, 'text', str(e))}
            print(f"API Error ({url}): {error_msg}")
            return error_msg

    async def login(self, username: str, password: str) -> Dict:
        form_data = {'grant_type': 'password', 'username': username, 'password': password, 'scope': '', 'client_id': '',
                     'client_secret': ''}
        headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
        return await self._make_request('POST', '/api/v1/auth/login', data=form_data, headers=headers)

    async def logout(self) -> Dict:
        return await self._make_request('POST', '/api/v1/auth/logout')

    async def create_project(self, project_data: Dict) -> Dict:
        return await self._make_request('POST', '/api/v1/project', data=project_data)

    async def get_projects(self) -> Dict:
        return await self._make_request('GET', '/api/v1/project')

    async def get_documents(self) -> Dict:
        return await self._make_request('GET', '/api/v1/document')


api_client = APIClient(API_BASE_URL)


async def logout():
    try:
        await api_client.logout()
    except:
        pass
    session.update(
        {'logged_in': False, 'user_id': None, 'username': None, 'role': None, 'token': None, 'user_data': None})
    ui.navigate.to('/')


def show_notification(message: str, type: str = 'info'):
    color_map = {'success': 'positive', 'error': 'negative', 'warning': 'warning', 'info': 'info'}
    ui.notify(message, color=color_map.get(type, 'info'))


def layout_wrapper(title: str):
    with ui.header(elevated=True).classes('justify-between bg-blue-600'):
        ui.label('Extracto Dashboard').classes('text-lg ml-4 text-white font-bold')
        with ui.row().classes('mr-4'):
            ui.label(f"Welcome, {session['username']}").classes('text-white mr-4')
            ui.button('Logout', on_click=logout).classes('bg-red-500 text-white')
    with ui.left_drawer(top_corner=True, bottom_corner=True).classes('bg-gray-100 w-64'):
        ui.link('🏠 Dashboard', '/welcome').classes('text-blue-600 font-medium p-2')
        if session['role'] == 'admin':
            ui.link('👤 Users', '/users').classes('text-blue-600 font-medium p-2')
        ui.link('📁 Projects', '/projects').classes('text-blue-600 font-medium p-2')
        ui.link('📄 Documents', '/documents').classes('text-blue-600 font-medium p-2')
    return ui.column().classes('p-8')


async def login_page():
    with ui.card().classes('absolute-center w-96 shadow-lg'):
        with ui.column().classes('p-8'):
            ui.label('Login to Extracto').classes('text-2xl mb-6 text-center font-bold')
            username_input = ui.input('Username').classes('mb-4 w-full')
            password_input = ui.input('Password', password=True, password_toggle_button=True).classes('mb-6 w-full')
            loading_spinner = ui.spinner('dots', size='lg', color='blue').classes('hidden')
            status_label = ui.label().classes('text-sm text-red-600 mt-2').style('display: none')

            async def try_login():
                if not username_input.value or not password_input.value:
                    show_notification('Please enter both username and password', 'error')
                    return
                loading_spinner.classes('block')
                status_label.style('display: block').set_text('Attempting login...')
                response = await api_client.login(username_input.value, password_input.value)
                loading_spinner.classes('hidden')
                status_label.style('display: none')
                print(f"Login response: {response}")
                if response.get('access_token') or response.get('status') == 'success':
                    user_data = response.get('user', {}) or {'id': None, 'username': username_input.value,
                                                             'role': 'user'}
                    session.update({
                        'logged_in': True,
                        'user_id': user_data.get('id'),
                        'username': user_data.get('username', username_input.value),
                        'role': user_data.get('role', 'user'),
                        'token': response.get('access_token'),
                        'user_data': user_data
                    })
                    if session['token']:
                        api_client.session.headers.update({'Authorization': f"Bearer {session['token']}"})
                    show_notification('Login successful!', 'success')
                    ui.navigate.to('/welcome')
                else:
                    error_msg = response.get('error', 'Invalid credentials or server issue')
                    show_notification(f"Login failed: {error_msg}", 'error')
                    status_label.set_text(f"Error: {error_msg}")

            username_input.on('keydown.enter', try_login)
            password_input.on('keydown.enter', try_login)
            ui.button('Login', on_click=try_login).classes('w-full bg-blue-600 text-white py-2')
            with ui.expansion('Demo Credentials', icon='info').classes('w-full mt-4'):
                ui.label('Try these test credentials:').classes('font-semibold')
                ui.label('Username: test@example.com').classes('text-sm text-gray-600')
                ui.label('Password: testpassword').classes('text-sm text-gray-600 mb-2')
                ui.label('Or check your API documentation for valid credentials.').classes('text-sm text-gray-500')


async def welcome_page():
    with ui.column().classes('w-full'):
        ui.label(f"Welcome back, {session['username']}!").classes('text-3xl mb-4 font-bold')
        ui.label(f"Role: {session['role'].title()}").classes('text-lg mb-8 text-gray-600')
        if session['user_data']:
            with ui.card().classes('w-full mb-8 p-6'):
                ui.label('User Information').classes('text-xl font-semibold mb-4')
                with ui.grid(columns=2).classes('gap-4'):
                    ui.label(f"ID: {session['user_data'].get('id', 'N/A')}").classes('text-sm')
                    ui.label(f"Name: {session['user_data'].get('name', 'N/A')}").classes('text-sm')
                    ui.label(f"Surname: {session['user_data'].get('surname', 'N/A')}").classes('text-sm')
                    ui.label(f"Role: {session['user_data'].get('role', 'N/A')}").classes('text-sm')
                    if session['user_data'].get('created_at'):
                        ui.label(f"Member since: {session['user_data']['created_at'][:10]}").classes('text-sm')
        stats_container = ui.row().classes('w-full gap-4 mb-8')

        async def load_dashboard_stats():
            projects, documents = await asyncio.gather(api_client.get_projects(), api_client.get_documents())
            projects_count = len(projects.get('result', []))
            documents_count = sum(
                len(folder.get('documents', [])) for project in documents.get('result', []) for folder in
                project.get('folders', []))
            with stats_container:
                with ui.card().classes('flex-1 p-6 bg-blue-50'):
                    ui.label('Projects').classes('text-lg font-semibold text-blue-800')
                    ui.label(str(projects_count)).classes('text-3xl font-bold text-blue-600')
                with ui.card().classes('flex-1 p-6 bg-orange-50'):
                    ui.label('Documents').classes('text-lg font-semibold text-orange-800')
                    ui.label(str(documents_count)).classes('text-3xl font-bold text-orange-600')

        await load_dashboard_stats()
        with ui.card().classes('w-full p-6'):
            ui.label('Quick Actions').classes('text-xl font-semibold mb-4')
            with ui.row().classes('gap-4'):
                ui.button('View Projects', icon='folder', on_click=lambda: ui.navigate.to('/projects')).classes(
                    'bg-blue-600 text-white')
                ui.button('View Documents', icon='description', on_click=lambda: ui.navigate.to('/documents')).classes(
                    'bg-purple-600 text-white')


async def projects_page():
    ui.label('Project Management').classes('text-2xl mb-6 font-bold')
    projects_container = ui.column().classes('w-full')

    async def load_projects():
        projects_container.clear()
        with ui.row().classes('w-full mb-4') as loading_row:
            ui.spinner('dots', size='lg', color='blue')
            ui.label('Loading projects...').classes('ml-2')
        response = await api_client.get_projects()
        loading_row.clear() 
        if response.get('success'):
            projects = response.get('result', [])
            with projects_container:
                if not projects:
                    ui.label('No projects found').classes('text-gray-600 text-center py-8')
                else:
                    with ui.grid(columns=1).classes('gap-4'):
                        for project in projects:
                            with ui.card().classes('w-full p-6 hover:shadow-lg transition-shadow'):
                                with ui.row().classes('w-full justify-between items-center mb-4'):
                                    ui.label(project.get('projectName', 'Unnamed Project')).classes(
                                        'text-xl font-bold text-blue-800')
                                    ui.button('View Details',
                                              on_click=lambda p=project: show_project_details(p)).classes(
                                        'bg-blue-600 text-white')
                                with ui.column().classes('gap-2'):
                                    ui.label(f"ID: {project.get('projectId', 'N/A')}").classes('text-sm text-gray-600')
                                    ui.label(f"Description: {project.get('description', 'No description')}").classes(
                                        'text-sm')
                                    if project.get('tags'):
                                        with ui.row().classes('gap-1 mt-2'):
                                            ui.label('Tags:').classes('text-sm text-gray-600')
                                            for tag in project.get('tags', []):
                                                ui.badge(tag).classes('bg-blue-100 text-blue-800')
                                    created_date = project.get('createdTs', '')[:10] if project.get(
                                        'createdTs') else 'N/A'
                                    ui.label(f"Created: {created_date}").classes('text-xs text-gray-500 mt-2')
        else:
            with projects_container:
                ui.label('Failed to load projects').classes('text-red-600 text-center py-8')

    async def create_project_dialog():
        with ui.dialog() as dialog, ui.card():
            with ui.column().classes('p-4'):
                name = ui.input('Project Name').classes('mb-4')
                desc = ui.input('Description').classes('mb-4')

                async def submit():
                    if name.value and desc.value:
                        response = await api_client.create_project(
                            {'projectName': name.value, 'description': desc.value})
                        if response.get('success'):
                            show_notification('Project created successfully!', 'success')
                            dialog.close()
                            await load_projects()
                        else:
                            show_notification(f'Failed to create project: {response.get("error")}', 'error')

                ui.button('Create', on_click=submit).classes('bg-green-600 text-white')
            ui.button('Cancel', on_click=dialog.close).classes('bg-gray-600 text-white mt-2')
        dialog.open()

    with ui.row().classes('gap-4 mb-6'):
        ui.button('Refresh Projects', icon='refresh', on_click=load_projects).classes('bg-blue-600 text-white')
        ui.button('Create Project', icon='add', on_click=create_project_dialog).classes('bg-green-600 text-white')
    await load_projects()

    async def show_project_details(project):
        with ui.column().classes('w-full h-full'):
            with ui.row().classes('w-full h-[calc(100vh-100px)]'):
                with ui.column().classes('w-1/2 bg-gray-100 p-4 overflow-y-auto'):
                    ui.label('Documents').classes('text-xl font-bold mb-4')
                    docs_response = await api_client.get_documents()
                    if docs_response.get('success'):
                        all_docs = docs_response.get('result', [])
                        project_docs = [doc for p in all_docs if p.get('projectId') == project.get('projectId') for
                                        folder in p.get('folders', []) for doc in folder.get('documents', [])]
                        if project_docs:
                            with ui.grid(columns=1).classes('gap-2'):
                                for doc in project_docs:
                                    with ui.card().classes('p-4 hover:shadow-md transition-shadow'):
                                        ui.label(doc.get('documentName', 'Unnamed Document')).classes(
                                            'font-semibold text-blue-800')
                                        ui.label(f"ID: {doc.get('documentId', 'N/A')}").classes('text-xs text-gray-600')
                        else:
                            ui.label('No documents available for this project').classes(
                                'text-gray-600 text-center py-4')
                    else:
                        ui.label('Failed to load documents').classes('text-red-600 text-center py-4')
                with ui.column().classes('w-1/2 bg-white p-6'):
                    ui.label(f"Project: {project.get('projectName', 'Unnamed')}").classes('text-2xl font-bold mb-4')
                    with ui.column().classes('gap-2'):
                        ui.label(f"ID: {project.get('projectId', 'N/A')}").classes('text-lg')
                        ui.label(f"Description: {project.get('description', 'No description')}").classes('text-lg')
                        if project.get('tags'):
                            with ui.row().classes('gap-1 mt-2'):
                                ui.label('Tags:').classes('text-md font-semibold')
                                for tag in project.get('tags', []):
                                    ui.badge(tag).classes('bg-blue-100 text-blue-800')
                        ui.label(f"Created: {project.get('createdTs', 'N/A')}").classes('text-md text-gray-600 mt-4')
                    ui.button('Return', on_click=lambda: ui.navigate.to('/projects')).classes(
                        'mt-6 bg-gray-600 text-white')


async def documents_page():
    ui.label('Document Management').classes('text-2xl mb-6 font-bold')
    documents_container = ui.column().classes('w-full')

    async def load_documents():
        documents_container.clear()
        with ui.row().classes('w-full mb-4') as loading_row:
            ui.spinner('dots', size='lg', color='purple')
            ui.label('Loading documents...').classes('ml-2')
        response = await api_client.get_documents()
        loading_row.clear() 
        if response.get('success'):
            projects_with_docs = response.get('result', [])
            with documents_container:
                if not projects_with_docs:
                    ui.label('No documents found').classes('text-gray-600 text-center py-8')
                else:
                    for project in projects_with_docs:
                        project_name = project.get('projectName', 'Unnamed Project')
                        project_id = project.get('projectId', '')
                        with ui.expansion(f"📁 {project_name}", icon='folder').classes('w-full mb-4'):
                            ui.label(f"Project ID: {project_id}").classes('text-xs text-gray-600 mb-4')
                            for folder in project.get('folders', []):
                                folder_name = folder.get('folderName', 'Unnamed Folder')
                                documents = folder.get('documents', [])
                                with ui.expansion(f"📂 {folder_name} ({len(documents)} docs)",
                                                  icon='folder_open').classes('ml-4 mb-2'):
                                    if documents:
                                        with ui.grid(columns=1).classes('gap-2 mt-2'):
                                            for doc in documents:
                                                with ui.card().classes('p-4 hover:shadow-md transition-shadow'):
                                                    with ui.row().classes('w-full justify-between items-center'):
                                                        with ui.column().classes('flex-1'):
                                                            ui.label(
                                                                doc.get('documentName', 'Unnamed Document')).classes(
                                                                'font-semibold text-blue-800')
                                                            ui.label(f"ID: {doc.get('documentId', 'N/A')}").classes(
                                                                'text-xs text-gray-600')
                                                            created_date = doc.get('createdTs', '')[:16] if doc.get(
                                                                'createdTs') else 'N/A'
                                                            ui.label(f"Created: {created_date}").classes(
                                                                'text-xs text-gray-500')
                                                        with ui.column().classes('gap-1'):
                                                            ui.button('View',
                                                                      on_click=lambda d=doc: show_document_details(
                                                                          d)).classes('bg-blue-600 text-white')
                                                            ui.button('Download',
                                                                      on_click=lambda d=doc: download_document(
                                                                          d)).classes('bg-green-600 text-white')
                                    else:
                                        ui.label('No documents in this folder').classes('text-gray-500 text-sm ml-4')
        else:
            with documents_container:
                ui.label('Failed to load documents').classes('text-red-600 text-center py-8')

    async def upload_document_dialog():
        projects_response = await api_client.get_projects()
        projects = projects_response.get('result', []) if projects_response.get('success') else []
        if not projects:
            show_notification('No projects available. Please create a project first.', 'warning')
            ui.navigate.to('/projects')
            return

        project_options = {p.get('projectName'): p.get('projectId') for p in projects if p.get('projectName')}
        print(f"project_options: {project_options}")

        uploaded_files = [] 
        file_list_container = ui.column().classes('mb-4') 

        with ui.dialog() as dialog, ui.card():
            with ui.column().classes('p-4'):
                default_value = list(project_options.keys())[0] if project_options else None
                project_select = ui.select(options=project_options, label='Select Project',
                                           value=default_value).classes('mb-4')
                folder_name = ui.input('Folder Name', placeholder='Enter folder name').classes('mb-4')

                def handle_upload(e):
                    e.content.seek(0) 
                    file_size = len(e.content.read())  
                    e.content.seek(0) 
                    print(f"on_upload called for {e.name} (type: {e.type}, size: {file_size})")
                    uploaded_files.append(e)
                    with file_list_container:
                        ui.label(f"Selected: {e.name} ({file_size} bytes, type: {e.type or 'unknown'})").classes(
                            'text-sm text-green-600')
                    show_notification(
                        f'File "{e.name}" selected successfully ({file_size} bytes). Click UPLOAD to send to server.',
                        'success')

                ui.upload(
                    on_upload=handle_upload,
                    auto_upload=True,
                    max_file_size=50 * 1024 * 1024
                ).classes('mb-4').props('accept=image/*,.pdf,.txt,.docx')  

                ui.label('Selected Files:').classes('font-medium mb-2')
                file_list_container 

                async def submit():
                    print("Submit button clicked")
                    if not uploaded_files:
                        show_notification('Please select a file first (progress should update on selection).',
                                          'warning')
                        return
                    if not project_select.value or not folder_name.value:
                        show_notification('Please select a project and enter a folder name.', 'warning')
                        return

                    e = uploaded_files[0]
                    e.content.seek(0)
                    project_id = project_options[project_select.value]

                    document_type = e.type
                    if not document_type:
                        guessed, _ = mimetypes.guess_type(e.name)
                        document_type = guessed or 'application/octet-stream'

                    multipart_data = {
                        'projectId': project_id,
                        'folderName': folder_name.value,
                        'documentType': document_type,
                        'documentName': e.name,
                    }

                    files = {
                        'document': (e.name, e.content, document_type)
                    }

                    print(f"Payload keys: {list(multipart_data.keys())}")  
                    print(f"Files keys: {list(files.keys())}") 

                    try:
                        print("Sending to API...")
                        response = await api_client.upload_document(multipart_data, files)
                        print(f"API Response: {response}")
                        if response.get('success', False):
                            show_notification('Document uploaded successfully!', 'success')
                            dialog.close()
                            uploaded_files.clear()
                            file_list_container.clear()
                            await load_documents()
                        else:
                            error_msg = response.get('error', 'Unknown API error')
                            show_notification(f'API upload failed: {error_msg}', 'error')
                    except Exception as ex:
                        print(f"Upload exception: {ex}")
                        show_notification(f'Upload error: {str(ex)}', 'error')


                ui.button('UPLOAD to Server', on_click=submit).classes('bg-green-600 text-white w-full')

            ui.button('Cancel', on_click=dialog.close).classes('bg-gray-600 text-white mt-2')
        dialog.open()





    with ui.row().classes('gap-4 mb-6'):
        ui.button('Refresh Documents', icon='refresh', on_click=load_documents).classes('bg-purple-600 text-white')
        ui.button('Upload Document', icon='upload', on_click=upload_document_dialog).classes('bg-green-600 text-white')
    await load_documents()

    async def show_document_details(document):
        with ui.dialog() as dialog, ui.card():
            ui.label(f"Document: {document.get('documentName', 'Unnamed')}").classes('text-xl font-bold mb-4')
            with ui.column().classes('gap-2 min-w-96'):
                ui.label(f"Document ID: {document.get('documentId', 'N/A')}").classes('text-sm')
                ui.label(f"Project ID: {document.get('projectId', 'N/A')}").classes('text-sm')
                ui.label(f"Folder: {document.get('folderName', 'N/A')}").classes('text-sm')
                ui.label(f"Created: {document.get('createdTs', 'N/A')}").classes('text-xs text-gray-600 mt-4')
            with ui.row().classes('gap-2 mt-4'):
                ui.button('Download', on_click=lambda: download_document(document)).classes('bg-green-600 text-white')
                ui.button('Close', on_click=dialog.close).classes('bg-gray-600 text-white')
        dialog.open()

    def download_document(document):
        doc_id = document.get('documentId')
        if doc_id:
            show_notification(f"Download started for {document.get('documentName', 'document')}", 'info')
            # TODO: Implement actual download


@ui.page('/')
async def main():
    if not session['logged_in']:
        await login_page()
    else:
        ui.navigate.to('/welcome')


@ui.page('/welcome')
async def welcome():
    if not session['logged_in']:
        ui.navigate.to('/')
        return
    with layout_wrapper('Dashboard'):
        await welcome_page()


@ui.page('/projects')
async def projects():
    if not session['logged_in']:
        ui.navigate.to('/')
        return
    with layout_wrapper('Project Management'):
        await projects_page()


@ui.page('/documents')
async def documents():
    if not session['logged_in']:
        ui.navigate.to('/')
        return
    with layout_wrapper('Document Management'):
        await documents_page()


async def on_startup():
    print(f"Starting Extracto Dashboard at {datetime.now()}")
    print(f"API Base URL: {API_BASE_URL}")


if platform.system() == "Emscripten":
    asyncio.ensure_future(on_startup())
else:
    if __name__ == "__main__":
        asyncio.run(on_startup())
        ui.run(port=8090, title="Extracto Dashboard", favicon="🚀", show=False, reload=False)
