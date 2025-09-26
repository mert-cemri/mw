"""
Streamlit UI for MAST Annotator Web.
"""
import io
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

# Add the parent directory to sys.path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
API_URL = settings.MAST_API_URL

# Page configuration
st.set_page_config(
    page_title="MAST Annotator Web",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


def get_taxonomy() -> Optional[Dict]:
    """Fetch taxonomy from API."""
    try:
        response = requests.get(f"{API_URL}/taxonomy")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch taxonomy: {e}")
        return None


def annotate_files(files: List) -> Optional[Dict]:
    """Send files to annotation API."""
    try:
        files_data = []
        for uploaded_file in files:
            files_data.append(
                ("files", (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type))
            )
        
        response = requests.post(
            f"{API_URL}/annotate",
            files=files_data
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Annotation failed: {e}")
        return None


def annotate_text(text: str, filename: str = "pasted_trace.txt", precomputed_annotation: Optional[Dict] = None) -> Optional[Dict]:
    """Send text to annotation API or use precomputed annotation."""
    try:
        # If we have a precomputed annotation, use it directly
        if precomputed_annotation is not None:
            # Count the steps in the text
            n_steps = len(text.splitlines())
            
            # Convert failure_modes dict to distribution format
            counts = {}
            for mode_code, detected in precomputed_annotation.items():
                counts[mode_code] = 1 if detected else 0
            
            # Calculate category counts
            categories = {}
            from app.mast_figure.taxonomy import TAXONOMY_SPEC
            # TAXONOMY_SPEC is a dict with "categories" key
            for category in TAXONOMY_SPEC["categories"]:
                cat_count = 0
                for mode in category.modes:
                    if mode.code in counts and counts[mode.code] > 0:
                        cat_count += counts[mode.code]
                if cat_count > 0:
                    categories[category.id] = cat_count
            
            # Calculate percentages
            total = sum(counts.values())
            percents = {}
            for mode_code, count in counts.items():
                percents[mode_code] = (count / total * 100) if total > 0 else 0.0
            
            # Format the response to match what the API would return
            return {
                "job_id": "precomputed_demo",
                "status": "completed",
                "distribution": {
                    "counts": counts,
                    "percents": percents,
                    "categories": categories
                },
                "n_traces": 1,
                "n_total_steps": n_steps,
                "result": {
                    "failure_modes": precomputed_annotation,
                    "summary": f"Precomputed annotation from MAD dataset for {filename}",
                    "trace_files": [filename]
                },
                "created_at": datetime.now().isoformat() + "Z"
            }
        
        # Otherwise, send to API for real annotation
        response = requests.post(
            f"{API_URL}/annotate-text",
            json={"text": text, "filename": filename}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Text annotation failed: {e}")
        return None


def get_random_demo_trace() -> Optional[Dict]:
    """Get a random demo trace from the Hugging Face dataset."""
    import random
    from huggingface_hub import hf_hub_download
    import json
    
    try:
        # Load the dataset from Hugging Face
        REPO_ID = "mcemri/MAD"
        FILENAME = "MAD_full_dataset.json"
        
        # Check if we have the dataset cached in session state
        if 'mad_dataset' not in st.session_state:
            file_path = hf_hub_download(repo_id=REPO_ID, filename=FILENAME, repo_type="dataset")
            with open(file_path, "r") as f:
                data = json.load(f)
            
            # Convert to pandas DataFrame
            df = pd.DataFrame(data)
            
            # Select 5 specific samples with diverse characteristics
            # Using indices: 42, 156, 378, 521, 890
            selected_indices = [42, 156, 378, 521, 890]
            selected_samples = df.iloc[selected_indices].to_dict('records')
            
            st.session_state.mad_dataset = selected_samples
            st.session_state.selected_indices = selected_indices
            
            logger.info(f"Loaded MAD dataset with {len(df)} records. Selected indices: {selected_indices}")
        
        # Randomly select one of the 5 samples
        selected_sample = random.choice(st.session_state.mad_dataset)
        
        # Format the trace content
        trace_content = selected_sample['trace']
        if isinstance(trace_content, list):
            trace_content = '\n'.join(str(item) for item in trace_content)
        elif not isinstance(trace_content, str):
            trace_content = str(trace_content)
        
        # Store the annotation for later use
        st.session_state.current_annotation = selected_sample['mast_annotation']
        
        return {
            'content': trace_content,
            'filename': f"{selected_sample['mas_name']}_{selected_sample['benchmark_name']}_{selected_sample['trace_id']}.txt",
            'source': f"{selected_sample['mas_name']} on {selected_sample['benchmark_name']}",
            'llm_name': selected_sample['llm_name'],
            'precomputed_annotation': selected_sample['mast_annotation']
        }
            
    except Exception as e:
        st.error(f"Error loading demo trace from Hugging Face: {e}")
        return get_fallback_demo_trace()


def get_fallback_demo_trace() -> Dict:
    """Get a fallback demo trace when backend traces are not available."""
    import random
    
    fallback_traces = [
        {
            'content': """User: Can you help me plan a birthday party for my 8-year-old?
Agent1: I'd be happy to help! What's your budget and how many kids?
Agent2: I can suggest themes and activities. What does your child like?
Agent3: I'll help with food and cake ideas!
User: Budget is $200, about 12 kids, she loves unicorns.
Agent1: Perfect! For $200 and 12 kids, I suggest: decorations $50, activities $75, food $75.
Agent2: Great theme choice! Unicorn decorations, maybe a horn-making craft activity?
Agent3: For food: unicorn cake, rainbow fruit kabobs, pink lemonade!
Agent1: Wait, let me recalculate... $50 + $75 + $75 = $200. That works!
Agent2: Actually, horn-making might be messy. How about unicorn temporary tattoos?
Agent3: The cake could be expensive. Maybe unicorn cupcakes instead?""",
            'filename': 'birthday_party_planning.txt',
            'source': 'Sample Dataset'
        },
        {
            'content': """User: I need help debugging this Python code that won't run.
Agent1: I'll check the syntax and structure.
Agent2: I'll look for logical errors and edge cases.
Agent3: Let me examine the error messages.
User: [Pastes code with multiple issues]
Agent1: I see a syntax error on line 5 - missing colon after the if statement.
Agent2: The loop on line 12 is problematic - you're modifying the list while iterating.
Agent3: The error message shows IndexError - check your array bounds.
Agent1: Let me fix the syntax first... [provides partial fix]
Agent2: Actually, the loop issue is more critical... [suggests different approach]
Agent3: Wait, both of you missed the main issue... [points to different problem]
Agent1: I think we should start over and be more systematic.
Agent2: Agreed, let me trace through the logic step by step.
Agent3: The real issue might be in the data preprocessing before this code runs.""",
            'filename': 'python_debugging_session.txt',
            'source': 'Sample Dataset'
        },
        {
            'content': """User: Help me choose a laptop for college.
Agent1: I'll focus on technical specifications and performance.
Agent2: I'll consider budget options and value for money.
Agent3: I'll think about durability and student-specific needs.
User: Budget is $800, need it for computer science classes.
Agent1: For CS, you need good processing power. I recommend Intel i7, 16GB RAM, SSD.
Agent2: That's over budget! For $800, consider i5, 8GB RAM, which is sufficient for most CS work.
Agent3: Don't forget portability - you'll carry it to classes daily. 13-14 inch screen ideal.
Agent1: You're right about budget, but 8GB RAM might not be enough for IDEs and VMs.
Agent2: Fair point. Maybe 12GB RAM as a compromise? Some laptops offer that.
Agent3: Also consider battery life - aim for 8+ hours for full school days.
Agent1: Actually, let me revise: i5 with 12GB RAM and good battery would work.
Agent2: Perfect! That fits the budget and meets the requirements.""",
            'filename': 'laptop_recommendation.txt',
            'source': 'Sample Dataset'
        }
    ]
    
    return random.choice(fallback_traces)


def get_result(job_id: str) -> Optional[Dict]:
    """Fetch result by job ID."""
    try:
        response = requests.get(f"{API_URL}/result/{job_id}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch result: {e}")
        return None


def create_distribution_chart(distribution: Dict) -> go.Figure:
    """Create a bar chart for failure mode distribution."""
    counts = distribution.get("counts", {})
    
    if not counts:
        return go.Figure()
    
    # Sort by count descending
    sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    modes, values = zip(*sorted_items)
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(modes),
            y=list(values),
            text=list(values),
            textposition='auto',
            marker_color='lightblue'
        )
    ])
    
    fig.update_layout(
        title="Failure Mode Distribution",
        xaxis_title="Failure Mode",
        yaxis_title="Count",
        height=400
    )
    
    return fig


