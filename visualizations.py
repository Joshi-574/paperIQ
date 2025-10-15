import plotly.graph_objects as go
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import pandas as pd
from typing import Dict, List

class VisualizationGenerator:
    def __init__(self):
        self.color_palette = ['#6366F1', '#EC4899', '#8B5CF6', '#06B6D4', '#10B981']
    
    def generate_entity_chart(self, entities: Dict) -> str:
        """Generate bar chart for entity frequencies"""
        entity_types = []
        counts = []
        
        for entity_type, entity_list in entities.items():
            if entity_list:  # Only include entities that have values
                entity_types.append(entity_type)
                counts.append(len(entity_list))
        
        fig = go.Figure(data=[
            go.Bar(x=entity_types, y=counts, marker_color=self.color_palette)
        ])
        
        fig.update_layout(
            title='Named Entities Distribution',
            xaxis_title='Entity Types',
            yaxis_title='Count',
            template='plotly_white'
        )
        
        return fig.to_html(include_plotlyjs=False, div_id="entity-chart")
    
    def generate_topic_visualization(self, topics: List[Dict]) -> str:
        """Generate visualization for topics"""
        if not topics:
            return "<p>No topics to visualize</p>"
        
        topic_ids = [f"Topic {topic['topic_id']}" for topic in topics]
        weights = [topic['weight'] for topic in topics]
        
        fig = go.Figure(data=[
            go.Pie(labels=topic_ids, values=weights, hole=0.3)
        ])
        
        fig.update_layout(
            title='Topic Distribution',
            template='plotly_white'
        )
        
        return fig.to_html(include_plotlyjs=False, div_id="topic-chart")
    
    def generate_wordcloud(self, text: str) -> str:
        """Generate word cloud image"""
        if not text:
            return ""
        
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color='white',
            colormap='viridis'
        ).generate(text)
        
        # Convert to base64 for HTML embedding
        img_buffer = BytesIO()
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout(pad=0)
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
        plt.close()
        
        img_buffer.seek(0)
        img_data = base64.b64encode(img_buffer.read()).decode()
        
        return f'<img src="data:image/png;base64,{img_data}" class="wordcloud-img">'
    
    def generate_key_phrases_chart(self, key_phrases: List[tuple]) -> str:
        """Generate bar chart for key phrases"""
        if not key_phrases:
            return "<p>No key phrases to visualize</p>"
        
        phrases, scores = zip(*key_phrases)
        
        fig = go.Figure(data=[
            go.Bar(x=list(phrases), y=list(scores), marker_color=self.color_palette)
        ])
        
        fig.update_layout(
            title='Key Phrases Importance',
            xaxis_title='Phrases',
            yaxis_title='Importance Score',
            template='plotly_white'
        )
        
        return fig.to_html(include_plotlyjs=False, div_id="keyphrases-chart")
    
    def generate_sentiment_gauge(self, sentiment_data: Dict) -> str:
        """Generate sentiment gauge chart"""
        sentiment_score = sentiment_data.get('score', 0)
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = sentiment_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Sentiment Score"},
            delta = {'reference': 0},
            gauge = {
                'axis': {'range': [-1, 1]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [-1, -0.1], 'color': "lightcoral"},
                    {'range': [-0.1, 0.1], 'color': "lightyellow"},
                    {'range': [0.1, 1], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': sentiment_score
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        return fig.to_html(include_plotlyjs=False, div_id="sentiment-gauge")