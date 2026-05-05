import dash
from dash import html, dcc, callback, Input, Output, State, ALL, ctx
import pandas as pd
from design import get_styles
import webbrowser
from threading import Timer
from functions import (
    load_data,
    process_data,
    calculate_statistics,
    get_word_frequency,
    get_bigram_frequency
)
from dash_iconify import DashIconify
from visualizations import (
    COLOR_PALETTE,
    create_category_distribution_bar,
    create_sentiment_distribution_stacked,
    create_sentiment_intensity_analysis,
    create_avg_polarity_treemap,
    create_emotional_complexity_bar,
    create_comprehensive_statistical_table,
    create_word_frequency_chart,
    create_bigram_chart,
    create_word_length_histogram,
    create_subjectivity_histogram
)
import plotly.graph_objects as go

#App Configuration
MAX_WORD_LEN = 500
PAGE_SIZE = 50

_LABEL_STYLE = {
    'color': 'rgba(30, 41, 59, 0.85)',
    'fontSize': '13px',
    'fontWeight': '700',
    'marginBottom': '10px',
    'display': 'block',
    'textTransform': 'uppercase',
    'letterSpacing': '0.8px'
}

stored_figures = {}

#App Navigation Structure
VIEWS = [
    {"slug": "overview", "text": "Overview", "icon": "mdi:chart-bar"},
    {"slug": "metrics", "text": "Metrics", "icon": "mdi:chart-line"},
    {"slug": "sentiment", "text": "Sentiment", "icon": "mdi:emoticon-happy-outline"},
    {"slug": "text", "text": "Text Analysis", "icon": "mdi:format-letter-case"},
    {"slug": "data", "text": "Data Explorer", "icon": "mdi:database-search-outline"},
    {"slug": "results", "text": "Results", "icon": "mdi:check-decagram-outline"},
]

#Data Loading and Processing
df, _ = load_data()
clean_df = process_data(df, MAX_WORD_LEN) if df is not None else None

#Global Statistics Calculation
if clean_df is not None and not clean_df.empty:
    stats = calculate_statistics(clean_df)
    total_rows = stats['total_rows']
    avg_word_len = stats['avg_word_len']
    max_word_len_val = stats['max_word_len']
    positive_pct = (stats['positive_count'] / total_rows * 100) if total_rows > 0 else 0
    negative_pct = (stats['negative_count'] / total_rows * 100) if total_rows > 0 else 0
    label_counts = clean_df['label'].value_counts() if 'label' in clean_df.columns else pd.Series()
    num_categories = stats['num_categories']
    label_color_map = {label: COLOR_PALETTE[i % len(COLOR_PALETTE)] for i, label in enumerate(label_counts.index)}
else:
    stats = calculate_statistics(None)
    total_rows = avg_word_len = max_word_len_val = 0
    positive_pct = 0
    negative_pct = 0
    label_counts = pd.Series()
    num_categories = 0
    label_color_map = {}

#Dash App Initialization
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Sentiment Analysis Dashboard"
server = app.server

#Set App HTML Index String
app.index_string = f'''<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}
        <style>
            {get_styles()}
        </style>
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>'''

#Component Creation Functions

def create_navigation(current_view="overview"):
    # Generates the sidebar navigation component.
    nav_links = []
    for view in VIEWS:
        is_active = view["slug"] == current_view
        # Add a specific class for each view to enable individual coloring
        specific_class = f"nav-link-{view['slug']}"
        base_class = f'nav-link {specific_class}'

        link = html.Div([
            DashIconify(icon=view["icon"], className='nav-icon'),
            html.Span(view["text"], className='nav-text')
        ],
            id={'type': 'nav-button', 'index': view["slug"]},
            className=f'{base_class} active' if is_active else base_class,
            n_clicks=0
        )
        nav_links.append(link)

    return html.Div([
        html.Div([
            html.Span("SAD", className='sidebar-logo-text'),
            html.Div(
                DashIconify(icon="mdi:menu", width=24, height=24, id='sidebar-toggle-icon'),
                id='sidebar-toggle',
                className='sidebar-toggle',
                n_clicks=0
            ),
        ], className='sidebar-header'),
        html.Nav(nav_links, className='sidebar-nav')
    ],
        id='sidebar-container',
        className='sidebar-container')


def create_metric_card(label, value):
    # Generates a single metric display card.
    return html.Div([
        html.Div(label, className='metric-label'),
        html.Div(str(value), className='metric-value')
    ], className='metric-card')