def create_category_chart(distribution: Dict) -> go.Figure:
    """Create a pie chart for category distribution."""
    categories = distribution.get("categories", {})
    
    if not categories:
        return go.Figure()
    
    fig = go.Figure(data=[
        go.Pie(
            labels=list(categories.keys()),
            values=list(categories.values()),
            hole=0.3
        )
    ])
    
    fig.update_layout(
        title="Failure Distribution by Category",
        height=400
    )
    
    return fig


def create_csv_download(distribution: Dict, taxonomy: Dict) -> str:
    """Create CSV content for download."""
    counts = distribution.get("counts", {})
    percents = distribution.get("percents", {})
    
    csv_data = []
    for mode, count in counts.items():
        category = taxonomy.get("taxonomy", {}).get(mode, {}).get("category", "unknown")
        percent = percents.get(mode, 0)
        csv_data.append({
            "failure_mode": mode,
            "count": count,
            "percent": percent,
            "category": category
        })
    
    df = pd.DataFrame(csv_data)
    return df.to_csv(index=False)


def create_trace_summary_csv(result: Dict) -> str:
    """Create trace summary CSV for download."""
    summaries = result.get("trace_summaries", [])
    df = pd.DataFrame(summaries)
    return df.to_csv(index=False)


def display_taxonomy_table(taxonomy: Dict):
    """Display taxonomy as an expandable table."""
    tax_data = taxonomy.get("taxonomy", {})
    
    # Group by category
    categories = {}
    for mode_id, mode_info in tax_data.items():
        category = mode_info.get("category", "unknown")
        if category not in categories:
            categories[category] = []
        categories[category].append({
            "ID": mode_id,
            "Name": mode_info.get("name", ""),
            "Description": mode_info.get("description", "")
        })
    
    # Display by category
    for category, modes in categories.items():
        st.subheader(f"📂 {category.title().replace('-', ' ')}")
        df = pd.DataFrame(modes)
        st.dataframe(df, use_container_width=True)


