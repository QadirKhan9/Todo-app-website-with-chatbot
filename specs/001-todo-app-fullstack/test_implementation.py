# Test that the project structure is correctly set up
import os
import sys

# Add backend/src to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'src'))

def test_project_structure():
    """Test that the basic project structure is in place"""
    required_dirs = [
        'backend',
        'backend/src',
        'backend/src/models',
        'backend/src/services',
        'backend/src/api',
        'backend/src/config',
        'frontend',
        'frontend/src',
        'frontend/src/app',
        'frontend/src/components',
        'frontend/src/lib',
        'frontend/src/types',
        'frontend/src/styles'
    ]
    
    for directory in required_dirs:
        assert os.path.isdir(directory), f"Directory {directory} does not exist"
    
    # Check for key files
    required_files = [
        'backend/requirements.txt',
        'backend/src/models/user.py',
        'backend/src/models/task.py',
        'backend/src/services/auth_service.py',
        'backend/src/services/task_service.py',
        'backend/src/api/auth.py',
        'backend/src/api/tasks.py',
        'backend/src/config/settings.py',
        'backend/src/main.py',
        'frontend/package.json',
        'frontend/src/app/page.tsx',
        'frontend/src/app/login/page.tsx',
        'frontend/src/app/register/page.tsx',
        'frontend/src/app/dashboard/page.tsx',
        'frontend/src/components/TaskItem.tsx',
        'frontend/src/components/TaskForm.tsx',
        'frontend/src/components/TaskList.tsx',
        'frontend/src/lib/auth.ts',
        'frontend/src/lib/api.ts',
        'frontend/src/types/task.ts'
    ]
    
    for file in required_files:
        assert os.path.isfile(file), f"File {file} does not exist"
    
    print("✅ All required directories and files exist")
    
def test_imports():
    """Test that we can import the key modules"""
    try:
        # Test backend modules
        from models.user import User
        from models.task import Task
        from services.auth_service import create_user, authenticate_user
        from services.task_service import create_task, get_tasks_by_user
        from config.settings import settings
        
        print("✅ Backend modules can be imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Testing project structure...")
    test_project_structure()
    
    print("\nTesting imports...")
    success = test_imports()
    
    if success:
        print("\n🎉 All tests passed! The basic implementation is complete.")
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)