def create_modal():
    # Generates the layout for the chart-expansion modal.
    return html.Div([
        html.Div([
            html.Div([
                html.Button('×', id='close-modal', className='close-modal-btn', n_clicks=0),
                html.Div(id='modal-title', className='modal-title'),
                html.Div(id='modal-description', className='modal-description'),
                dcc.Graph(id='modal-chart', config={'displayModeBar': False},
                          style={'height': '600px', 'width': '100%'}),
            ], className='modal-content')
        ], className='modal-inner')
    ], id='chart-modal', className='modal', style={'display': 'none'})


def create_chart_card(fig, key, height=450):
    return html.Div([
        dcc.Graph(
            id={'type': 'modal-chart', 'index': key},
            figure=fig,
            config={'displayModeBar': False},
            style={'height': f'{height}px', 'width': '100%'},
            clear_on_unhover=True
        )
    ], className='chart-container', style={'cursor': 'pointer'},
        id={'type': 'modal-trigger', 'index': key})


#Page Rendering Functions

def render_overview():
    # Renders the layout for the 'Overview' page.
    if clean_df is None or clean_df.empty:
        return html.Div("No data available")

    metric_cards = [
        create_metric_card("Total Statements", f"{total_rows:,}"),
        create_metric_card("Categories", num_categories),
        create_metric_card("Positive Statements", f"{positive_pct:.1f}%"),
        create_metric_card("Negative Statements", f"{negative_pct:.1f}%"),
        create_metric_card("Avg Word Length", f"{avg_word_len:.1f}"),
    ]

    project_info = html.Div([
        html.H2("Project Overview", className='section-header', style={'marginTop': '0'}),
        html.P(
            "This interactive dashboard provides comprehensive analysis of mental health discussions on social media. "
            "As of 2025, with over 5.24 billion social media users globally, understanding the sentiment expressed in "
            "online mental health conversations has become critical for researchers, policymakers, and mental health organizations."
        ),
        html.H3("Problem Statement", className='subsection-header'),
        html.P(
            "Despite abundant mental health discussions online, there is a lack of accessible tools to systematically "
            "monitor and analyze these conversations. The unstructured nature of social media posts makes it challenging "
            "to detect sentiment patterns, shifts in public concern, or early warning signs of widespread distress."
        ),
        html.H3("Project Goal", className='subsection-header'),
        html.P(
            "Create an interactive dashboard to analyze sentiment expressed in social media posts related to mental health. "
            "The dashboard helps stakeholders detect trends, identify areas of concern, and derive actionable insights "
            "from online discussions about mental health conditions including Anxiety, Depression, Stress, and more."
        ),
        html.H3("Analysis Conducted", className='subsection-header'),
        html.Ul([
            html.Li(
                "Data Processing: Loaded 53,043 raw statements, removed 362 null values (retaining 99.3% of data), "
                "and applied TextBlob for sentiment scores."),
            html.Li("Feature Engineering: Calculated word count, polarity, and subjectivity."),
            html.Li(
                "Sentiment Analysis: Visualized sentiment distribution, intensity, polarity, and subjectivity by category."),
            html.Li("Text Analysis: Implemented word and bigram frequency analysis."),
            html.Li("Interactive Dashboard: Built a multi-page Dash app with filtering and interactive charts."),
        ], style={'listStyleType': 'disc', 'paddingLeft': '20px', 'marginBottom': '16px',
                  'color': 'rgba(30, 41, 59, 0.8)'}),
        html.H3("Hypotheses Tested", className='subsection-header'),
        html.Ul([
            html.Li(
                "Posts about Anxiety, Depression, Suicidal thoughts have higher negative sentiment than Normal posts"),
            html.Li("Specific keywords appear more frequently in mental health condition posts"),
            html.Li("Distribution of categories is uneven (Depression dominates)"),
            html.Li("Negative sentiment posts are frequent than positive ones"),
        ], style={'listStyleType': 'disc', 'paddingLeft': '20px', 'marginBottom': '16px',
                  'color': 'rgba(30, 41, 59, 0.8)'}),
        html.H3("Target Audience", className='subsection-header'),
        html.P(
            "Researchers, Policymakers, Mental Health Organizations, Educators, Healthcare Professionals, Students, Journalists, and the Public"
        ),
        html.H3("Tools and Technologies", className='subsection-header'),
        html.P(
            "Python, Pandas, Plotly, Dash, TextBlob, HTML/CSS"
        ),
        html.H3("Team Members", className='subsection-header'),
        html.Ul([
            html.Li("Aditya Jain (35017062)"),
            html.Li("Ryan Alex (35044301)"),
            html.Li("Rohit Kumar Malik (35363998)"),
            html.Li("Izaan Shumaiz (34984006)"),
            html.Li("Mohamed Sinan (35078074)"),
        ], style={'listStyleType': 'disc', 'paddingLeft': '20px', 'marginBottom': '16px',
                  'color': 'rgba(30, 41, 59, 0.8)'}),

    ], className='chart-container',
        style={'cursor': 'default', 'marginTop': '50px', 'paddingTop': '25px'})

    return html.Div([
        html.H2("Dashboard Overview", className='section-header'),
        html.P("Key performance indicators from the dataset",
               style={'color': 'rgba(30, 41, 59, 0.6)', 'fontSize': '14px', 'marginTop': '-10px'}),
        html.Div(metric_cards, className='metrics-container'),
        project_info
    ])


