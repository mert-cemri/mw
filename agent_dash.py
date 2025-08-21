#!/usr/bin/env python3
"""
MAST CLI Dashboard Interface

Usage:
    python agent_dash.py --trace_file "sample_trace.txt"
"""
import argparse
import os
import sys
import json
import webbrowser
import logging
from datetime import datetime
from pathlib import Path
import time

# Add the current directory to Python path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.llm_judge import MASTLLMJudge
from app.taxonomy import TAXONOMY as MAST_TAXONOMY

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import Streamlit
try:
    import streamlit as st
    import pandas as pd
    import plotly.graph_objects as go
except ImportError:
    logger.error("Required packages not installed. Please run: pip install streamlit pandas plotly")
    sys.exit(1)


def read_trace_file(trace_path: str) -> str:
    """Read the trace file content."""
    try:
        with open(trace_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading trace file: {e}")
        raise


def analyze_trace(trace_content: str, api_key: str = None) -> dict:
    """Analyze the trace using LLM judge."""
    try:
        judge = MASTLLMJudge(api_key=api_key)
        result = judge.evaluate_trace(trace_content)
        return result
    except Exception as e:
        logger.error(f"Error analyzing trace: {e}")
        # Return mock result if API fails
        return {
            "failure_modes": {
                '1.1': 0, '1.2': 0, '1.3': 0, '1.4': 0, '1.5': 0,
                '2.1': 0, '2.2': 0, '2.3': 0, '2.4': 0, '2.5': 0, '2.6': 0,
                '3.1': 0, '3.2': 0, '3.3': 0
            },
            "summary": f"Analysis failed: {str(e)}",
            "task_completion": False,
            "total_failures": 0
        }


def create_dashboard():
    """Create the Streamlit dashboard."""
    st.set_page_config(
        page_title="MAST Agent Dashboard",
        page_icon="🤖",
        layout="wide"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main { padding-top: 0; }
    .failure-detected { background-color: #ffebee; padding: 10px; border-radius: 5px; }
    .no-failure { background-color: #e8f5e9; padding: 10px; border-radius: 5px; }
    .metric-box { 
        background-color: #f5f5f5; 
        padding: 20px; 
        border-radius: 10px; 
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.title("🔍 MAST Agent Dashboard")
    st.markdown("**Multi-Agent Systems Failure Taxonomy Analysis**")
    
    # Get trace file from session state or command line
    trace_file = st.session_state.get('trace_file', None)
    
    if not trace_file:
        st.error("No trace file specified. Please run with: python agent_dash.py --trace_file <path>")
        return
    
    # Read trace content
    try:
        trace_content = read_trace_file(trace_file)
        st.success(f"✅ Loaded trace file: {trace_file}")
    except Exception as e:
        st.error(f"Failed to load trace file: {e}")
        return
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Analysis", "📝 Trace Content", "🎯 MAST Figure", "📈 Visualizations", "📚 Taxonomy Reference"])
    
    with tab1:
        st.header("🔬 Failure Mode Analysis")
        
        # Analyze button
        if st.button("🚀 Analyze Trace", type="primary"):
            with st.spinner("🤖 Running LLM Judge analysis..."):
                # Get API key from environment
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    st.warning("⚠️ No OpenAI API key found. Using mock analysis.")
                
                # Run analysis
                analysis_result = analyze_trace(trace_content, api_key)
                st.session_state.analysis_result = analysis_result
        
        # Display results if available
        if 'analysis_result' in st.session_state:
            result = st.session_state.analysis_result
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📊 Total Failures", result.get('total_failures', 0))
            
            with col2:
                task_status = "✅ Completed" if result.get('task_completion', False) else "❌ Not Completed"
                st.metric("🎯 Task Status", task_status)
            
            with col3:
                trace_length = len(trace_content.split())
                st.metric("📄 Trace Length", f"{trace_length} words")
            
            with col4:
                timestamp = datetime.now().strftime("%H:%M")
                st.metric("⏰ Analyzed At", timestamp)
            
            # Summary
            st.markdown("### 📋 Analysis Summary")
            st.info(result.get('summary', 'No summary available'))
            
            # Failure modes table
            st.markdown("### 🎯 Detected Failure Modes")
            
            failure_data = []
            failure_modes = result.get('failure_modes', {})
            
            for mode_id, detected in failure_modes.items():
                mode_info = MAST_TAXONOMY.get(mode_id, {})
                category = mode_info.get('category', 'unknown')
                name = mode_info.get('name', f'Mode {mode_id}')
                description = mode_info.get('description', '')
                
                failure_data.append({
                    'ID': mode_id,
                    'Category': category.replace('-', ' ').title(),
                    'Failure Mode': name,
                    'Description': description,
                    'Detected': '✅ Yes' if detected else '❌ No'
                })
            
            df = pd.DataFrame(failure_data)
            
            # Style the dataframe
            def highlight_detected(row):
                if row['Detected'] == '✅ Yes':
                    return ['background-color: #ffebee'] * len(row)
                return [''] * len(row)
            
            styled_df = df.style.apply(highlight_detected, axis=1)
            st.dataframe(styled_df, use_container_width=True, height=500)
            
            # Download results
            st.markdown("### 💾 Export Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # JSON export
                export_data = {
                    'trace_file': trace_file,
                    'analysis_date': datetime.now().isoformat(),
                    'failure_modes': failure_modes,
                    'summary': result.get('summary', ''),
                    'task_completion': result.get('task_completion', False),
                    'total_failures': result.get('total_failures', 0)
                }
                
                json_str = json.dumps(export_data, indent=2)
                st.download_button(
                    label="📄 Download JSON Results",
                    data=json_str,
                    file_name=f"mast_analysis_{Path(trace_file).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
            with col2:
                # CSV export
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📊 Download CSV Results",
                    data=csv,
                    file_name=f"mast_analysis_{Path(trace_file).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    
    with tab2:
        st.header("📄 Trace Content")
        
        # Trace info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File", Path(trace_file).name)
        with col2:
            st.metric("Size", f"{len(trace_content)} chars")
        with col3:
            st.metric("Lines", len(trace_content.splitlines()))
        
        # Display trace
        st.text_area("Trace Content", trace_content, height=600, disabled=True)
    
    with tab3:
        st.header("🎯 MAST Taxonomy Visualization")
        
        if 'analysis_result' in st.session_state:
            result = st.session_state.analysis_result
            
            # Add controls
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown("*Failure modes positioned by conversation stage and colored by category*")
            with col2:
                show_zero_modes = st.checkbox("Show zero modes", value=True, key="dash_zero_modes")
            
            # Generate MAST figure
            try:
                from app.mast_figure import render_mast_taxonomy
                
                # Create analysis result in the format expected by render_mast_taxonomy
                formatted_result = {
                    'job_id': f'cli_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                    'failure_modes': result.get('failure_modes', {}),
                    'distribution': {
                        'counts': result.get('failure_modes', {}),
                        'percents': {}
                    },
                    'n_traces': 1,
                    'n_total_steps': len(trace_content.splitlines())
                }
                
                # Calculate percentages (percentage of traces where each mode was detected)
                # For single trace analysis, it's either 0% or 100%
                for mode_id, detected in result.get('failure_modes', {}).items():
                    formatted_result['distribution']['percents'][mode_id] = 100.0 if detected else 0.0
                
                # Configure matplotlib for maximum crispness BEFORE creating figure
                import matplotlib
                matplotlib.use('Agg')  # Use Anti-Grain Geometry backend for better rendering
                matplotlib.rcParams['figure.dpi'] = 300
                matplotlib.rcParams['savefig.dpi'] = 300
                matplotlib.rcParams['font.family'] = ['Helvetica Neue', 'Arial', 'DejaVu Sans', 'sans-serif']
                matplotlib.rcParams['font.size'] = 14  # Increased base font size
                matplotlib.rcParams['font.weight'] = 'normal'
                matplotlib.rcParams['axes.linewidth'] = 1.0  # Cleaner line weight
                matplotlib.rcParams['lines.linewidth'] = 1.2  # Slightly thinner lines
                matplotlib.rcParams['patch.linewidth'] = 1.0
                matplotlib.rcParams['text.antialiased'] = True
                matplotlib.rcParams['path.simplify'] = False  # Disable path simplification for crisp paths
                matplotlib.rcParams['agg.path.chunksize'] = 0  # Disable chunking for better quality
                matplotlib.rcParams['figure.facecolor'] = 'white'
                matplotlib.rcParams['axes.facecolor'] = 'white'
                matplotlib.rcParams['savefig.facecolor'] = 'white'
                matplotlib.rcParams['savefig.edgecolor'] = 'none'
                matplotlib.rcParams['savefig.transparent'] = False
                matplotlib.rcParams['text.hinting'] = 'auto'  # Better text hinting
                matplotlib.rcParams['text.hinting_factor'] = 8  # Improved text clarity
                
                # Use even larger dimensions for maximum crispness
                figure_width = 3200  # Extra large for crisp text
                figure_height = 2000  # Optimal aspect ratio
                
                mast_fig = render_mast_taxonomy(
                    annotation_result=formatted_result,
                    width_px=figure_width,
                    height_px=figure_height,
                    show_zero_modes=show_zero_modes
                )
                
                # Display figure with high quality
                st.pyplot(mast_fig, use_container_width=True)
                
                # Clean up any temporary images that might have been created
                import glob
                temp_images = glob.glob("*.png") + glob.glob("mast_*.png") + glob.glob("test_*.png")
                for temp_img in temp_images:
                    try:
                        os.remove(temp_img)
                    except:
                        pass
                
                # Add download button with maximum quality settings
                import io
                buf = io.BytesIO()
                mast_fig.savefig(
                    buf, 
                    format='png', 
                    dpi=300,                    # Maximum DPI for crisp output
                    bbox_inches='tight',       # Remove excess whitespace
                    facecolor='white',         # Clean white background
                    edgecolor='none',          # No edge color
                    pad_inches=0.05,           # Minimal padding for tighter crop
                    transparent=False,         # Ensure solid white background
                    pil_kwargs={               # Enhanced PNG quality settings
                        'optimize': True, 
                        'quality': 100,
                        'compress_level': 1,   # Best compression quality
                        'icc_profile': None    # Remove ICC profile for smaller file
                    }
                )
                buf.seek(0)
                
                st.download_button(
                    label="📥 Download MAST Figure (PNG)",
                    data=buf.getvalue(),
                    file_name=f"mast_taxonomy_{Path(trace_file).stem}.png",
                    mime="image/png"
                )
                
            except Exception as e:
                st.error(f"Error generating MAST figure: {e}")
                st.info("Showing simplified visualization instead...")
                
                # Fallback visualization
                failure_modes = result.get('failure_modes', {})
                categories = {}
                
                for mode_id, detected in failure_modes.items():
                    if detected or show_zero_modes:
                        mode_info = MAST_TAXONOMY.get(mode_id, {})
                        category = mode_info.get('category', 'unknown')
                        if category not in categories:
                            categories[category] = []
                        categories[category].append(f"{mode_id}: {mode_info.get('name', '')}")
                
                # Display as structured text
                for cat, modes in categories.items():
                    st.subheader(f"📂 {cat.replace('-', ' ').title()}")
                    for mode in modes:
                        st.write(f"• {mode}")
        else:
            st.info("Please run the analysis first to see the MAST visualization.")
    
    with tab4:
        st.header("📊 Failure Mode Visualizations")
        
        if 'analysis_result' in st.session_state:
            result = st.session_state.analysis_result
            failure_modes = result.get('failure_modes', {})
            
            # Prepare data for visualization
            detected_modes = {k: v for k, v in failure_modes.items() if v > 0}
            
            if detected_modes:
                # Bar chart of detected failures
                mode_names = []
                counts = []
                categories = []
                
                for mode_id, count in detected_modes.items():
                    mode_info = MAST_TAXONOMY.get(mode_id, {})
                    mode_names.append(f"{mode_id}: {mode_info.get('name', 'Unknown')}")
                    counts.append(count)
                    categories.append(mode_info.get('category', 'unknown'))
                
                # Color map for categories
                category_colors = {
                    'specification-issues': '#8B5CF6',
                    'inter-agent-misalignment': '#EF4444',
                    'task-verification': '#10B981'
                }
                
                colors = [category_colors.get(cat, '#gray') for cat in categories]
                
                fig = go.Figure(data=[
                    go.Bar(x=mode_names, y=counts, marker_color=colors)
                ])
                
                fig.update_layout(
                    title="Detected Failure Modes",
                    xaxis_title="Failure Mode",
                    yaxis_title="Detection Count",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Category breakdown pie chart
                category_counts = {}
                for mode_id, detected in failure_modes.items():
                    if detected:
                        mode_info = MAST_TAXONOMY.get(mode_id, {})
                        category = mode_info.get('category', 'unknown')
                        category_counts[category] = category_counts.get(category, 0) + 1
                
                if category_counts:
                    fig2 = go.Figure(data=[
                        go.Pie(
                            labels=[cat.replace('-', ' ').title() for cat in category_counts.keys()],
                            values=list(category_counts.values()),
                            marker_colors=[category_colors.get(cat, '#gray') for cat in category_counts.keys()]
                        )
                    ])
                    
                    fig2.update_layout(
                        title="Failure Distribution by Category",
                        height=400
                    )
                    
                    st.plotly_chart(fig2, use_container_width=True)
            else:
                st.success("✅ No failure modes detected in this trace!")
        else:
            st.info("Please run the analysis first to see visualizations.")
    
    with tab5:
        st.header("📚 MAST Taxonomy Reference")
        
        # Group by category
        categories = {}
        for mode_id, mode_info in MAST_TAXONOMY.items():
            category = mode_info.get('category', 'unknown')
            if category not in categories:
                categories[category] = []
            categories[category].append({
                'ID': mode_id,
                'Name': mode_info.get('name', ''),
                'Description': mode_info.get('description', '')
            })
        
        # Display by category
        for category, modes in categories.items():
            st.subheader(f"📂 {category.replace('-', ' ').title()}")
            df = pd.DataFrame(modes)
            st.dataframe(df, use_container_width=True)


def print_terminal_results(trace_file: str, analysis_result: dict):
    """Print analysis results to terminal."""
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    
    console = Console()
    
    # Header
    console.print(Panel.fit(
        f"[bold blue]MAST Analysis Results[/bold blue]\n[dim]Trace: {trace_file}[/dim]",
        border_style="blue"
    ))
    
    # Summary metrics
    console.print("\n[bold]Summary Metrics:[/bold]")
    console.print(f"  • Total Failures Detected: [red]{analysis_result.get('total_failures', 0)}[/red]")
    console.print(f"  • Task Completion: {'[green]✓ Completed[/green]' if analysis_result.get('task_completion', False) else '[red]✗ Not Completed[/red]'}")
    
    # Analysis summary
    console.print("\n[bold]Analysis Summary:[/bold]")
    console.print(Panel(analysis_result.get('summary', 'No summary available'), 
                       title="LLM Judge Summary", 
                       border_style="yellow"))
    
    # Failure modes table
    console.print("\n[bold]Failure Mode Detection:[/bold]")
    
    table = Table(title="MAST Taxonomy Analysis", box=box.ROUNDED)
    table.add_column("ID", style="cyan", width=6)
    table.add_column("Category", style="magenta", width=20)
    table.add_column("Failure Mode", style="white", width=30)
    table.add_column("Detected", justify="center", width=10)
    
    failure_modes = analysis_result.get('failure_modes', {})
    
    # Group by category for better display
    categories = {
        'specification-issues': [],
        'inter-agent-misalignment': [],
        'task-verification': []
    }
    
    for mode_id, detected in failure_modes.items():
        mode_info = MAST_TAXONOMY.get(mode_id, {})
        category = mode_info.get('category', 'unknown')
        
        categories[category].append({
            'id': mode_id,
            'name': mode_info.get('name', f'Mode {mode_id}'),
            'detected': detected
        })
    
    # Add rows by category
    for category, modes in categories.items():
        if modes:
            # Add category separator
            table.add_row("", f"[bold]{category.upper()}[/bold]", "", "")
            
            for mode in modes:
                detected_str = "[green]✓ Yes[/green]" if mode['detected'] else "[dim]✗ No[/dim]"
                table.add_row(
                    mode['id'],
                    category.replace('-', ' ').title(),
                    mode['name'],
                    detected_str
                )
    
    console.print(table)
    
    # Statistics
    detected_count = sum(1 for v in failure_modes.values() if v)
    console.print(f"\n[bold]Statistics:[/bold]")
    console.print(f"  • Failure Modes Detected: {detected_count} / {len(failure_modes)}")
    console.print(f"  • Detection Rate: {(detected_count/len(failure_modes)*100):.1f}%")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description='MAST Agent Dashboard - Analyze multi-agent system traces')
    parser.add_argument('--trace_file', required=True, help='Path to the trace file to analyze')
    parser.add_argument('--port', type=int, default=8501, help='Port to run the dashboard on (default: 8501)')
    parser.add_argument('--no-browser', action='store_true', help='Print results to terminal instead of opening dashboard')
    parser.add_argument('--export', choices=['json', 'csv'], help='Export results to file (terminal mode only)')
    
    args = parser.parse_args()
    
    # Verify trace file exists
    if not os.path.exists(args.trace_file):
        logger.error(f"Trace file not found: {args.trace_file}")
        sys.exit(1)
    
    # If no-browser mode, run analysis and print to terminal
    if args.no_browser:
        try:
            # Try to import rich for better terminal output
            from rich.console import Console
            console = Console()
            
            with console.status("[bold green]Loading trace file..."):
                trace_content = read_trace_file(args.trace_file)
            
            with console.status("[bold green]Running MAST analysis..."):
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    console.print("[yellow]Warning: No OpenAI API key found. Using mock analysis.[/yellow]")
                
                analysis_result = analyze_trace(trace_content, api_key)
            
            # Print results to terminal
            print_terminal_results(args.trace_file, analysis_result)
            
            # Export if requested
            if args.export:
                export_path = Path(args.trace_file).stem + f"_mast_analysis.{args.export}"
                
                if args.export == 'json':
                    export_data = {
                        'trace_file': args.trace_file,
                        'analysis_date': datetime.now().isoformat(),
                        'failure_modes': analysis_result.get('failure_modes', {}),
                        'summary': analysis_result.get('summary', ''),
                        'task_completion': analysis_result.get('task_completion', False),
                        'total_failures': analysis_result.get('total_failures', 0)
                    }
                    with open(export_path, 'w') as f:
                        json.dump(export_data, f, indent=2)
                    console.print(f"\n[green]Results exported to: {export_path}[/green]")
                
                elif args.export == 'csv':
                    failure_data = []
                    for mode_id, detected in analysis_result.get('failure_modes', {}).items():
                        mode_info = MAST_TAXONOMY.get(mode_id, {})
                        failure_data.append({
                            'ID': mode_id,
                            'Category': mode_info.get('category', 'unknown'),
                            'Failure Mode': mode_info.get('name', ''),
                            'Description': mode_info.get('description', ''),
                            'Detected': 'Yes' if detected else 'No'
                        })
                    
                    df = pd.DataFrame(failure_data)
                    df.to_csv(export_path, index=False)
                    console.print(f"\n[green]Results exported to: {export_path}[/green]")
                    
        except ImportError:
            # Fallback to basic printing if rich is not available
            logger.info("Installing rich for better terminal output...")
            os.system("pip install rich")
            logger.info("Please run the command again.")
            sys.exit(1)
    else:
        # Web dashboard mode
        os.environ['MAST_TRACE_FILE'] = args.trace_file
        
        logger.info(f"Starting MAST Dashboard for trace: {args.trace_file}")
        logger.info(f"Dashboard will be available at: http://localhost:{args.port}")
        
        # Create a temporary Streamlit script
        dashboard_script = Path(__file__).parent / "_mast_dashboard.py"
        
        with open(dashboard_script, 'w') as f:
            f.write(f"""
import os
import sys
sys.path.insert(0, '{os.path.dirname(os.path.abspath(__file__))}')

import streamlit as st
st.session_state['trace_file'] = '{args.trace_file}'

from agent_dash import create_dashboard
create_dashboard()
""")
        
        try:
            # Check if port is available
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            port_available = sock.connect_ex(('localhost', args.port)) != 0
            sock.close()
            
            if not port_available:
                logger.error(f"Port {args.port} is already in use. Try a different port with --port <number>")
                logger.info("Common alternative ports: 8502, 8503, 8080, 8888")
                sys.exit(1)
            
            # Open browser
            time.sleep(2)  # Give Streamlit time to start
            webbrowser.open(f'http://localhost:{args.port}')
            
            # Run Streamlit
            os.system(f"streamlit run {dashboard_script} --server.port {args.port} --server.headless true")
        finally:
            # Clean up temporary file
            if dashboard_script.exists():
                dashboard_script.unlink()


if __name__ == "__main__":
    main()