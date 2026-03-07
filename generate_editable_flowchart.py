#!/usr/bin/env python3
"""
Editable Intent Parser System Architecture Flowchart Generator
Modify the parameters below to customize the flowchart appearance and content
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

# EDITABLE PARAMETERS - Modify these to customize your flowchart
FLOWCHART_CONFIG = {
    # Overall layout
    'figure_size': (14, 10),
    'title': 'Intent Parser: AI-Driven Natural Language Mission Extraction System',
    'subtitle': 'Five-Stage Processing Pipeline for UAV Operations',
    
    # Colors (modify these hex codes to change colors)
    'colors': {
        'input': '#E3F2FD',      # Light blue
        'ai': '#FFF3E0',         # Light orange  
        'geo': '#E8F5E8',        # Light green
        'calc': '#FCE4EC',       # Light pink
        'viz': '#F3E5F5',        # Light purple
        'arrow': '#1976D2',      # Blue
        'text': '#333333',       # Dark gray
        'performance': '#F5F5F5', # Light gray
    },
    
    # Stage configurations
    'stages': {
        'stage1': {
            'title': 'Input Acquisition',
            'subtitle': '• Voice Recording\n• Text Input',
            'position': (0.5, 7),
            'size': (2.5, 1.2),
            'details': [
                {'title': 'Voice Input', 'content': 'Whisper API\nTranscription', 'pos': (0.2, 5.5)},
                {'title': 'Text Input', 'content': 'Direct Entry\nBypass', 'pos': (1.7, 5.5)}
            ]
        },
        'stage2': {
            'title': 'AI Structured Extraction',
            'subtitle': '• GPT-4o-mini\n• Context Preservation',
            'position': (4, 7),
            'size': (2.5, 1.2),
            'details': [
                {'title': 'OpenAI Processing', 'content': 'LocationExtraction\nOffsetInfo Schema', 'pos': (4.2, 5.5)}
            ]
        },
        'stage3': {
            'title': 'Geographic Resolution',
            'subtitle': '• Google Maps API\n• OpenStreetMap',
            'position': (7.5, 7),
            'size': (2.5, 1.2),
            'details': [
                {'title': 'Primary', 'content': 'Google Maps\nGeocoding', 'pos': (7.2, 5.5)},
                {'title': 'Fallback', 'content': 'OpenStreetMap\nBackup', 'pos': (8.7, 5.5)}
            ]
        },
        'stage4': {
            'title': 'Offset Calculation',
            'subtitle': '• Spherical Geometry\n• ±1m Precision',
            'position': (4, 3.5),
            'size': (2.5, 1.2),
            'details': [
                {'title': 'Mathematical Engine', 'content': 'Earth Radius: 6,371km\nTrigonometry Formulas', 'pos': (4.2, 2)}
            ]
        },
        'stage5': {
            'title': 'Map Visualization',
            'subtitle': '• Auto Browser Launch\n• Google Maps Display',
            'position': (7.5, 3.5),
            'size': (2.5, 1.2),
            'details': [
                {'title': 'User Interface', 'content': 'Reference + Target\nZero Menu Navigation', 'pos': (7.7, 2)}
            ]
        }
    },
    
    # Performance metrics (edit these values)
    'performance_metrics': {
        'title': 'PERFORMANCE\nMETRICS',
        'position': (11, 6),
        'size': (2.5, 2.5),
        'metrics': [
            {'text': '94.4% Accuracy', 'color': '#2E7D32', 'bold': True},
            {'text': '2.06s Avg Speed', 'color': '#1976D2', 'bold': True},
            {'text': '6 Countries Tested', 'color': '#333333', 'bold': False},
            {'text': '18 Test Scenarios', 'color': '#333333', 'bold': False},
            {'text': 'Voice Input 40% Faster', 'color': '#333333', 'bold': False},
        ]
    },
    
    # Example text at bottom
    'example': {
        'main': 'Example: "Deliver supplies 4km west of Queanbeyan"',
        'flow': 'Voice → AI Extraction → Geocoding → Offset Math → Map Display'
    }
}

def create_stage_box(ax, stage_key, stage_config, color):
    """Create a stage box with title and subtitle"""
    pos = stage_config['position']
    size = stage_config['size']
    
    # Main stage box
    stage_box = FancyBboxPatch(pos, size[0], size[1], boxstyle="round,pad=0.1", 
                              facecolor=color, edgecolor=get_border_color(color), linewidth=2)
    ax.add_patch(stage_box)
    
    # Stage number and title
    center_x = pos[0] + size[0]/2
    center_y = pos[1] + size[1]/2
    
    ax.text(center_x, center_y + 0.3, f'STAGE {stage_key[-1]}', ha='center', va='center', 
            fontweight='bold', fontsize=10)
    ax.text(center_x, center_y, stage_config['title'], ha='center', va='center', 
            fontweight='bold', fontsize=11)
    ax.text(center_x, center_y - 0.3, stage_config['subtitle'], ha='center', va='center', 
            fontsize=9)
    
    return center_x, center_y

def create_detail_boxes(ax, stage_config, color):
    """Create detail boxes for each stage"""
    for detail in stage_config['details']:
        detail_box = FancyBboxPatch(detail['pos'], 1.1 if len(stage_config['details']) == 2 else 2.1, 0.8, 
                                   boxstyle="round,pad=0.05", facecolor='#FFFFFF', 
                                   edgecolor=get_border_color(color), linewidth=1)
        ax.add_patch(detail_box)
        
        detail_center_x = detail['pos'][0] + (1.1 if len(stage_config['details']) == 2 else 2.1)/2
        detail_center_y = detail['pos'][1] + 0.4
        
        ax.text(detail_center_x, detail_center_y + 0.15, detail['title'], ha='center', va='center', 
                fontweight='bold', fontsize=9)
        ax.text(detail_center_x, detail_center_y - 0.15, detail['content'], ha='center', va='center', 
                fontsize=8)

def get_border_color(facecolor):
    """Get appropriate border color for each facecolor"""
    color_map = {
        '#E3F2FD': '#1976D2',
        '#FFF3E0': '#F57C00',
        '#E8F5E8': '#388E3C',
        '#FCE4EC': '#C2185B',
        '#F3E5F5': '#7B1FA2'
    }
    return color_map.get(facecolor, '#333333')

def create_performance_box(ax, config):
    """Create performance metrics box"""
    perf_config = config['performance_metrics']
    perf_box = FancyBboxPatch(perf_config['position'], perf_config['size'][0], perf_config['size'][1], 
                             boxstyle="round,pad=0.1", facecolor=config['colors']['performance'], 
                             edgecolor='#424242', linewidth=2)
    ax.add_patch(perf_box)
    
    center_x = perf_config['position'][0] + perf_config['size'][0]/2
    base_y = perf_config['position'][1] + perf_config['size'][1] - 0.7
    
    ax.text(center_x, base_y, perf_config['title'], ha='center', va='center', 
            fontweight='bold', fontsize=11)
    
    y_offset = 0.3
    for metric in perf_config['metrics']:
        ax.text(center_x, base_y - y_offset, metric['text'], ha='center', va='center', 
                fontweight='bold' if metric['bold'] else 'normal', 
                fontsize=10 if metric['bold'] else 9, color=metric['color'])
        y_offset += 0.2

def create_arrows(ax, config):
    """Create flow arrows between stages"""
    arrow_color = config['colors']['arrow']
    
    # Stage 1 to Stage 2
    arrow1 = ConnectionPatch((3, 7.6), (4, 7.6), "data", "data",
                            arrowstyle="->", shrinkA=5, shrinkB=5, 
                            mutation_scale=20, fc=arrow_color, ec=arrow_color, linewidth=2)
    ax.add_patch(arrow1)
    
    # Stage 2 to Stage 3  
    arrow2 = ConnectionPatch((6.5, 7.6), (7.5, 7.6), "data", "data",
                            arrowstyle="->", shrinkA=5, shrinkB=5, 
                            mutation_scale=20, fc=arrow_color, ec=arrow_color, linewidth=2)
    ax.add_patch(arrow2)
    
    # Stage 3 to Stage 4 (curved)
    arrow3 = ConnectionPatch((8.75, 7), (5.25, 4.7), "data", "data",
                            arrowstyle="->", shrinkA=5, shrinkB=5, 
                            mutation_scale=20, fc=arrow_color, ec=arrow_color, linewidth=2,
                            connectionstyle="arc3,rad=-0.3")
    ax.add_patch(arrow3)
    
    # Stage 4 to Stage 5
    arrow4 = ConnectionPatch((6.5, 4.1), (7.5, 4.1), "data", "data",
                            arrowstyle="->", shrinkA=5, shrinkB=5, 
                            mutation_scale=20, fc=arrow_color, ec=arrow_color, linewidth=2)
    ax.add_patch(arrow4)

def create_editable_flowchart(config=FLOWCHART_CONFIG):
    """Main function to create the flowchart with editable configuration"""
    
    # Create figure and axis
    fig, ax = plt.subplots(1, 1, figsize=config['figure_size'])
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(7, 9.5, config['title'], ha='center', va='center', fontsize=16, 
            fontweight='bold', color=config['colors']['text'])
    ax.text(7, 9, config['subtitle'], ha='center', va='center', fontsize=12, 
            style='italic', color=config['colors']['text'])
    
    # Create all stages
    stage_colors = [config['colors']['input'], config['colors']['ai'], 
                   config['colors']['geo'], config['colors']['calc'], config['colors']['viz']]
    
    for i, (stage_key, stage_config) in enumerate(config['stages'].items()):
        create_stage_box(ax, stage_key, stage_config, stage_colors[i])
        create_detail_boxes(ax, stage_config, stage_colors[i])
    
    # Create performance metrics box
    create_performance_box(ax, config)
    
    # Create arrows
    create_arrows(ax, config)
    
    # Add example text at bottom
    ax.text(7, 0.8, config['example']['main'], ha='center', va='center', fontsize=11, 
            fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", facecolor='#FFFDE7', 
            edgecolor='#FBC02D'))
    ax.text(7, 0.4, config['example']['flow'], ha='center', va='center', fontsize=10, 
            style='italic', color='#555555')
    
    plt.tight_layout()
    return fig

def main():
    """Generate both PNG and SVG versions of the flowchart"""
    
    # Generate the flowchart
    fig = create_editable_flowchart()
    
    # Save as PNG (high resolution)
    png_path = '/home/moham/mavsdk_bin/mini/INTENT_PARSER_FLOWCHART_EDITABLE.png'
    fig.savefig(png_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    # Save as SVG (vector format - fully editable)
    svg_path = '/home/moham/mavsdk_bin/mini/INTENT_PARSER_FLOWCHART_EDITABLE.svg'
    fig.savefig(svg_path, format='svg', bbox_inches='tight',
                facecolor='white', edgecolor='none')
    
    print("=== EDITABLE FLOWCHART FILES GENERATED ===")
    print(f"PNG Version: {png_path}")
    print(f"SVG Version: {svg_path}")
    print("\n=== HOW TO EDIT ===")
    print("1. PYTHON SCRIPT EDITING:")
    print("   - Modify FLOWCHART_CONFIG dictionary at the top of this file")
    print("   - Change colors, text, positions, sizes, performance metrics")
    print("   - Run the script again to regenerate")
    print("\n2. SVG EDITING:")
    print("   - Open the .svg file in:")
    print("     • Inkscape (free, full-featured)")
    print("     • Adobe Illustrator")
    print("     • CorelDRAW")
    print("     • Web browsers (basic editing)")
    print("   - Edit text, colors, shapes, positions directly")
    print("   - Export to PNG, PDF, or other formats")
    print("\n3. CONFIGURATION OPTIONS:")
    print("   - Colors: Modify hex codes in 'colors' section")
    print("   - Text: Change titles, subtitles, performance metrics")
    print("   - Layout: Adjust positions and sizes")
    print("   - Content: Add/remove stages or details")
    
    plt.close(fig)

if __name__ == "__main__":
    main()