def render_metrics():
    # Renders the layout for the 'Metrics' page.
    if clean_df is None or clean_df.empty:
        return html.Div("No data available")

    fig_dist_bar = create_category_distribution_bar(clean_df, label_color_map, "Category Distribution")
    fig_dist_bar.update_layout(height=450)
    stored_figures['metric_dist_bar'] = fig_dist_bar

    fig_summary_table = create_comprehensive_statistical_table(clean_df)
    fig_summary_table.update_layout(height=450)
    stored_figures['metric_summary_table'] = fig_summary_table

    fig_word_len = create_word_length_histogram(clean_df, "Word Length Distribution")
    fig_word_len.update_layout(height=450)
    stored_figures['metric_word_len'] = fig_word_len

    fig_subjectivity = create_subjectivity_histogram(clean_df, "Overall Subjectivity Distribution")
    fig_subjectivity.update_layout(height=450)
    stored_figures['metric_subjectivity'] = fig_subjectivity


    return html.Div([
        html.H2("Metrics", className='section-header'),
        html.P("Key dataset metrics and statistical summary",
               style={'color': 'rgba(30, 41, 59, 0.6)', 'fontSize': '14px', 'marginTop': '-10px'}),
        html.Div([
            html.Div(create_chart_card(fig_dist_bar, 'metric_dist_bar'), className='col-6'),
            html.Div(create_chart_card(fig_summary_table, 'metric_summary_table'), className='col-6'),
        ], className='row'),
        html.Div([
            html.Div(create_chart_card(fig_word_len, 'metric_word_len'), className='col-6'),
            html.Div(create_chart_card(fig_subjectivity, 'metric_subjectivity'), className='col-6'),
        ], className='row')
    ])


def render_sentiment():
    # Renders the layout for the 'Sentiment' page.
    if clean_df is None or clean_df.empty:
        return html.Div("No data available")

    try:
        fig_stacked = create_sentiment_distribution_stacked(clean_df, label_color_map, "Sentiment by Category")
        fig_stacked.update_layout(height=450)
        stored_figures['sent_stacked'] = fig_stacked

        fig_intensity = create_sentiment_intensity_analysis(clean_df, label_color_map, "Sentiment Intensity Analysis")
        fig_intensity.update_layout(height=450)
        stored_figures['sent_intensity'] = fig_intensity

        fig_complexity = create_emotional_complexity_bar(clean_df, label_color_map,
                                                         "Emotional Complexity (Subjectivity)")
        fig_complexity.update_layout(height=450)
        stored_figures['sent_complexity'] = fig_complexity

        fig_treemap = create_avg_polarity_treemap(clean_df, label_color_map, "Average Polarity by Category")
        fig_treemap.update_layout(height=450)
        stored_figures['sent_treemap'] = fig_treemap

        return html.Div([
            html.H2("Sentiment Analysis", className='section-header'),
            html.P("Comprehensive sentiment metrics and emotional patterns",
                   style={'color': 'rgba(30, 41, 59, 0.6)', 'fontSize': '14px', 'marginTop': '-10px'}),
            html.H3("Distribution and Intensity", className='subsection-header'),
            html.Div([
                html.Div(create_chart_card(fig_stacked, 'sent_stacked'), className='col-6'),
                html.Div(create_chart_card(fig_intensity, 'sent_intensity'), className='col-6'),
            ], className='row'),
            html.Hr(style={'border': 'none', 'borderTop': '1px solid rgba(148,163,184,0.15)', 'margin': '40px 0'}),
            html.H3("Complexity and Polarity", className='subsection-header'),
            html.Div([
                html.Div(create_chart_card(fig_complexity, 'sent_complexity'), className='col-6'),
                html.Div(create_chart_card(fig_treemap, 'sent_treemap'), className='col-6'),
            ], className='row'),
        ])
    except Exception as e:
        print(f"Error rendering sentiment page: {e}")
        import traceback
        traceback.print_exc()
        return html.Div(f"Error loading sentiment analysis: {str(e)}")


