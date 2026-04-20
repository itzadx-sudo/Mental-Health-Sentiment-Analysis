import plotly.graph_objects as go
import pandas as pd

COLOR_PALETTE = [
    '#0072FF', '#00B4DB', '#0891B2', '#06B6D4', '#14B8A6',
    '#10B981', '#22C55E', '#84CC16', '#EAB308', '#F59E0B',
    '#F97316', '#EF4444', '#EC4899', '#D946EF', '#A855F7',
    '#8B5CF6', '#6366F1', '#3B82F6', '#0EA5E9', '#06B6D4'
]


def get_plot_layout(title, subtitle=""):
    # Returns a consistent Plotly layout dictionary for all charts.
    return dict(
        title=dict(
            text=f"{title}{subtitle}" if subtitle else f"{title}",
            x=0.5,
            xanchor='center',
            font=dict(size=24, color='#1e293b', family='Inter, sans-serif', weight=800)
        ),
        plot_bgcolor='rgba(255,255,255,0)',
        paper_bgcolor='rgba(255,255,255,0)',
        font=dict(color='#334155', family='Inter, sans-serif'),
        xaxis=dict(
            showgrid=False,
            title='',
            tickfont=dict(size=12, color='#64748b', family='Inter, sans-serif'),
            showline=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(148, 163, 184, 0.12)',
            gridwidth=1,
            title='',
            tickfont=dict(size=12, color='#64748b', family='Inter, sans-serif'),
            showline=False,
            zeroline=False
        ),
        margin=dict(l=50, r=50, t=100, b=60),
        height=400,
        hoverlabel=dict(
            bgcolor='rgba(255,255,255,0.98)',
            font_size=13,
            font_family='Inter, sans-serif',
            font_color='#1e293b',
            bordercolor='rgba(148,163,184,0.3)'
        )
    )


def create_category_distribution_bar(df, color_map, title="Category Distribution"):
    # Creates a bar chart showing the distribution of categories.
    if 'label' not in df.columns:
        return go.Figure()

    category_counts = df['label'].value_counts().reset_index()
    category_counts.columns = ['category', 'count']

    total = category_counts['count'].sum()
    category_counts['pct'] = (category_counts['count'] / total * 100).round(1)

    colors = [color_map.get(cat, COLOR_PALETTE[i % len(COLOR_PALETTE)])
              for i, cat in enumerate(category_counts['category'])]

    fig = go.Figure(data=[
        go.Bar(
            x=category_counts['category'],
            y=category_counts['count'],
            text=category_counts['pct'],
            texttemplate='%{text}%',
            textposition='outside',
            marker=dict(
                color=colors,
                line=dict(color='rgba(255, 255, 255, 0.8)', width=2),
                opacity=0.85
            ),
            hovertemplate='%{x}<br>Count: %{y:,} (%{text}%)<extra></extra>'
        )
    ])

    fig.update_layout(**get_plot_layout(title))
    return fig


def create_sentiment_distribution_stacked(df, color_map, title="Sentiment Distribution by Category"):
    # Creates a 100% stacked bar chart for sentiment distribution.
    if 'sentiment' not in df.columns or 'label' not in df.columns:
        return go.Figure()

    ct = pd.crosstab(df['label'], df['sentiment'], normalize='index') * 100

    fig = go.Figure()
    sentiments = ct.columns

    for i, sentiment in enumerate(sentiments):
        fig.add_trace(go.Bar(
            name=sentiment,
            x=ct.index,
            y=ct[sentiment],
            marker=dict(
                color=COLOR_PALETTE[i % len(COLOR_PALETTE)],
                line=dict(color='rgba(255, 255, 255, 0.8)', width=1.5)
            ),
            hovertemplate='%{x}<br>' + sentiment + ': %{y:.1f}%<extra></extra>'
        ))

    layout = get_plot_layout(title)
    layout.update(dict(
        barmode='stack',
        yaxis=dict(title='Percentage (%)', showgrid=True, gridcolor='rgba(148, 163, 184, 0.12)',
                   tickfont=dict(size=12, color='#64748b', family='Inter, sans-serif')),
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            font=dict(size=11, color='#334155', weight=600, family='Inter, sans-serif')
        )
    ))

    fig.update_layout(**layout)
    return fig


