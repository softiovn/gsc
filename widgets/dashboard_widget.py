from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QComboBox, QDateEdit, QProgressBar,
                            QGroupBox, QTextEdit, QTableWidget, QTableWidgetItem,
                            QHeaderView, QTabWidget, QSplitter)
from PySide6.QtCore import QDate, Qt
import pandas as pd
from datetime import datetime, timedelta

class DashboardWidget(QWidget):
    def __init__(self, gsc_client, gemini_analyzer):
        super().__init__()
        self.gsc_client = gsc_client
        self.gemini_analyzer = gemini_analyzer
        self.data_points = []
        self.init_ui()
        self.connect_signals()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Controls section
        controls_layout = QHBoxLayout()
        
        # Site selection
        controls_layout.addWidget(QLabel("Site:"))
        self.site_combo = QComboBox()
        self.site_combo.setMinimumWidth(300)
        controls_layout.addWidget(self.site_combo)
        
        # Date range
        controls_layout.addWidget(QLabel("From:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setCalendarPopup(True)
        controls_layout.addWidget(self.start_date)
        
        controls_layout.addWidget(QLabel("To:"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        controls_layout.addWidget(self.end_date)
        
        # Fetch button
        self.fetch_btn = QPushButton("Fetch Data")
        self.fetch_btn.clicked.connect(self.fetch_data)
        controls_layout.addWidget(self.fetch_btn)
        
        # Analyze button
        self.analyze_btn = QPushButton("Analyze with AI")
        self.analyze_btn.clicked.connect(self.analyze_data)
        self.analyze_btn.setEnabled(False)
        controls_layout.addWidget(self.analyze_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Main content area
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Summary
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Summary stats
        self.summary_group = QGroupBox("Summary Statistics")
        summary_layout = QVBoxLayout()
        self.summary_text = QTextEdit()
        self.summary_text.setMaximumHeight(200)
        summary_layout.addWidget(self.summary_text)
        self.summary_group.setLayout(summary_layout)
        left_layout.addWidget(self.summary_group)
        
        # Analysis results
        self.analysis_group = QGroupBox("AI Analysis")
        analysis_layout = QVBoxLayout()
        self.analysis_text = QTextEdit()
        analysis_layout.addWidget(self.analysis_text)
        self.analysis_group.setLayout(analysis_layout)
        left_layout.addWidget(self.analysis_group)
        
        # Right panel - Data table
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        self.data_table = QTableWidget()
        right_layout.addWidget(self.data_table)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 600])
        
        layout.addWidget(splitter)
        self.setLayout(layout)
    
    def connect_signals(self):
        self.gsc_client.data_loaded.connect(self.on_data_loaded)
        self.gsc_client.error_occurred.connect(self.on_error)
        self.gemini_analyzer.analysis_complete.connect(self.on_analysis_complete)
        self.gemini_analyzer.suggestions_generated.connect(self.on_suggestions_generated)
        self.gemini_analyzer.error_occurred.connect(self.on_error)
    
    def load_sites(self):
        """Load available sites from GSC"""
        sites = self.gsc_client.get_sites()
        self.site_combo.clear()
        for site in sites:
            self.site_combo.addItem(site['siteUrl'], site['siteUrl'])
    
    def fetch_data(self):
        """Fetch data from Google Search Console"""
        if self.site_combo.currentIndex() == -1:
            self.show_message("Please select a site first")
            return
        
        site_url = self.site_combo.currentData()
        start_date = self.start_date.date().toPyDate()
        end_date = self.end_date.date().toPyDate()
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.fetch_btn.setEnabled(False)
        
        # Fetch data with common dimensions
        dimensions = ['date', 'query', 'page', 'country', 'device']
        self.gsc_client.fetch_search_analytics(site_url, start_date, end_date, dimensions)
    
    def analyze_data(self):
        """Analyze data using Gemini AI"""
        if not self.data_points:
            self.show_message("No data to analyze")
            return
        
        if not self.gemini_analyzer.is_available():
            self.show_message("Gemini API is not available. Please check your API key in settings.")
            return
        
        site_url = self.site_combo.currentData()
        self.progress_bar.setVisible(True)
        self.gemini_analyzer.analyze_data(self.data_points, site_url)
    
    def on_data_loaded(self, data_points):
        """Handle loaded data"""
        self.data_points = data_points
        self.progress_bar.setVisible(False)
        self.fetch_btn.setEnabled(True)
        self.analyze_btn.setEnabled(len(data_points) > 0)
        
        self.update_summary()
        self.update_data_table()
    
    def on_analysis_complete(self, analysis_result):
        """Handle completed analysis"""
        self.progress_bar.setVisible(False)
        self.display_analysis(analysis_result)
    
    def on_suggestions_generated(self, suggestions):
        """Handle generated suggestions"""
        # This will be connected to the suggestions widget
        pass
    
    def on_error(self, error_message):
        """Handle errors"""
        self.progress_bar.setVisible(False)
        self.fetch_btn.setEnabled(True)
        self.show_message(f"Error: {error_message}")
    
    def update_summary(self):
        """Update summary statistics"""
        if not self.data_points:
            return
        
        df = pd.DataFrame([{
            'clicks': point.clicks,
            'impressions': point.impressions,
            'ctr': point.ctr,
            'position': point.position
        } for point in self.data_points])
        
        summary_text = f"""
        Total Records: {len(self.data_points):,}
        Total Clicks: {df['clicks'].sum():,}
        Total Impressions: {df['impressions'].sum():,}
        Average CTR: {df['ctr'].mean():.2f}%
        Average Position: {df['position'].mean():.2f}
        Date Range: {self.start_date.date().toString('yyyy-MM-dd')} to {self.end_date.date().toString('yyyy-MM-dd')}
        """
        
        self.summary_text.setPlainText(summary_text.strip())
    
    def update_data_table(self):
        """Update data table with fetched data"""
        if not self.data_points:
            return
        
        self.data_table.setRowCount(len(self.data_points))
        self.data_table.setColumnCount(8)
        self.data_table.setHorizontalHeaderLabels([
            'Date', 'Query', 'Page', 'Country', 'Device', 
            'Clicks', 'Impressions', 'CTR', 'Position'
        ])
        
        for row, point in enumerate(self.data_points):
            self.data_table.setItem(row, 0, QTableWidgetItem(str(point.date)))
            self.data_table.setItem(row, 1, QTableWidgetItem(point.query[:50] + '...' if len(point.query) > 50 else point.query))
            self.data_table.setItem(row, 2, QTableWidgetItem(point.page[:50] + '...' if len(point.page) > 50 else point.page))
            self.data_table.setItem(row, 3, QTableWidgetItem(point.country))
            self.data_table.setItem(row, 4, QTableWidgetItem(point.device))
            self.data_table.setItem(row, 5, QTableWidgetItem(str(point.clicks)))
            self.data_table.setItem(row, 6, QTableWidgetItem(str(point.impressions)))
            self.data_table.setItem(row, 7, QTableWidgetItem(f"{point.ctr:.2f}%"))
            self.data_table.setItem(row, 8, QTableWidgetItem(f"{point.position:.2f}"))
        
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    
    def display_analysis(self, analysis_result):
        """Display AI analysis results"""
        analysis_text = f"SUMMARY:\n{analysis_result.summary}\n\n"
        
        analysis_text += "TRENDS:\n"
        for trend in analysis_result.trends:
            analysis_text += f"• {trend}\n"
        
        analysis_text += "\nOPPORTUNITIES:\n"
        for opportunity in analysis_result.opportunities:
            analysis_text += f"• {opportunity}\n"
        
        analysis_text += "\nISSUES:\n"
        for issue in analysis_result.issues:
            analysis_text += f"• {issue}\n"
        
        analysis_text += "\nRECOMMENDATIONS:\n"
        for recommendation in analysis_result.recommendations:
            analysis_text += f"• {recommendation}\n"
        
        self.analysis_text.setPlainText(analysis_text)
    
    def show_message(self, message):
        """Show message in summary area"""
        self.summary_text.setPlainText(message)