def render_text():
    # Renders the layout for the 'Text Analysis' page.
    if clean_df is None or clean_df.empty:
        return html.Div("No data available")

    return html.Div([
        html.H2("Text Analysis", className='section-header'),
        html.P("Word frequency and bigram analysis by category",
               style={'color': 'rgba(30, 41, 59, 0.6)', 'fontSize': '14px', 'marginTop': '-10px'}),
        html.Div([
            html.Div([
                html.Label("Select Category", style=_LABEL_STYLE),
                dcc.Dropdown(
                    id='text-category-dropdown',
                    options=[{'label': cat, 'value': cat} for cat in label_counts.index],
                    value=label_counts.index[0] if len(label_counts) > 0 else None,
                    className='dropdown'
                )
            ], className='input-wrapper', style={'zIndex': 101})
        ]),
        html.Div(id='text-analysis-content', style={'marginTop': '28px'})
    ])


def render_data():
    # Renders the layout for the 'Data Explorer' page.
    if clean_df is None or clean_df.empty:
        return html.Div("No data available")

    categories = sorted(clean_df['label'].unique())

    pagination_controls = html.Div([
        html.Button("Previous Page", id='data-prev-page', n_clicks=0, className='nav-button'),
        html.Div(id='data-page-display', style={
            'color': 'rgba(30, 41, 59, 0.85)',
            'fontSize': '14px',
            'fontWeight': '700',
            'margin': '0 20px'
        }),
        html.Button("Next Page", id='data-next-page', n_clicks=0, className='nav-button')
    ], className='pagination-container')

    return html.Div([
        html.H2("Data Explorer", className='section-header'),
        html.P("Filter and explore the dataset",
               style={'color': 'rgba(30, 41, 59, 0.6)', 'fontSize': '14px', 'marginTop': '-10px'}),
        html.Div([
            html.Div([
                html.Div([
                    html.Label("Filter by Categories", style=_LABEL_STYLE),
                    dcc.Dropdown(
                        id='data-category-dropdown',
                        options=[{'label': 'All Categories', 'value': 'all'}] + [{'label': cat, 'value': cat} for cat in
                                                                                 categories],
                        value='all',
                        className='dropdown'
                    )
                ], className='input-wrapper', id='data-dropdown-wrapper')
            ], className='col-4'),
            html.Div([
                html.Div([
                    html.Label("Min Word Length", style=_LABEL_STYLE),
                    dcc.Input(
                        id='min-word-filter',
                        type='number',
                        value=0,
                        min=0,
                        max=int(max_word_len_val),
                        className='input-field'
                    )
                ], className='input-wrapper')
            ], className='col-4'),
            html.Div([
                html.Div([
                    html.Label("Max Word Length", style=_LABEL_STYLE),
                    dcc.Input(
                        id='max-word-filter',
                        type='number',
                        value=int(max_word_len_val),
                        min=0,
                        max=int(max_word_len_val),
                        className='input-field'
                    )
                ], className='input-wrapper')
            ], className='col-4')
        ], className='row'),
        html.Div(id='filter-metrics', className='metrics-container', style={'marginTop': '40px'}),
        html.H3("Filtered Data", className='subsection-header'),
        html.Div(id='filtered-table', style={'overflowX': 'auto'}),
        pagination_controls,
        dcc.Store(id='data-page-store', data=0)
    ])


def create_hypothesis_card(title, result, icon, icon_color, description):
    # Helper function to create a hypothesis result card.
    return html.Div([
        html.H3(title, style={
            'marginTop': '0',
            'marginBottom': '15px',
            'fontSize': '22px',
            'fontWeight': '800',
            'color': 'rgba(30, 41, 59, 0.85)',
            'letter-spacing': '-0.5px'
        }),
        html.Div([
            DashIconify(icon=icon, width=20, style={'color': icon_color, 'marginRight': '8px'}),
            html.Span(f"Result: {result}", style={'fontWeight': '700', 'color': icon_color, 'fontSize': '15px'})
        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '15px'}),
        html.P(description, style={'fontSize': '14px', 'color': 'rgba(30, 41, 59, 0.8)', 'lineHeight': '1.6'})
    ], className='chart-container',
        style={'height': '100%', 'cursor': 'default', 'padding': '25px'})