def create_sentiment_intensity_analysis(df, color_map, title="Sentiment Intensity Analysis"):
    # Creates a bar chart showing average sentiment intensity (absolute polarity).
    if 'sentiment_score' not in df.columns and 'polarity' not in df.columns:
        return go.Figure()

    if 'label' not in df.columns:
        return go.Figure()

    score_col = 'sentiment_score' if 'sentiment_score' in df.columns else 'polarity'

    intensity = df.groupby('label').agg({
        score_col: lambda x: abs(x).mean()
    }).reset_index()
    intensity.columns = ['category', 'intensity']
    intensity = intensity.sort_values('intensity', ascending=False)

    colors = [color_map.get(cat, COLOR_PALETTE[i % len(COLOR_PALETTE)])
              for i, cat in enumerate(intensity['category'])]

    fig = go.Figure(data=[
        go.Bar(
            x=intensity['category'],
            y=intensity['intensity'],
            marker=dict(
                color=colors,
                line=dict(color='rgba(255, 255, 255, 0.8)', width=2),
                opacity=0.85
            ),
            hovertemplate='%{x}<br>Intensity: %{y:.3f}<extra></extra>'
        )
    ])

    layout = get_plot_layout(title)
    layout['yaxis'].update(
        dict(title='Sentiment Intensity (Absolute)',
             tickfont=dict(size=12, color='#64748b', family='Inter, sans-serif')))

    fig.update_layout(**layout)
    return fig


def create_avg_polarity_treemap(df, color_map, title="Average Sentiment Polarity Treemap"):
    # Creates a treemap colored by average polarity and sized by count.
    if 'polarity' not in df.columns and 'sentiment_score' not in df.columns:
        return go.Figure()
    if 'label' not in df.columns:
        return go.Figure()

    score_col = 'sentiment_score' if 'sentiment_score' in df.columns else 'polarity'

    avg_pol = df.groupby('label').agg({
        score_col: 'mean',
        'statement': 'count'
    }).reset_index()
    avg_pol.columns = ['category', 'avg_polarity', 'count']

    data_min = avg_pol['avg_polarity'].min()
    data_max = avg_pol['avg_polarity'].max()
    max_abs_val = max(abs(data_min), abs(data_max), 0.01)
    color_limit = max_abs_val * 1.05

    new_cmin = -color_limit
    new_cmax = color_limit

    fig = go.Figure(go.Treemap(
        labels=avg_pol['category'],
        parents=[""] * len(avg_pol),
        values=avg_pol['count'],
        text=avg_pol['avg_polarity'].apply(lambda x: f"{x:.3f}"),
        textposition="middle center",
        textfont=dict(size=14, color='white', family='Inter', weight=700),
        marker=dict(
            colors=avg_pol['avg_polarity'],
            colorscale=[[0, '#EF4444'], [0.5, '#94A3B8'], [1, '#10B981']],
            cmid=0,
            cmin=new_cmin,
            cmax=new_cmax,
            colorbar=dict(
                title="Polarity",
                thickness=15,
                tickfont=dict(size=11, family='Inter, sans-serif')
            ),
            line=dict(color='rgba(255, 255, 255, 0.8)', width=2)
        ),
        hovertemplate='%{label}<br>Avg Polarity: %{text}<br>Count: %{value}<extra></extra>'
    ))

    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            xanchor='center',
            font=dict(size=24, color='#1e293b', family='Inter, sans-serif', weight=800)
        ),
        plot_bgcolor='rgba(255,255,255,0)',
        paper_bgcolor='rgba(255,255,255,0)',
        height=500,
        margin=dict(l=10, r=10, t=80, b=10)
    )

    return fig


def create_emotional_complexity_bar(df, color_map, title="Emotional Complexity by Category"):
    # Creates a bar chart showing average subjectivity (complexity).
    if 'subjectivity' not in df.columns or 'label' not in df.columns:
        return go.Figure()

    complexity = df.groupby('label').agg({
        'subjectivity': 'mean'
    }).reset_index()
    complexity.columns = ['category', 'complexity_score']
    complexity = complexity.sort_values('complexity_score', ascending=False)

    colors = [color_map.get(cat, COLOR_PALETTE[i % len(COLOR_PALETTE)])
              for i, cat in enumerate(complexity['category'])]

    fig = go.Figure(data=[
        go.Bar(
            x=complexity['category'],
            y=complexity['complexity_score'],
            marker=dict(
                color=colors,
                line=dict(color='rgba(255, 255, 255, 0.8)', width=2),
                opacity=0.85
            ),
            hovertemplate='%{x}<br>Complexity Score: %{y:.3f}<extra></extra>'
        )
    ])

    layout = get_plot_layout(title)
    layout['yaxis'].update(
        dict(title='Complexity Score (Subjectivity)',
             tickfont=dict(size=12, color='#64748b', family='Inter, sans-serif')))

    fig.update_layout(**layout)
    return fig


