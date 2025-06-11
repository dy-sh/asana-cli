#!/usr/bin/env python3
"""
Asana Project Progress Bar Display

This script connects to the Asana API and displays progress bars for all projects
in the console, showing completion percentage based on completed vs total tasks.
"""

import os
import sys
from typing import List, Dict, Any
import asana
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

class AsanaProgressTracker:
    def __init__(self, api_key: str = None):
        """
        Initialize the Asana progress tracker.
        
        Args:
            api_key (str): Asana API key. If None, will try to get from environment variable.
        """
        self.console = Console()
        
        # Get API key from parameter or environment variable
        if api_key is None:
            api_key = os.getenv('ASANA_API_KEY')
            if not api_key:
                self.console.print("[red]Error: ASANA_API_KEY environment variable not set or no API key provided[/red]")
                self.console.print("Please set your Asana API key as an environment variable:")
                self.console.print("  Windows: set ASANA_API_KEY=your_api_key_here")
                self.console.print("  Linux/Mac: export ASANA_API_KEY=your_api_key_here")
                sys.exit(1)
        
        # Initialize Asana client
        try:
            self.client = asana.Client.access_token(api_key)
            # Test the connection
            self.client.users.me()
            self.console.print("[green]✓ Successfully connected to Asana API[/green]")
        except Exception as e:
            self.console.print(f"[red]Error connecting to Asana API: {e}[/red]")
            sys.exit(1)
    
    def get_all_projects(self) -> List[Dict[str, Any]]:
        """
        Fetch all projects accessible to the user.
        
        Returns:
            List of project dictionaries
        """
        try:
            self.console.print("[yellow]Fetching projects...[/yellow]")
            
            # Get all workspaces
            workspaces = self.client.workspaces.find_all()
            
            all_projects = []
            for workspace in workspaces:
                workspace_name = workspace.get('name', 'Unknown Workspace')
                self.console.print(f"  [blue]Scanning workspace: {workspace_name}[/blue]")
                
                # Get projects in this workspace
                projects = self.client.projects.find_all({
                    'workspace': workspace['gid'],
                    'opt_fields': 'name,completed,completed_at,owner,team,notes,color,created_at,due_date,start_on,archived'
                })
                
                for project in projects:
                    project['workspace_name'] = workspace_name
                    all_projects.append(project)
            
            self.console.print(f"[green]✓ Found {len(all_projects)} projects[/green]")
            return all_projects
            
        except Exception as e:
            self.console.print(f"[red]Error fetching projects: {e}[/red]")
            return []
    
    def get_project_progress(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate progress for a specific project based on completed tasks.
        
        Args:
            project: Project dictionary from Asana API
            
        Returns:
            Dictionary with progress information
        """
        try:
            project_gid = project['gid']
            project_name = project.get('name', 'Unnamed Project')
            
            # Get all tasks in the project
            tasks_generator = self.client.tasks.find_by_project(project_gid, {
                'opt_fields': 'completed,completed_at,name'
            })
            
            # Convert generator to list
            tasks = list(tasks_generator)
            
            total_tasks = len(tasks)
            completed_tasks = sum(1 for task in tasks if task.get('completed', False))
            
            # Calculate percentage
            percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            return {
                'name': project_name,
                'workspace': project.get('workspace_name', 'Unknown'),
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'percentage': percentage,
                'completed': project.get('completed', False),
                'archived': project.get('archived', False),
                'color': project.get('color', 'light-blue')
            }
            
        except Exception as e:
            self.console.print(f"[red]Error calculating progress for project {project.get('name', 'Unknown')}: {e}[/red]")
            return {
                'name': project.get('name', 'Unknown'),
                'workspace': project.get('workspace_name', 'Unknown'),
                'total_tasks': 0,
                'completed_tasks': 0,
                'percentage': 0,
                'completed': project.get('completed', False),
                'archived': project.get('archived', False),
                'color': 'red'
            }
    
    def display_progress_bars(self, projects: List[Dict[str, Any]]):
        """
        Display progress bars for all projects in a nice console format.
        
        Args:
            projects: List of project progress dictionaries
        """
        if not projects:
            self.console.print("[yellow]No projects found to display.[/yellow]")
            return
        
        # Create a table to display all projects
        table = Table(title="Asana Projects Progress", show_header=True, header_style="bold magenta")
        table.add_column("Project Name", style="cyan", width=30)
        table.add_column("Workspace", style="blue", width=20)
        table.add_column("Progress", style="green", width=40)
        table.add_column("Tasks", style="yellow", width=15)
        table.add_column("Status", style="white", width=10)
        
        # Sort projects by percentage (descending)
        sorted_projects = sorted(projects, key=lambda x: x['percentage'], reverse=True)
        
        for project in sorted_projects:
            # Create progress bar
            progress_bar = self._create_progress_bar(project['percentage'])
            
            # Determine status
            if project['completed']:
                status = "✅ Done"
                status_style = "green"
            elif project['archived']:
                status = "📦 Archived"
                status_style = "dim"
            else:
                status = "🔄 Active"
                status_style = "yellow"
            
            # Add row to table
            table.add_row(
                project['name'][:28] + "..." if len(project['name']) > 30 else project['name'],
                project['workspace'][:18] + "..." if len(project['workspace']) > 20 else project['workspace'],
                progress_bar,
                f"{project['completed_tasks']}/{project['total_tasks']}",
                Text(status, style=status_style)
            )
        
        # Display the table
        self.console.print()
        self.console.print(table)
        
        # Display summary statistics
        self._display_summary(projects)
    
    def _create_progress_bar(self, percentage: float) -> str:
        """
        Create a text-based progress bar.
        
        Args:
            percentage: Progress percentage (0-100)
            
        Returns:
            String representation of progress bar
        """
        bar_length = 20
        filled_length = int(bar_length * percentage / 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        return f"{bar} {percentage:.1f}%"
    
    def _display_summary(self, projects: List[Dict[str, Any]]):
        """
        Display summary statistics.
        
        Args:
            projects: List of project progress dictionaries
        """
        total_projects = len(projects)
        completed_projects = sum(1 for p in projects if p['completed'])
        active_projects = sum(1 for p in projects if not p['completed'] and not p['archived'])
        archived_projects = sum(1 for p in projects if p['archived'])
        
        total_tasks = sum(p['total_tasks'] for p in projects)
        completed_tasks = sum(p['completed_tasks'] for p in projects)
        overall_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        summary_text = f"""
        📊 Summary:
        • Total Projects: {total_projects}
        • Active Projects: {active_projects}
        • Completed Projects: {completed_projects}
        • Archived Projects: {archived_projects}
        • Total Tasks: {total_tasks}
        • Completed Tasks: {completed_tasks}
        • Overall Progress: {overall_percentage:.1f}%
        """
        
        summary_panel = Panel(summary_text, title="Project Summary", border_style="blue")
        self.console.print(summary_panel)
    
    def run(self):
        """
        Main method to run the progress tracker.
        """
        self.console.print(Panel.fit(
            "[bold blue]Asana Project Progress Tracker[/bold blue]\n"
            "Fetching and displaying progress for all your Asana projects...",
            border_style="blue"
        ))
        
        # Get all projects
        projects = self.get_all_projects()
        
        if not projects:
            self.console.print("[yellow]No projects found or error occurred.[/yellow]")
            return
        
        # Calculate progress for each project
        self.console.print("[yellow]Calculating project progress...[/yellow]")
        project_progress = []
        
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task("Processing projects...", total=len(projects))
            
            for project in projects:
                progress_info = self.get_project_progress(project)
                project_progress.append(progress_info)
                progress.advance(task)
        
        # Display the results
        self.display_progress_bars(project_progress)


def main():
    """
    Main function to run the Asana progress tracker.
    """
    console = Console()
    
    console.print("[bold blue]Asana Project Progress Tracker[/bold blue]")
    console.print("This tool will display progress bars for all your Asana projects.\n")
    
    # Check if API key is provided as command line argument
    api_key = None
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
        console.print("[green]Using API key from command line argument[/green]")
    
    # Create and run the tracker
    tracker = AsanaProgressTracker(api_key)
    tracker.run()


if __name__ == "__main__":
    main() 