def render_results():
    # Renders the layout for the 'Results' page.
    if clean_df is None or clean_df.empty:
        return html.Div("No data available")

    card1 = create_hypothesis_card(
        title="H1: Negative Sentiment",
        result="Confirmed",
        icon="mdi:check-circle-outline",
        icon_color="#10B981",
        description="Analysis of the 'Average Polarity Treemap' and 'Sentiment Intensity' charts confirms this. Categories like 'Anxiety' and 'Depression' exhibit significantly lower average polarity (more negative) compared to 'Normal' posts."
    )

    card2 = create_hypothesis_card(
        title="H2: Specific Keywords",
        result="Confirmed",
        icon="mdi:check-circle-outline",
        icon_color="#10B981",
        description="The 'Text Analysis' page strongly supports this. Filtering for categories like 'Depression' reveals unique and distinct top words (e.g., 'suicidal', 'hopeless') not found in 'Normal' posts, indicating unique linguistic patterns."
    )

    card3 = create_hypothesis_card(
        title="H3: Uneven Distribution",
        result="Confirmed",
        icon="mdi:check-circle-outline",
        icon_color="#10B981",
        description="The 'Category Distribution' chart on the 'Metrics' page clearly validates this. 'Depression' is the most dominant category, which is a critical context for the entire analysis."
    )

    card4 = create_hypothesis_card(
        title="H4: Negative vs. Positive",
        result="Partially Confirmed",
        icon="mdi:information-outline",
        icon_color="#F59E0B",
        description=f"This is more complex. While negative posts ({negative_pct:.1f}%) are a major component, 'Neutral' and 'Positive' statements are also substantial. This suggests conversations include support and recovery, not just distress."
    )

    conclusion = html.Div([
        html.H3("Overall Conclusion", style={
            'marginTop': '0',
            'fontSize': '22px',
            'fontWeight': '800',
            'color': 'rgba(30, 41, 59, 0.85)',
            'letter-spacing': '-0.5px',
            'marginBottom': '24px'
        }),
        html.P(
            "The dashboard successfully visualizes the complex landscape of mental health discussions. The analysis confirms that sentiment and language differ significantly across topics. Key takeaways are:"),
        html.Ul([
            html.Li(
                "Sentiment analysis is effective at differentiating the emotional tone of various mental health topics."),
            html.Li(
                "Text frequency analysis provides clear, actionable insights into the specific language used by communities."),
            html.Li(
                "Conversations are not monolithic; they contain a mix of distress, support, and recovery-focused language."),
        ], style={'listStyleType': 'disc', 'paddingLeft': '20px', 'marginBottom': '0px',
                  'color': 'rgba(30, 41, 59, 0.8)', 'lineHeight': '1.6'}),
    ], className='chart-container',
        style={'cursor': 'default', 'padding': '25px'})

    data_resources = html.Div([
        html.H3("Dataset & Mental Health Resources",
                style={
                    'marginTop': '0',
                    'fontSize': '22px',
                    'fontWeight': '800',
                    'color': 'rgba(30, 41, 59, 0.85)',
                    'letter-spacing': '-0.5px',
                    'marginBottom': '24px'
                }),
        html.P([
            "The dataset used for this analysis is publicly available on Kaggle. You can access it here: ",
            html.A("Mental Health Sentiment Analysis Dataset",
                   href="https://www.kaggle.com/datasets/suchintikasarkar/sentiment-analysis-for-mental-health?resource=download",
                   target="_blank",
                   style={'fontWeight': '700', 'color': 'var(--theme-text-accent)'})
        ], style={'fontSize': '14px', 'color': 'rgba(30, 41, 59, 0.8)', 'lineHeight': '1.6'}),
        html.P("If you or someone you know is struggling, please reach out to a professional. Here are some global resources:",
               style={'fontSize': '14px', 'color': 'rgba(30, 41, 59, 0.8)', 'lineHeight': '1.6', 'marginTop': '20px'}),
        html.Ul([
            html.Li(html.A("Befrienders Worldwide", href="https://www.befrienders.org/", target="_blank",
                           style={'color': 'var(--theme-text-accent)', 'fontWeight': '500'})),
            html.Li(html.A("World Federation for Mental Health", href="https://wfmh.global/", target="_blank",
                           style={'color': 'var(--theme-text-accent)', 'fontWeight': '500'})),
            html.Li(html.A("International Association for Suicide Prevention (IASP)", href="https://www.iasp.info/",
                           target="_blank", style={'color': 'var(--theme-text-accent)', 'fontWeight': '500'})),
        ], style={'listStyleType': 'disc', 'paddingLeft': '20px', 'marginBottom': '0px',
                  'color': 'rgba(30, 41, 59, 0.8)', 'lineHeight': '1.6'}),

    ], className='chart-container',
        style={'cursor': 'default', 'padding': '25px', 'marginTop': '28px'})

    return html.Div([
        html.H2("Analysis Results & Summary", className='section-header'),
        html.P("A summary of findings based on the dashboard's analysis",
               style={'color': 'rgba(30, 41, 59, 0.6)', 'fontSize': '14px', 'marginTop': '-10px'}),
        html.Div([
            html.Div(card1, className='col-6'),
            html.Div(card2, className='col-6'),
            html.Div(card3, className='col-6'),
            html.Div(card4, className='col-6'),
        ], className='row'),
        conclusion,
        data_resources
    ])


