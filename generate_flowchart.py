#!/usr/bin/env python3
"""
Generate Intent Parser System Architecture Flowchart
Creates a PNG diagram showing the five-stage processing pipeline
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_intent_parser_flowchart():
    # Create figure and axis
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Define colors
    input_color = '#E3F2FD'      # Light blue
    ai_color = '#FFF3E0'         # Light orange
    geo_color = '#E8F5E8'        # Light green
    calc_color = '#FCE4EC'       # Light pink
    viz_color = '#F3E5F5'        # Light purple
    arrow_color = '#1976D2'      # Blue
    text_color = '#333333'       # Dark gray
    
    # Title
    ax.text(7, 9.5, 'Intent Parser: AI-Driven Natural Language Mission Extraction System', 
            ha='center', va='center', fontsize=16, fontweight='bold', color=text_color)
    ax.text(7, 9, 'Five-Stage Processing Pipeline for UAV Operations', 
            ha='center', va='center', fontsize=12, style='italic', color=text_color)
    
    # Stage 1: Input Acquisition
    stage1_box = FancyBboxPatch((0.5, 7), 2.5, 1.2, boxstyle="round,pad=0.1", 
                                facecolor=input_color, edgecolor='#1976D2', linewidth=2)
    ax.add_patch(stage1_box)
    ax.text(1.75, 7.8, 'STAGE 1', ha='center', va='center', fontweight='bold', fontsize=10)
    ax.text(1.75, 7.5, 'Input Acquisition', ha='center', va='center', fontweight='bold', fontsize=11)
    ax.text(1.75, 7.2, '• Voice Recording\n• Text Input', ha='center', va='center', fontsize=9)
    
    # Voice/Text detail boxes
    voice_box = FancyBboxPatch((0.2, 5.5), 1.1, 0.8, boxstyle="round,pad=0.05", 
                               facecolor='#FFFFFF', edgecolor='#1976D2', linewidth=1)
    ax.add_patch(voice_box)
    ax.text(0.75, 5.9, 'Voice Input', ha='center', va='center', fontweight='bold', fontsize=9)
    ax.text(0.75, 5.6, 'Whisper API\nTranscription', ha='center', va='center', fontsize=8)
    
    text_box = FancyBboxPatch((1.7, 5.5), 1.1, 0.8, boxstyle="round,pad=0.05", 
                              facecolor='#FFFFFF', edgecolor='#1976D2', linewidth=1)
    ax.add_patch(text_box)
    ax.text(2.25, 5.9, 'Text Input', ha='center', va='center', fontweight='bold', fontsize=9)
    ax.text(2.25, 5.6, 'Direct Entry\nBypass', ha='center', va='center', fontsize=8)
    
    # Stage 2: Structured Extraction
    stage2_box = FancyBboxPatch((4, 7), 2.5, 1.2, boxstyle="round,pad=0.1", 
                                facecolor=ai_color, edgecolor='#F57C00', linewidth=2)
    ax.add_patch(stage2_box)
    ax.text(5.25, 7.8, 'STAGE 2', ha='center', va='center', fontweight='bold', fontsize=10)
    ax.text(5.25, 7.5, 'AI Structured Extraction', ha='center', va='center', fontweight='bold', fontsize=11)
    ax.text(5.25, 7.2, '• GPT-4o-mini\n• Context Preservation', ha='center', va='center', fontsize=9)
    
    # AI detail box
    ai_detail_box = FancyBboxPatch((4.2, 5.5), 2.1, 0.8, boxstyle="round,pad=0.05", 
                                   facecolor='#FFFFFF', edgecolor='#F57C00', linewidth=1)
    ax.add_patch(ai_detail_box)
    ax.text(5.25, 5.9, 'OpenAI Processing', ha='center', va='center', fontweight='bold', fontsize=9)
    ax.text(5.25, 5.6, 'LocationExtraction\nOffsetInfo Schema', ha='center', va='center', fontsize=8)
    
    # Stage 3: Geographic Resolution
    stage3_box = FancyBboxPatch((7.5, 7), 2.5, 1.2, boxstyle="round,pad=0.1", 
                                facecolor=geo_color, edgecolor='#388E3C', linewidth=2)
    ax.add_patch(stage3_box)
    ax.text(8.75, 7.8, 'STAGE 3', ha='center', va='center', fontweight='bold', fontsize=10)
    ax.text(8.75, 7.5, 'Geographic Resolution', ha='center', va='center', fontweight='bold', fontsize=11)
    ax.text(8.75, 7.2, '• Google Maps API\n• OpenStreetMap', ha='center', va='center', fontsize=9)
    
    # Geocoding detail boxes
    gmaps_box = FancyBboxPatch((7.2, 5.5), 1.1, 0.8, boxstyle="round,pad=0.05", 
                               facecolor='#FFFFFF', edgecolor='#388E3C', linewidth=1)
    ax.add_patch(gmaps_box)
    ax.text(7.75, 5.9, 'Primary', ha='center', va='center', fontweight='bold', fontsize=9)
    ax.text(7.75, 5.6, 'Google Maps\nGeocoding', ha='center', va='center', fontsize=8)
    
    osm_box = FancyBboxPatch((8.7, 5.5), 1.1, 0.8, boxstyle="round,pad=0.05", 
                             facecolor='#FFFFFF', edgecolor='#388E3C', linewidth=1)
    ax.add_patch(osm_box)
    ax.text(9.25, 5.9, 'Fallback', ha='center', va='center', fontweight='bold', fontsize=9)
    ax.text(9.25, 5.6, 'OpenStreetMap\nBackup', ha='center', va='center', fontsize=8)
    
    # Stage 4: Offset Calculation
    stage4_box = FancyBboxPatch((4, 3.5), 2.5, 1.2, boxstyle="round,pad=0.1", 
                                facecolor=calc_color, edgecolor='#C2185B', linewidth=2)
    ax.add_patch(stage4_box)
    ax.text(5.25, 4.3, 'STAGE 4', ha='center', va='center', fontweight='bold', fontsize=10)
    ax.text(5.25, 4, 'Offset Calculation', ha='center', va='center', fontweight='bold', fontsize=11)
    ax.text(5.25, 3.7, '• Spherical Geometry\n• ±1m Precision', ha='center', va='center', fontsize=9)
    
    # Math detail box
    math_box = FancyBboxPatch((4.2, 2), 2.1, 0.8, boxstyle="round,pad=0.05", 
                              facecolor='#FFFFFF', edgecolor='#C2185B', linewidth=1)
    ax.add_patch(math_box)
    ax.text(5.25, 2.4, 'Mathematical Engine', ha='center', va='center', fontweight='bold', fontsize=9)
    ax.text(5.25, 2.1, 'Earth Radius: 6,371km\nTrigonometry Formulas', ha='center', va='center', fontsize=8)
    
    # Stage 5: Visualization
    stage5_box = FancyBboxPatch((7.5, 3.5), 2.5, 1.2, boxstyle="round,pad=0.1", 
                                facecolor=viz_color, edgecolor='#7B1FA2', linewidth=2)
    ax.add_patch(stage5_box)
    ax.text(8.75, 4.3, 'STAGE 5', ha='center', va='center', fontweight='bold', fontsize=10)
    ax.text(8.75, 4, 'Map Visualization', ha='center', va='center', fontweight='bold', fontsize=11)
    ax.text(8.75, 3.7, '• Auto Browser Launch\n• Google Maps Display', ha='center', va='center', fontsize=9)
    
    # Visualization detail box
    viz_detail_box = FancyBboxPatch((7.7, 2), 2.1, 0.8, boxstyle="round,pad=0.05", 
                                    facecolor='#FFFFFF', edgecolor='#7B1FA2', linewidth=1)
    ax.add_patch(viz_detail_box)
    ax.text(8.75, 2.4, 'User Interface', ha='center', va='center', fontweight='bold', fontsize=9)
    ax.text(8.75, 2.1, 'Reference + Target\nZero Menu Navigation', ha='center', va='center', fontsize=8)
    
    # Performance metrics box
    perf_box = FancyBboxPatch((11, 6), 2.5, 2.5, boxstyle="round,pad=0.1", 
                              facecolor='#F5F5F5', edgecolor='#424242', linewidth=2)
    ax.add_patch(perf_box)
    ax.text(12.25, 7.8, 'PERFORMANCE', ha='center', va='center', fontweight='bold', fontsize=11)
    ax.text(12.25, 7.5, 'METRICS', ha='center', va='center', fontweight='bold', fontsize=11)
    ax.text(12.25, 7.1, '94.4% Accuracy', ha='center', va='center', fontweight='bold', fontsize=10, color='#2E7D32')
    ax.text(12.25, 6.8, '2.06s Avg Speed', ha='center', va='center', fontweight='bold', fontsize=10, color='#1976D2')
    ax.text(12.25, 6.5, '6 Countries Tested', ha='center', va='center', fontsize=9)
    ax.text(12.25, 6.3, '18 Test Scenarios', ha='center', va='center', fontsize=9)
    ax.text(12.25, 6.1, 'Voice Input 40% Faster', ha='center', va='center', fontsize=9)
    
    # Flow arrows
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
    
    # Input detail connections
    voice_conn = ConnectionPatch((0.75, 6.3), (1.5, 7), "data", "data",
                                arrowstyle="->", shrinkA=2, shrinkB=2, 
                                mutation_scale=15, fc='#666666', ec='#666666', linewidth=1)
    ax.add_patch(voice_conn)
    
    text_conn = ConnectionPatch((2.25, 6.3), (2, 7), "data", "data",
                               arrowstyle="->", shrinkA=2, shrinkB=2, 
                               mutation_scale=15, fc='#666666', ec='#666666', linewidth=1)
    ax.add_patch(text_conn)
    
    # AI detail connection
    ai_conn = ConnectionPatch((5.25, 6.3), (5.25, 7), "data", "data",
                             arrowstyle="->", shrinkA=2, shrinkB=2, 
                             mutation_scale=15, fc='#666666', ec='#666666', linewidth=1)
    ax.add_patch(ai_conn)
    
    # Geocoding detail connections
    gmaps_conn = ConnectionPatch((7.75, 6.3), (8.5, 7), "data", "data",
                                arrowstyle="->", shrinkA=2, shrinkB=2, 
                                mutation_scale=15, fc='#666666', ec='#666666', linewidth=1)
    ax.add_patch(gmaps_conn)
    
    osm_conn = ConnectionPatch((9.25, 6.3), (9, 7), "data", "data",
                              arrowstyle="->", shrinkA=2, shrinkB=2, 
                              mutation_scale=15, fc='#666666', ec='#666666', linewidth=1)
    ax.add_patch(osm_conn)
    
    # Math detail connection
    math_conn = ConnectionPatch((5.25, 2.8), (5.25, 3.5), "data", "data",
                               arrowstyle="->", shrinkA=2, shrinkB=2, 
                               mutation_scale=15, fc='#666666', ec='#666666', linewidth=1)
    ax.add_patch(math_conn)
    
    # Viz detail connection
    viz_conn = ConnectionPatch((8.75, 2.8), (8.75, 3.5), "data", "data",
                              arrowstyle="->", shrinkA=2, shrinkB=2, 
                              mutation_scale=15, fc='#666666', ec='#666666', linewidth=1)
    ax.add_patch(viz_conn)
    
    # Add example flow text
    ax.text(7, 0.8, 'Example: "Deliver supplies 4km west of Queanbeyan"', 
            ha='center', va='center', fontsize=11, fontweight='bold', 
            bbox=dict(boxstyle="round,pad=0.3", facecolor='#FFFDE7', edgecolor='#FBC02D'))
    ax.text(7, 0.4, 'Voice → AI Extraction → Geocoding → Offset Math → Map Display', 
            ha='center', va='center', fontsize=10, style='italic', color='#555555')
    
    plt.tight_layout()
    return fig

def main():
    # Generate the flowchart
    fig = create_intent_parser_flowchart()
    
    # Save as PNG
    output_path = '/home/moham/mavsdk_bin/mini/INTENT_PARSER_FLOWCHART.png'
    fig.savefig(output_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    print(f"Intent Parser flowchart saved to: {output_path}")
    print("Flowchart features:")
    print("- Five-stage processing pipeline visualization")
    print("- Performance metrics display")
    print("- Technical implementation details")
    print("- Color-coded system components")
    print("- High-resolution PNG format (300 DPI)")
    
    plt.close(fig)

if __name__ == "__main__":
    main()