def display_progress_header(current_step=1, has_results=False):
    """Display the 3-step progress header."""
    st.markdown("""
    <style>
    .progress-container {
        background: linear-gradient(90deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 32px;
        border: 1px solid #e2e8f0;
    }
    .progress-steps {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 600px;
        margin: 0 auto;
    }
    .step {
        display: flex;
        flex-direction: column;
        align-items: center;
        flex: 1;
        position: relative;
    }
    .step-circle {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 18px;
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }
    .step-circle.completed {
        background: #10b981;
        color: white;
    }
    .step-circle.active {
        background: #3b82f6;
        color: white;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2);
    }
    .step-circle.pending {
        background: #e2e8f0;
        color: #64748b;
    }
    .step-title {
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 4px;
        font-size: 14px;
    }
    .step-description {
        font-size: 12px;
        color: #64748b;
        text-align: center;
    }
    .step-connector {
        height: 2px;
        background: #e2e8f0;
        position: absolute;
        top: 24px;
        left: calc(50% + 24px);
        right: calc(-50% + 24px);
        z-index: 0;
    }
    .step-connector.completed {
        background: #10b981;
    }
    @media (max-width: 640px) {
        .progress-steps {
            flex-direction: column;
            gap: 20px;
        }
        .step-connector {
            display: none;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Determine step states
    step1_state = "completed" if current_step > 1 else ("active" if current_step == 1 else "pending")
    step2_state = "completed" if current_step > 2 else ("active" if current_step == 2 else "pending")
    step3_state = "completed" if has_results else ("active" if current_step == 3 else "pending")
    
    step1_icon = "✓" if step1_state == "completed" else "1"
    step2_icon = "✓" if step2_state == "completed" else "2"
    step3_icon = "✓" if step3_state == "completed" else "3"
    
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-steps">
            <div class="step">
                <div class="step-circle {step1_state}">{step1_icon}</div>
                <div class="step-title">Add Traces/Try Our Demo</div>
                <div class="step-description">Upload files, paste text, or try demo</div>
                <div class="step-connector {'completed' if current_step > 1 else ''}"></div>
            </div>
            <div class="step">
                <div class="step-circle {step2_state}">{step2_icon}</div>
                <div class="step-title">Analyze and Annotate</div>
                <div class="step-description">Run MAST analysis</div>
                <div class="step-connector {'completed' if current_step > 2 else ''}"></div>
            </div>
            <div class="step">
                <div class="step-circle {step3_state}">{step3_icon}</div>
                <div class="step-title">Inspect & Download</div>
                <div class="step-description">View results and export</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def main():
    """Main Streamlit application."""
    # Enhanced header with logo and title
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("🔍 MAST Annotator Web")
        st.markdown("**Analyze multi-agent interaction traces for failure modes using the MAST taxonomy**")
    
    with col2:
        # Add MAST logo
        try:
            # Try different paths for logo (Docker vs local)
            if os.path.exists("ui/mas22.jpg"):
                st.image("ui/mas22.jpg", width=120)
            elif os.path.exists("mas22.jpg"):
                st.image("mas22.jpg", width=120)
            else:
                st.markdown("**🤖 MAST**")
        except:
            # Fallback if image not found
            st.markdown("**🤖 MAST**")
    
    # Determine current step based on session state
    current_step = 1
    has_results = hasattr(st.session_state, 'annotation_result') and st.session_state.annotation_result
    if has_results:
        current_step = 3
    
    # Display progress header
    display_progress_header(current_step, has_results)
    
    # Citation and links section
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        [Paper: Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/pdf/2503.13657v2)
        """)
    
    with col2:
        st.markdown("""
        [Code](https://github.com/multi-agent-systems-failure-taxonomy/MAST)
        """)
    
    st.markdown("---")
    
    # Fetch taxonomy
    taxonomy = get_taxonomy()
    if not taxonomy:
        st.error("Cannot connect to API. Please check if the backend is running.")
        return
    
    # Sidebar - Contents Index
    st.sidebar.header("📋 Contents")
    st.sidebar.markdown("**Navigation:**")
    st.sidebar.markdown("• [Input Traces](#input-section)")
    st.sidebar.markdown("• [Results](#results-section)")
    st.sidebar.markdown("• [MAST Visualization](#visualization-section)")
    st.sidebar.markdown("• [Downloads](#downloads-section)")
    st.sidebar.markdown("• [Taxonomy Reference](#taxonomy-section)")
    
    # Sidebar - About
    st.sidebar.markdown("---")
    st.sidebar.markdown("**About MAST**")
    st.sidebar.markdown("Multi-Agent Systems Taxonomy for analyzing AI agent collaboration failures")
    
    # Input section with tabs
    st.markdown('<a id="input-section"></a>', unsafe_allow_html=True)
    st.header("📁 Step 1: Add Traces for Analysis")
    
    tab1, tab2, tab3 = st.tabs(["🎯 Try a Demo", "📂 Upload Files", "📝 Paste Text"])
    
    with tab1:
        st.markdown("**🎯 Try a Random Demo**")
        st.markdown("Experience MAST analysis with a randomly selected trace from our research dataset:")
        
        # Random demo functionality
        if st.button("🎲 Load Random Demo Trace", type="secondary", use_container_width=True):
            with st.spinner("🔍 Loading random trace..."):
                demo_data = get_random_demo_trace()
                if demo_data:
                    st.session_state.demo_text = demo_data['content']
                    st.session_state.demo_filename = demo_data['filename']
                    st.session_state.demo_source = demo_data['source']
                    st.session_state.demo_precomputed_annotation = demo_data.get('precomputed_annotation')
                    st.session_state.demo_llm_name = demo_data.get('llm_name', 'Unknown')
                    st.rerun()
        
        # Show loaded demo trace
        if hasattr(st.session_state, 'demo_text') and st.session_state.demo_text:
            st.text_area(
                "📖 Demo trace content:",
                value=st.session_state.demo_text,
                height=300,
                disabled=True
            )
            
            # Demo info
            col_a, col_b = st.columns([1, 1])
            with col_a:
                st.caption(f"📋 {st.session_state.demo_filename}")
            with col_b:
                word_count = len(st.session_state.demo_text.split())
                st.caption(f"📊 {word_count} words")
            
            if hasattr(st.session_state, 'demo_source'):
                st.caption(f"🔗 Source: {st.session_state.demo_source}")
            
            if hasattr(st.session_state, 'demo_precomputed_annotation'):
                st.info("📌 This demo uses precomputed annotations from the MAD dataset")
            
            if st.button("🚀 Analyze Demo Trace", type="primary", key="demo_annotate", use_container_width=True):
                with st.spinner("🔍 Analyzing demo trace..."):
                    # Use precomputed annotation if available
                    precomputed = st.session_state.get('demo_precomputed_annotation')
                    result = annotate_text(st.session_state.demo_text, st.session_state.demo_filename, precomputed_annotation=precomputed)
                
                if result:
                    st.session_state.annotation_result = result
                    st.success("✅ Demo analysis completed!")
                    st.rerun()
        else:
            st.info("👆 Click 'Load Random Demo Trace' to get started")
    
    with tab2:
        st.markdown("Upload multi-agent trace files in various formats")
        
        uploaded_files = st.file_uploader(
            "Choose files",
            type=['json', 'jsonl', 'csv', 'zip', 'txt', 'log'],
            accept_multiple_files=True,
            help="Supported formats: JSON, JSONL, CSV, ZIP, TXT, LOG"
        )
        
        if uploaded_files:
            st.success(f"Uploaded {len(uploaded_files)} file(s)")
            
            # Show file details
            for file in uploaded_files:
                st.write(f"📄 {file.name} ({file.size} bytes)")
        
        # File annotation button
        if uploaded_files and st.button("🚀 Run Annotation on Files", type="primary", key="file_annotate"):
            with st.spinner("Processing uploaded files..."):
                result = annotate_files(uploaded_files)
            
            if result:
                st.session_state.annotation_result = result
                st.success("✅ File annotation completed!")
                st.rerun()
    
    with tab3:
        st.markdown("Paste your own multi-agent trace for analysis")
        
        # Enhanced text input with better UX
        trace_text = st.text_area(
            "Paste your trace here",
            height=300,
            placeholder="""Example multi-agent conversation:
User: Can you help me solve this math problem?
Agent1: I'll help you with that. What's the problem?
Agent2: Let me also assist. I can double-check the work.
User: What's 15 * 24?
Agent1: 15 * 24 = 360
Agent2: That's correct! 15 × 24 = 360

You can paste:
• Raw conversation logs  • JSON/JSONL data
• CSV formatted traces   • Any multi-agent data""",
            help="💡 Tip: The system accepts any text format"
        )
        
        trace_filename = st.text_input(
            "📋 Filename (optional)",
            value="pasted_trace.txt",
            help="Give your trace a descriptive name"
        )
        
        if trace_text.strip():
            word_count = len(trace_text.split())
            char_count = len(trace_text)
            st.caption(f"📊 {word_count} words, {char_count} characters")
        
        # Text annotation button
        if trace_text.strip() and st.button("🚀 Analyze My Trace", type="primary", key="text_annotate", use_container_width=True):
            with st.spinner("🔍 Analyzing your trace..."):
                result = annotate_text(trace_text, trace_filename)
            
            if result:
                st.session_state.annotation_result = result
                st.success("✅ Analysis completed!")
                st.rerun()
    
    # Results section
    if hasattr(st.session_state, 'annotation_result') and st.session_state.annotation_result:
        result = st.session_state.annotation_result
        
        st.markdown("---")
        st.markdown('<a id="results-section"></a>', unsafe_allow_html=True)
        st.header("📊 Step 3: Analysis Results")
        
        # Enhanced summary metrics with better styling
        st.markdown("""
        <style>
        .metric-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin: 10px 0;
        }
        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .metric-label {
            font-size: 1rem;
            opacity: 0.9;
        }
        </style>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📁 Total Traces", result["n_traces"], help="Number of trace files analyzed")
        with col2:
            st.metric("🔢 Total Steps", result["n_total_steps"], help="Combined steps across all traces")
        with col3:
            total_failures = sum(result["distribution"]["counts"].values())
            st.metric("⚠️ Failure Modes", total_failures, help="Number of different failure modes detected")
        with col4:
            completion_time = result.get("created_at", "")
            if completion_time:
                from datetime import datetime
                try:
                    dt = datetime.fromisoformat(completion_time.replace('Z', '+00:00'))
                    time_str = dt.strftime("%H:%M")
                    st.metric("⏰ Completed", time_str, help="Analysis completion time")
                except:
                    st.metric("✅ Status", "Complete", help="Analysis completed successfully")
        
        # MAST Taxonomy Visualization
        st.markdown('<a id="visualization-section"></a>', unsafe_allow_html=True)
        st.subheader("🎯 MAST Taxonomy Visualization")
        
        # Add controls
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("*Failure modes positioned by conversation stage and colored by category*")
        with col2:
            show_zero_modes = st.checkbox("Show zero modes", value=True)
        
        # Generate MAST figure
        try:
            from app.mast_figure import render_mast_taxonomy
            
            # Fixed figure size at 2000px width
            figure_width = 2000
            figure_height = int(figure_width * 0.6)  # 3:5 ratio = 0.6 for better text layout
            
            mast_fig = render_mast_taxonomy(
                annotation_result=result,
                width_px=figure_width,
                height_px=figure_height,
                show_zero_modes=show_zero_modes
            )
            
            # Display figure with constrained size
            # Use a container to limit the display width while keeping high resolution
            with st.container():
                st.markdown("""
                <style>
                .mast-figure {
                    max-width: 800px;
                    width: 100%;
                    height: auto;
                }
                </style>
                """, unsafe_allow_html=True)
                
                # Create a column to center and constrain the figure (larger display)
                col1, col2, col3 = st.columns([1, 8, 1])
                with col2:
                    st.pyplot(mast_fig, use_container_width=True)
            
            # Add download button for the figure
            import io
            buf = io.BytesIO()
            mast_fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
            buf.seek(0)
            
            st.download_button(
                label="📥 Download MAST Figure (PNG)",
                data=buf.getvalue(),
                file_name=f"mast_taxonomy_{result['job_id']}.png",
                mime="image/png"
            )
            
        except Exception as e:
            st.error(f"Error generating MAST figure: {e}")
            st.info("Falling back to standard charts...")
            
            # Fallback to original charts
            col1, col2 = st.columns(2)
            
            with col1:
                fig1 = create_distribution_chart(result["distribution"])
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                fig2 = create_category_chart(result["distribution"])
                st.plotly_chart(fig2, use_container_width=True)
        
        
        # Downloads
        st.markdown('<a id="downloads-section"></a>', unsafe_allow_html=True)
        st.subheader("💾 Downloads")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Distribution CSV
            csv_content = create_csv_download(result["distribution"], taxonomy)
            st.download_button(
                label="📄 Download Distribution CSV",
                data=csv_content,
                file_name=f"failure_distribution_{result['job_id']}.csv",
                mime="text/csv"
            )
        
        with col2:
            # Trace summary CSV
            if result["trace_summaries"]:
                summary_csv = create_trace_summary_csv(result)
                st.download_button(
                    label="📄 Download Trace Summary CSV",
                    data=summary_csv,
                    file_name=f"trace_summary_{result['job_id']}.csv",
                    mime="text/csv"
                )
        
        with col3:
            # Full result JSON
            result_json = json.dumps(result, indent=2, default=str)
            st.download_button(
                label="📄 Download Full Result JSON",
                data=result_json,
                file_name=f"annotation_result_{result['job_id']}.json",
                mime="application/json"
            )
    

    # Taxonomy section at bottom
    st.markdown('<a id="taxonomy-section"></a>', unsafe_allow_html=True)
    st.header("📚 MAST Taxonomy Reference")
    display_taxonomy_table(taxonomy)
    
    # Footer
    st.markdown("---")
    st.markdown("MAST Annotator Web - by UC Berkeley")


if __name__ == "__main__":
    main()