#Main App Layout
app.layout = html.Div([
    dcc.Store(id='current-view', data='overview'),
    dcc.Store(id='filtered-data-store', data=[]),
    create_navigation(),
    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.H1("Sentiment Analysis Dashboard", className='main-title'),
                    html.P("Tracking Mental Health states using Tweets", className='main-subtitle')
                ], className='main-header-content')
            ], className='main-header-wrapper'),
            html.Div(id='page-content', className='page-content'),
            create_modal()
        ], className='app-container')
    ],
        id='main-content-wrapper',
        className='main-content-wrapper'),
], id='theme-wrapper', className='theme-overview')


#CALLBACKS

@callback(
    Output('theme-wrapper', 'className'),
    Output('current-view', 'data'),
    Output('page-content', 'children'),
    Output({'type': 'nav-button', 'index': ALL}, 'className'),
    Input({'type': 'nav-button', 'index': ALL}, 'n_clicks'),
    State('current-view', 'data'),
    prevent_initial_call=False
)
def handle_navigation(n_clicks, current_view):
    # Handles page navigation and theme switching based on sidebar clicks.
    triggered_id = ctx.triggered_id
    new_view = current_view

    if triggered_id and isinstance(triggered_id, dict) and 'index' in triggered_id:
        new_view = triggered_id['index']

    if new_view == 'overview':
        content = render_overview()
    elif new_view == 'metrics':
        content = render_metrics()
    elif new_view == 'sentiment':
        content = render_sentiment()
    elif new_view == 'text':
        content = render_text()
    elif new_view == 'data':
        content = render_data()
    elif new_view == 'results':
        content = render_results()
    else:
        content = render_overview()
        new_view = 'overview'

    button_classes = []
    for v in VIEWS:
        slug = v['slug']
        base = f'nav-link nav-link-{slug}'
        if slug == new_view:
            button_classes.append(f'{base} active')
        else:
            button_classes.append(base)

    theme_class = f"theme-{new_view}"

    return theme_class, new_view, content, button_classes


@callback(
    Output('text-analysis-content', 'children'),
    Input('text-category-dropdown', 'value'),
    prevent_initial_call=False
)
def update_text_analysis(category):
    # Updates the word/bigram charts when the category dropdown changes.
    if not category or clean_df is None:
        return html.Div("Select a category")

    filtered = clean_df[clean_df['label'] == category]
    word_freq = get_word_frequency(filtered, category=category)
    bigram_freq = get_bigram_frequency(filtered, category=category)

    fig_word = create_word_frequency_chart(word_freq, '#F97316', f"Top Words - {category}")
    fig_word.update_layout(height=500)
    stored_figures['text_words'] = fig_word

    fig_bigram = create_bigram_chart(bigram_freq, '#F59E0B', f"Top Bigrams - {category}")
    fig_bigram.update_layout(height=500)
    stored_figures['text_bigrams'] = fig_bigram

    return html.Div([
        html.Div(create_chart_card(fig_word, 'text_words', height=500), className='col-6'),
        html.Div(create_chart_card(fig_bigram, 'text_bigrams', height=500), className='col-6'),
    ], className='row')


