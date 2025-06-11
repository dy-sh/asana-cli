#!/usr/bin/env python3
"""
Example usage of the Asana Progress Tracker

This file demonstrates different ways to use the AsanaProgressTracker class.
"""

from asana_progress import AsanaProgressTracker

def example_with_environment_variable():
    """
    Example: Using API key from environment variable ASANA_API_KEY
    """
    print("Example 1: Using environment variable ASANA_API_KEY")
    print("Make sure to set: set ASANA_API_KEY=your_key_here (Windows)")
    print("or: export ASANA_API_KEY=your_key_here (Linux/Mac)")
    print()
    
    tracker = AsanaProgressTracker()  # Will use ASANA_API_KEY env var
    tracker.run()

def example_with_api_key_parameter():
    """
    Example: Passing API key directly to the constructor
    """
    print("Example 2: Passing API key directly")
    print("Replace 'your_api_key_here' with your actual Asana API key")
    print()
    
    # Replace this with your actual API key
    api_key = "your_api_key_here"
    
    if api_key == "your_api_key_here":
        print("⚠️  Please replace 'your_api_key_here' with your actual Asana API key")
        return
    
    tracker = AsanaProgressTracker(api_key=api_key)
    tracker.run()

def example_custom_usage():
    """
    Example: Using the tracker class methods individually
    """
    print("Example 3: Custom usage - getting projects only")
    
    # Initialize tracker
    tracker = AsanaProgressTracker()
    
    # Get all projects
    projects = tracker.get_all_projects()
    
    # Calculate progress for first 3 projects only
    print(f"Found {len(projects)} projects. Showing progress for first 3:")
    print()
    
    for i, project in enumerate(projects[:3]):
        progress_info = tracker.get_project_progress(project)
        print(f"Project {i+1}: {progress_info['name']}")
        print(f"  Workspace: {progress_info['workspace']}")
        print(f"  Progress: {progress_info['percentage']:.1f}%")
        print(f"  Tasks: {progress_info['completed_tasks']}/{progress_info['total_tasks']}")
        print()

if __name__ == "__main__":
    print("Asana Progress Tracker - Usage Examples")
    print("=" * 50)
    print()
    
    # Uncomment the example you want to run:
    
    # example_with_environment_variable()
    # example_with_api_key_parameter()
    # example_custom_usage()
    
    print("To run examples, uncomment the desired function call above.")
    print("Make sure you have set up your Asana API key first!") 