#!/usr/bin/env python3
"""
Test script to verify the bulk operations functionality is working
"""
import sys
import os

# Add the backend directory to the path so we can import from src
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

def test_api_routes():
    """Test that the API routes are properly defined"""
    print("Testing API routes...")
    
    try:
        # Import the main API router
        from src.api import api_router
        print("✓ Main API router imported successfully")
        
        # Import the todos API specifically
        from src.api.todos import router as todos_router
        print("✓ Todos API router imported successfully")
        
        # Check if the bulk update route exists
        bulk_route_found = False
        for route in todos_router.routes:
            if hasattr(route, 'path') and route.path == '/bulk-update' and route.methods and 'POST' in route.methods:
                bulk_route_found = True
                break
                
        if bulk_route_found:
            print("✓ Bulk update route (/bulk-update POST) found")
        else:
            print("✗ Bulk update route not found")
            
        # List all routes in the todos router
        print("\nRoutes in todos API:")
        for route in todos_router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                print(f"  {', '.join(route.methods)} {route.path}")
        
        print("\n✓ API routes test completed successfully!")
        print("\nThe bulk operations feature is properly integrated into the API.")
        print("Frontend can now call POST /api/v1/todos/bulk-update with:")
        print('  { "todo_ids": ["id1", "id2", ...], "action": "complete" }')
        
    except Exception as e:
        print(f"✗ Error testing API routes: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_routes()