@callback(
    Output('chart-modal', 'style'),
    Output('modal-chart', 'figure'),
    Output('modal-title', 'children'),
    Output('modal-description', 'children'),
    Input({'type': 'modal-chart', 'index': ALL}, 'clickData'),
    Input({'type': 'modal-trigger', 'index': ALL}, 'n_clicks'),
    Input('close-modal', 'n_clicks'),
    prevent_initial_call=True
)
def handle_chart_modal(click_data_list, n_clicks_list, close_clicks):
    # Manages opening and closing the chart expansion modal.
    triggered_id = ctx.triggered_id
    triggered_input = ctx.triggered[0] if ctx.triggered else None

    if triggered_id == 'close-modal':
        return {'display': 'none'}, go.Figure(), '', ''

    if not triggered_id or not isinstance(triggered_id, dict):
        return {'display': 'none'}, go.Figure(), '', ''

    if not triggered_input or triggered_input['value'] is None:
        return {'display': 'none'}, go.Figure(), '', ''

    chart_index = triggered_id.get('index')

    if chart_index and chart_index in stored_figures:
        fig = stored_figures[chart_index]
        titles = {
            'metric_dist_bar': ("Category Distribution", "Count of statements per category"),
            'metric_summary_table': ("Comprehensive Summary", "Statistical overview of the dataset"),
            'metric_word_len': ("Word Length Distribution", "Distribution of statement length by word count"),
            'metric_subjectivity': ("Subjectivity Distribution", "Distribution of subjectivity scores (0=Objective, 1=Subjective)"),
            'sent_stacked': ("Sentiment Distribution", "Sentiment breakdown by category"),
            'sent_intensity': ("Sentiment Intensity Analysis", "Polarity distribution by category"),
            'sent_complexity': ("Emotional Complexity", "Average subjectivity score by category"),
            'sent_treemap': ("Average Polarity by Category", "Average sentiment polarity and volume by category"),
            'text_words': ("Top Words", "Word frequency analysis"),
            'text_bigrams': ("Top Bigrams", "Phrase frequency analysis"),
        }
        title, desc = titles.get(chart_index, ("Chart", "Expanded view"))
        modal_fig = go.Figure(fig)
        modal_fig.update_layout(height=600, title=None)
        return {'display': 'flex'}, modal_fig, title, desc

    return {'display': 'none'}, go.Figure(), '', ''


@callback(
    Output('filtered-data-store', 'data'),
    Input('data-category-dropdown', 'value'),
    Input('min-word-filter', 'value'),
    Input('max-word-filter', 'value')
)
def update_filtered_data_store(selected_category, min_word, max_word):
    # Filters the main dataframe based on user inputs and stores the resulting indices.
    if clean_df is None or clean_df.empty:
        return []

    if selected_category == 'all':
        filtered = clean_df.copy()
    else:
        filtered = clean_df[clean_df['label'] == selected_category]

    min_word_val = min_word if min_word is not None else 0
    max_word_val = max_word if max_word is not None else int(max_word_len_val)

    filtered = filtered[filtered['word_len'] >= min_word_val]
    filtered = filtered[filtered['word_len'] <= max_word_val]

    return filtered.index.tolist()


