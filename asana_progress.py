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
import keyring
import getpass
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
            api_key (str): Asana API key. If None, will try to get from keychain or prompt user.
        """
        self.console = Console()
        
        # Get API key from parameter, keychain, or prompt user
        if api_key is None:
            api_key = self._get_api_key()
        
        # Initialize Asana client
        try:
            self.client = asana.Client.access_token(api_key)
            # Test the connection
            self.client.users.me()
            self.console.print("[green]✓ Successfully connected to Asana API[/green]")
        except Exception as e:
            self.console.print(f"[red]Error connecting to Asana API: {e}[/red]")
            sys.exit(1)
    
    def _get_api_key(self) -> str:
        """
        Get API key from keychain or prompt user to enter it.
        
        Returns:
            str: The API key
        """
        # Try to get from keychain first
        stored_key = keyring.get_password("asana_cli", "api_key")
        if stored_key:
            self.console.print("[green]✓ Retrieved API key from keychain[/green]")
            return stored_key
        
        # If not in keychain, prompt user
        self.console.print("[yellow]API key not found in keychain. Please enter your Asana API key:[/yellow]")
        self.console.print("You can get your API key from: https://app.asana.com/0/my-apps")
        
        api_key = getpass.getpass("Asana API Key: ")
        
        if not api_key.strip():
            self.console.print("[red]Error: API key cannot be empty[/red]")
            sys.exit(1)
        
        # Store in keychain for future use
        try:
            keyring.set_password("asana_cli", "api_key", api_key)
            self.console.print("[green]✓ API key stored in keychain for future use[/green]")
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not store API key in keychain: {e}[/yellow]")
            self.console.print("[yellow]You'll need to enter the API key again next time[/yellow]")
        
        return api_key
    
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
                
                # Get projects in this workspace with status field
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
            
            # Get actual project status from Asana project_statuses endpoint
            try:
                statuses = self.client.project_statuses.find_by_project(project_gid, {
                    'opt_fields': 'text,color,created_at'
                })
                # Get the most recent status
                if statuses:
                    latest_status = max(statuses, key=lambda x: x.get('created_at', ''))
                    color = latest_status.get('color', None)
                    
                    if color == 'green':
                        status_text = 'On track'
                    elif color == 'blue':
                        status_text = 'On hold'
                    elif color == 'yellow':
                        status_text = 'At risk'
                    elif color == 'red':
                        status_text = 'Off track'
                    elif color == 'complete':
                        status_text = 'Completed'
                    elif color is None:
                        # If no color, try to infer from text
                        text = latest_status.get('text', '').lower()
                        if 'hold' in text or 'pause' in text or 'wait' in text:
                            status_text = 'On hold'
                        elif 'risk' in text or 'delay' in text or 'issue' in text:
                            status_text = 'At risk'
                        elif 'off track' in text or 'problem' in text or 'red' in text:
                            status_text = 'Off track'
                        elif 'track' in text or 'progress' in text or 'good' in text:
                            status_text = 'On track'
                        elif 'complete' in text or 'done' in text:
                            status_text = 'Completed'
                        else:
                            status_text = 'No status'
                    else:
                        # Unknown color value - default to 'on hold' for now
                        status_text = 'on hold'
                else:
                    status_text = 'No status'
            except Exception as e:
                # If we can't fetch status, fall back to basic status
                if project.get('completed', False):
                    status_text = 'completed'
                elif project.get('archived', False):
                    status_text = 'Archived'
                else:
                    status_text = 'Active'
            
            return {
                'name': project_name,
                'workspace': project.get('workspace_name', 'Unknown'),
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'percentage': percentage,
                'completed': project.get('completed', False),
                'archived': project.get('archived', False),
                'status': status_text,
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
                'status': 'Error',
                'color': 'red'
            }
    
    def display_progress_bars(self, projects: List[Dict[str, Any]]):
        """
        Display progress bars for all projects in separate tables by workspace.
        
        Args:
            projects: List of project progress dictionaries
        """
        if not projects:
            self.console.print("[yellow]No projects found to display.[/yellow]")
            return
        
        # Group projects by workspace
        workspaces = {}
        for project in projects:
            workspace_name = project['workspace']
            if workspace_name not in workspaces:
                workspaces[workspace_name] = []
            workspaces[workspace_name].append(project)
        
        # Display separate table for each workspace
        for workspace_name, workspace_projects in workspaces.items():
            self._display_workspace_table(workspace_name, workspace_projects)
        
        # Display summary statistics
        self._display_summary(projects)
    
    def _display_workspace_table(self, workspace_name: str, projects: List[Dict[str, Any]]):
        """
        Display a table for projects in a specific workspace.
        
        Args:
            workspace_name: Name of the workspace
            projects: List of project progress dictionaries for this workspace
        """
        # Create a table for this workspace
        table = Table(title=f"Workspace: {workspace_name}", show_header=True, header_style="bold magenta")
        table.add_column("Project Name", style="cyan", width=35)
        table.add_column("Progress", style="green", width=40)
        table.add_column("Tasks", style="yellow", width=15)
        table.add_column("Status", style="white", width=15)
        
        # Sort projects by percentage (descending)
        sorted_projects = sorted(projects, key=lambda x: x['percentage'], reverse=True)
        
        for project in sorted_projects:
            # Create progress bar
            progress_bar = self._create_progress_bar(project['percentage'])
            
            # Get status with appropriate styling
            status_text = project['status']
            status_style = self._get_status_style(status_text)
            
            # Add row to table
            table.add_row(
                project['name'][:33] + "..." if len(project['name']) > 35 else project['name'],
                progress_bar,
                f"{project['completed_tasks']}/{project['total_tasks']}",
                Text(status_text, style=status_style)
            )
        
        # Display the table
        self.console.print()
        self.console.print(table)
    
    def _get_status_style(self, status: str) -> str:
        """
        Get appropriate styling for project status.
        
        Args:
            status: Project status text
            
        Returns:
            str: Rich text style
        """
        status_lower = status.lower()
        if status_lower == 'on track':
            return "green"
        elif status_lower == 'on hold':
            return "blue"
        elif status_lower == 'at risk':
            return "yellow"
        elif status_lower == 'off track':
            return "red"
        elif status_lower == 'completed':
            return "bold green"
        elif 'archived' in status_lower:
            return "dim"
        else:
            return "white"
    
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
        Summary:
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
    
    # Create and run the tracker (API key will be retrieved from keychain or prompted)
    tracker = AsanaProgressTracker()
    tracker.run()


if __name__ == "__main__":
    main() 