def create_comprehensive_statistical_table(df):
    # Creates a Plotly table summarizing key dataset statistics.
    if df.empty:
        return go.Figure()

    stats_data = []

    stats_data.append(['Total Records', len(df), '', '', ''])
    stats_data.append(['Unique Categories', df['label'].nunique() if 'label' in df.columns else 0, '', '', ''])

    if 'word_len' in df.columns:
        stats_data.append(['Word Length', f"{df['word_len'].mean():.2f}",
                           f"{df['word_len'].median():.2f}",
                           f"{df['word_len'].std():.2f}",
                           f"{df['word_len'].min()}-{df['word_len'].max()}"])

    if 'char_len' in df.columns:
        stats_data.append(['Char Length', f"{df['char_len'].mean():.2f}",
                           f"{df['char_len'].median():.2f}",
                           f"{df['char_len'].std():.2f}",
                           f"{df['char_len'].min()}-{df['char_len'].max()}"])

    score_col = 'sentiment_score' if 'sentiment_score' in df.columns else (
        'polarity' if 'polarity' in df.columns else None)
    if score_col:
        stats_data.append(['Polarity', f"{df[score_col].mean():.3f}",
                           f"{df[score_col].median():.3f}",
                           f"{df[score_col].std():.3f}",
                           f"{df[score_col].min():.3f}-{df[score_col].max():.3f}"])

    if 'subjectivity' in df.columns:
        stats_data.append(['Subjectivity', f"{df['subjectivity'].mean():.3f}",
                           f"{df['subjectivity'].median():.3f}",
                           f"{df['subjectivity'].std():.3f}",
                           f"{df['subjectivity'].min():.3f}-{df['subjectivity'].max():.3f}"])

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['Metric', 'Mean', 'Median', 'Std Dev', 'Range'],
            fill_color='rgba(65, 105, 225, 0.1)',
            align='left',
            font=dict(size=13, color='#1e293b', family='Inter', weight=700),
            height=40,
            line=dict(color='rgba(65, 105, 225, 0.2)', width=1)
        ),
        cells=dict(
            values=list(zip(*stats_data)),
            fill_color=[['rgba(255, 255, 255, 0.9)', 'rgba(248, 250, 252, 0.9)'] * (len(stats_data) // 2 + 1)],
            align='left',
            font=dict(size=12, color='#334155', family='Inter', weight=600),
            height=35,
            line=dict(color='rgba(148, 163, 184, 0.1)', width=1)
        )
    )])

    fig.update_layout(
        title=dict(
            text="Comprehensive Statistical Summary",
            x=0.5,
            xanchor='center',
            font=dict(size=24, color='#1e293b', family='Inter, sans-serif', weight=800)
        ),
        plot_bgcolor='rgba(255,255,255,0)',
        paper_bgcolor='rgba(255,255,255,0)',
        height=400,
        margin=dict(l=20, r=20, t=80, b=20)
    )

    return fig


def create_word_frequency_chart(word_df, color, title):
    # Creates a horizontal bar chart for word frequency.
    colors = [COLOR_PALETTE[i % len(COLOR_PALETTE)] for i in range(len(word_df))]

    fig = go.Figure(data=[
        go.Bar(
            y=word_df['word'],
            x=word_df['frequency'],
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='rgba(255, 255, 255, 0.8)', width=1.5),
                opacity=0.85
            ),
            hovertemplate='%{y}<br>Count: %{x:,}<extra></extra>'
        )
    ])

    layout = get_plot_layout(title)
    layout['xaxis'].update(dict(showgrid=True, gridcolor='rgba(148, 163, 184, 0.12)'))
    layout['yaxis'].update(dict(showgrid=False, autorange='reversed'))
    layout.update(dict(margin=dict(l=120, r=50, t=80, b=50), height=500))

    fig.update_layout(**layout)
    return fig


def create_bigram_chart(bigram_df, color, title):
    # Creates a horizontal bar chart for bigram frequency (reuses word freq chart).
    return create_word_frequency_chart(bigram_df.rename(columns={'bigram': 'word'}), color, title)


def create_word_length_histogram(df, title="Word Length Distribution"):
    # Creates a histogram for the distribution of word lengths in statements.
    if 'word_len' not in df.columns:
        return go.Figure()

    fig = go.Figure(data=[
        go.Histogram(
            x=df['word_len'],
            marker=dict(
                color='#0072FF',
                line=dict(color='rgba(255, 255, 255, 0.8)', width=1.5),
                opacity=0.85
            ),
            xbins=dict(size=5),
            hovertemplate='Word Length: %{x}<br>Count: %{y:,}<extra></extra>'
        )
    ])

    layout = get_plot_layout(title)
    layout['xaxis'].update(title='Word Length (Words per Statement)')
    layout['yaxis'].update(title='Frequency (Count)')
    fig.update_layout(**layout)
    return fig


def create_subjectivity_histogram(df, title="Overall Subjectivity Distribution"):
    # Creates a histogram for the distribution of subjectivity scores.
    if 'subjectivity' not in df.columns:
        return go.Figure()

    fig = go.Figure(data=[
        go.Histogram(
            x=df['subjectivity'],
            marker=dict(
                color='#10B981',
                line=dict(color='rgba(255, 255, 255, 0.8)', width=1.5),
                opacity=0.85
            ),
            xbins=dict(size=0.05),
            hovertemplate='Subjectivity: %{x:.2f}<br>Count: %{y:,}<extra></extra>'
        )
    ])

    layout = get_plot_layout(title)
    layout['xaxis'].update(title='Subjectivity Score (0=Objective, 1=Subjective)')
    layout['yaxis'].update(title='Frequency (Count)')
    fig.update_layout(**layout)
    return fig