@callback(
    Output('data-page-store', 'data'),
    Input('data-prev-page', 'n_clicks'),
    Input('data-next-page', 'n_clicks'),
    Input('filtered-data-store', 'data'),
    State('data-page-store', 'data'),
    prevent_initial_call=True
)
def update_page_number(prev_clicks, next_clicks, filtered_indices, current_page):
    # Manages the current page number for the data explorer table.
    triggered_id = ctx.triggered_id

    if triggered_id == 'filtered-data-store':
        return 0

    max_pages = max(0, (len(filtered_indices) - 1) // PAGE_SIZE)

    if triggered_id == 'data-prev-page' and current_page > 0:
        return current_page - 1
    if triggered_id == 'data-next-page' and current_page < max_pages:
        return current_page + 1

    return current_page


@callback(
    Output('filter-metrics', 'children'),
    Output('filtered-table', 'children'),
    Output('data-page-display', 'children'),
    Output('data-prev-page', 'disabled'),
    Output('data-prev-page', 'style'),
    Output('data-next-page', 'disabled'),
    Output('data-next-page', 'style'),
    Input('data-page-store', 'data'),
    Input('filtered-data-store', 'data')
)
def update_data_outputs(page, filtered_indices):
    # Updates the data table, metrics, and pagination buttons based on filters and page.
    disabled_style = {'opacity': 0.5, 'cursor': 'not-allowed'}
    enabled_style = {'opacity': 1, 'cursor': 'pointer'}

    if not filtered_indices:
        metrics = [
            create_metric_card("Records", 0),
            create_metric_card("Avg Words", "0.0"),
            create_metric_card("Avg Chars", 0),
            create_metric_card("Categories", 0)
        ]
        table = html.Div("No data matching filters.", style={'padding': '20px'})
        page_display = "Page 1 of 1"
        prev_disabled = True
        next_disabled = True
        return metrics, table, page_display, prev_disabled, disabled_style, next_disabled, disabled_style

    filtered_df = clean_df.loc[filtered_indices]

    metrics = [
        create_metric_card("Records", f"{len(filtered_df):,}"),
        create_metric_card("Avg Words", f"{filtered_df['word_len'].mean():.1f}"),
        create_metric_card("Avg Chars", f"{filtered_df['char_len'].mean():.0f}"),
        create_metric_card("Categories", filtered_df['label'].nunique())
    ]

    max_pages = max(0, (len(filtered_df) - 1) // PAGE_SIZE)
    start_idx = page * PAGE_SIZE
    end_idx = (page + 1) * PAGE_SIZE
    display_df = filtered_df.iloc[start_idx:end_idx]

    if not display_df.empty:
        core_cols = ['label', 'statement', 'word_len', 'char_len', 'polarity', 'sentiment']
        other_cols = [col for col in display_df.columns if col not in core_cols]
        display_cols = [col for col in core_cols if col in display_df.columns] + other_cols
        display_df = display_df[display_cols]

        table = html.Table([
            html.Thead(html.Tr([html.Th(col) for col in display_df.columns])),
            html.Tbody([
                html.Tr([html.Td(str(val)[:80] + '...' if len(str(val)) > 80 else str(val)) for val in row])
                for _, row in display_df.iterrows()
            ])
        ], className='data-table')

        table_summary = html.Div([
            table,
            html.P(f"Showing {start_idx + 1} - {min(end_idx, len(filtered_df))} of {len(filtered_df)} records",
                   style={'color': 'rgba(30, 41, 59, 0.6)', 'fontSize': '13px', 'marginTop': '16px'})
        ])
    else:
        table_summary = html.Div("No data", style={'padding': '20px'})

    page_display = f"Page {page + 1} of {max_pages + 1}"
    prev_disabled = (page == 0)
    next_disabled = (page >= max_pages)
    prev_style = disabled_style if prev_disabled else enabled_style
    next_style = disabled_style if next_disabled else enabled_style

    return metrics, table_summary, page_display, prev_disabled, prev_style, next_disabled, next_style


@callback(
    Output('data-dropdown-wrapper', 'className'),
    Input('data-category-dropdown', 'open'),
    State('data-dropdown-wrapper', 'className'),
    prevent_initial_call=True
)
def update_dropdown_wrapper_style(is_open, current_class):
    # Toggles a class on the dropdown wrapper to fix z-index issues.
    if is_open:
        return (current_class or '') + ' open-dropdown'
    else:
        return (current_class or '').replace(' open-dropdown', '')


@callback(
    Output('sidebar-container', 'className'),
    Output('main-content-wrapper', 'className'),
    Output('sidebar-toggle-icon', 'icon'),
    Input('sidebar-toggle', 'n_clicks'),
    State('sidebar-container', 'className'),
    prevent_initial_call=True
)
def toggle_sidebar(n_clicks, current_sidebar_class):
    # Handles the expanding and collapsing of the sidebar.
    sidebar_class = 'sidebar-container'
    content_class = 'main-content-wrapper'
    icon = 'mdi:menu'

    if 'collapsed' in current_sidebar_class:
        sidebar_class = 'sidebar-container'
        content_class = 'main-content-wrapper'
        icon = 'mdi:menu'
    else:
        sidebar_class = 'sidebar-container collapsed'
        content_class = 'main-content-wrapper collapsed'
        icon = 'mdi:menu-close'

    return sidebar_class, content_class, icon


#Run Application
if __name__ == '__main__':
    def open_browser():
        # Automatically opens the web browser to the app's address.
        webbrowser.open_new('http://127.0.0.1:8050')

    Timer(0.5, open_browser).start()
    app.run(port=8050, debug=False)