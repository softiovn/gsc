import google.generativeai as genai
import pandas as pd
from datetime import datetime, timedelta
from PyQt5.QtCore import QObject, pyqtSignal
from data_models import AnalysisResult, Suggestion
import time
import sys
import re

class GeminiAnalyzer(QObject):
    analysis_complete = pyqtSignal(AnalysisResult)
    suggestions_generated = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    status_update = pyqtSignal(str)
    initialization_complete = pyqtSignal(bool)
    
    def __init__(self, api_key=None):
        super().__init__()
        self.api_key = api_key
        self.model = None
        self.is_initialized = False
        self.available_models = []
        self.working_model_name = None
        print("🔧 Initializing GeminiAnalyzer...")
        self.initialize_gemini(api_key)
    
    def initialize_gemini(self, api_key=None):
        """Initialize Gemini with API key"""
        if api_key and api_key.strip():
            self.api_key = api_key.strip()
            try:
                print("🔧 Configuring Gemini API...")
                genai.configure(api_key=self.api_key)
                self.status_update.emit("Testing Gemini API connection...")
                
                # Get available models
                print("🔧 Fetching available models...")
                try:
                    models_generator = genai.list_models()
                    self.available_models = list(models_generator)
                    print(f"🔧 Found {len(self.available_models)} total models")
                except Exception as e:
                    print(f"❌ Error listing models: {e}")
                    self.available_models = []
                
                # Filter for Gemini models that support generateContent
                gemini_models = []
                for model in self.available_models:
                    if ('gemini' in model.name.lower() and 
                        'generateContent' in getattr(model, 'supported_generation_methods', [])):
                        gemini_models.append(model.name)
                
                print(f"🔧 Found {len(gemini_models)} Gemini models with generateContent support:")
                for model_name in gemini_models:
                    print(f"   - {model_name}")
                
                # If no Gemini models found, try common model names
                if not gemini_models:
                    gemini_models = [
                        'models/gemini-1.5-pro-latest',
                        'models/gemini-1.5-pro',
                        'models/gemini-1.0-pro-latest', 
                        'models/gemini-1.0-pro',
                        'models/gemini-pro'
                    ]
                    print("🔧 No Gemini models found in API response, trying common model names...")
                
                # Try each model
                successful_model = None
                for model_name in gemini_models:
                    try:
                        print(f"🔧 Testing model: {model_name}")
                        self.status_update.emit(f"Testing model: {model_name}...")
                        
                        self.model = genai.GenerativeModel(model_name)
                        # Test with a simple prompt
                        response = self.model.generate_content("Hello, please respond with 'OK'")
                        
                        if response and response.text:
                            print(f"✅ Successfully initialized with model: {model_name}")
                            print(f"✅ Test response: '{response.text.strip()}'")
                            self.is_initialized = True
                            successful_model = model_name
                            self.working_model_name = model_name
                            break
                        else:
                            print(f"❌ Model {model_name} returned no response text")
                            
                    except Exception as e:
                        print(f"❌ Model {model_name} failed: {str(e)}")
                        continue
                
                if self.is_initialized:
                    self.status_update.emit(f"✅ Connected to {successful_model}")
                    print(f"🎉 Gemini initialization successful with {successful_model}")
                else:
                    error_msg = "❌ Could not initialize any Gemini model"
                    print(error_msg)
                    self.status_update.emit("Failed to initialize Gemini. Please check your API key.")
                    self.error_occurred.emit(error_msg)
                
                self.initialization_complete.emit(self.is_initialized)
                    
            except Exception as e:
                error_msg = f"❌ Gemini initialization error: {str(e)}"
                print(error_msg)
                self.is_initialized = False
                self.status_update.emit(f"Initialization error: {str(e)}")
                self.error_occurred.emit(error_msg)
                self.initialization_complete.emit(False)
        else:
            error_msg = "No API key provided"
            print(f"❌ {error_msg}")
            self.is_initialized = False
            self.status_update.emit("No API key provided")
            self.error_occurred.emit(error_msg)
            self.initialization_complete.emit(False)
    
    def set_api_key(self, api_key):
        """Set new API key and reinitialize"""
        print(f"🔑 Setting new API key: {api_key[:10]}...{api_key[-10:] if api_key and len(api_key) > 20 else ''}")
        self.initialize_gemini(api_key)
    
    def is_available(self):
        """Check if Gemini is available and working"""
        return self.is_initialized and self.model is not None
    
    def get_status(self):
        """Get detailed status"""
        if self.is_available():
            return f"✅ Connected to {self.working_model_name}"
        elif self.api_key:
            return "❌ API key set but not connected"
        else:
            return "❌ No API key configured"
    
    def analyze_data(self, data_points, site_url):
        """Analyze GSC data using Gemini AI"""
        print("🔍 Starting data analysis...")
        
        if not self.is_available():
            error_msg = "Gemini API is not available. Please check your API key in Settings."
            print(f"❌ {error_msg}")
            self.error_occurred.emit(error_msg)
            return
        
        try:
            self.status_update.emit("Preparing data for analysis...")
            print("📊 Preparing data for analysis...")
            
            # Convert data to DataFrame for analysis
            df = self._prepare_dataframe(data_points)
            
            if df.empty:
                error_msg = "No data available for analysis"
                print(f"❌ {error_msg}")
                self.error_occurred.emit(error_msg)
                return
            
            print(f"📊 Data prepared: {len(df)} rows, {len(df.columns)} columns")
            
            # Generate comprehensive analysis
            self.status_update.emit("Creating detailed analysis...")
            analysis_result = self._generate_comprehensive_analysis(df, site_url)
            self.analysis_complete.emit(analysis_result)
            
            # Generate detailed suggestions based on actual data patterns
            self.status_update.emit("Generating detailed suggestions...")
            self._generate_detailed_suggestions(df, analysis_result, site_url)
            
            self.status_update.emit("Analysis complete!")
            print("🎉 Analysis complete!")
            
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            print(f"❌ {error_msg}")
            self.error_occurred.emit(error_msg)
            self.status_update.emit("Analysis failed")

    def _generate_comprehensive_analysis(self, df, site_url):
        """Generate comprehensive analysis using Gemini AI with enhanced data insights"""
        try:
            # Perform deep data analysis first
            data_insights = self._perform_deep_data_analysis(df)
            
            # Create enhanced prompt for Gemini
            prompt = self._create_enhanced_analysis_prompt(df, site_url, data_insights)
            
            self.status_update.emit("Sending comprehensive analysis request to Gemini...")
            response = self._safe_generate_content(prompt)
            
            if not response or not response.text:
                # Fallback: generate analysis from data insights
                return self._generate_analysis_from_data_insights(data_insights, site_url)
            
            # Parse the AI response
            analysis_result = self._parse_enhanced_analysis_response(response.text, data_insights)
            return analysis_result
            
        except Exception as e:
            print(f"❌ Comprehensive analysis failed: {e}")
            return self._create_fallback_analysis(df, str(e))

    def _perform_deep_data_analysis(self, df):
        """Perform deep data analysis to extract maximum insights"""
        insights = {
            'performance_metrics': {},
            'trend_analysis': {},
            'content_analysis': {},
            'technical_insights': {},
            'opportunity_areas': {},
            'competitive_analysis': {}
        }
        
        if df.empty:
            return insights
        
        # Basic performance metrics
        total_clicks = df['clicks'].sum()
        total_impressions = df['impressions'].sum()
        avg_ctr = df['ctr'].mean()
        avg_position = df['position'].mean()
        
        insights['performance_metrics'] = {
            'total_clicks': total_clicks,
            'total_impressions': total_impressions,
            'avg_ctr': avg_ctr,
            'avg_position': avg_position,
            'click_through_quality': 'Excellent' if avg_ctr > 5 else 'Good' if avg_ctr > 2 else 'Needs Improvement',
            'position_performance': 'Excellent' if avg_position < 3 else 'Good' if avg_position < 7 else 'Needs Improvement'
        }
        
        # Trend analysis
        if 'date' in df.columns and len(df) > 1:
            daily_stats = df.groupby('date').agg({
                'clicks': 'sum',
                'impressions': 'sum',
                'ctr': 'mean',
                'position': 'mean'
            }).sort_index()
            
            if len(daily_stats) > 1:
                # Calculate trends
                click_trend = self._calculate_trend(daily_stats['clicks'])
                impression_trend = self._calculate_trend(daily_stats['impressions'])
                ctr_trend = self._calculate_trend(daily_stats['ctr'])
                position_trend = self._calculate_trend(daily_stats['position'])
                
                insights['trend_analysis'] = {
                    'click_growth': click_trend,
                    'impression_growth': impression_trend,
                    'ctr_trend': ctr_trend,
                    'position_trend': position_trend,
                    'volatility': daily_stats['clicks'].std() / daily_stats['clicks'].mean() if daily_stats['clicks'].mean() > 0 else 0
                }
        
        # Content analysis
        if 'query' in df.columns:
            query_analysis = self._analyze_queries(df)
            insights['content_analysis']['queries'] = query_analysis
        
        if 'page' in df.columns:
            page_analysis = self._analyze_pages(df)
            insights['content_analysis']['pages'] = page_analysis
        
        # Technical insights
        if 'device' in df.columns:
            device_analysis = self._analyze_devices(df)
            insights['technical_insights']['devices'] = device_analysis
        
        if 'country' in df.columns:
            country_analysis = self._analyze_countries(df)
            insights['technical_insights']['countries'] = country_analysis
        
        # Opportunity areas
        insights['opportunity_areas'] = self._identify_opportunity_areas(df, insights)
        
        # Competitive analysis
        insights['competitive_analysis'] = self._analyze_competitive_position(df)
        
        return insights

    def _create_enhanced_analysis_prompt(self, df, site_url, data_insights):
        """Create an enhanced prompt for comprehensive analysis"""
        
        prompt = f"""
# COMPREHENSIVE SEO ANALYSIS REQUEST

## WEBSITE: {site_url}

## DATA OVERVIEW:
- Analysis Period: {df['date'].min()} to {df['date'].max()} ({df['date'].nunique()} days)
- Total Data Points: {len(df):,}
- Key Metrics Tracked: Clicks, Impressions, CTR, Position, {'Queries, ' if 'query' in df.columns else ''}{'Pages, ' if 'page' in df.columns else ''}{'Devices, ' if 'device' in df.columns else ''}{'Countries' if 'country' in df.columns else ''}

## PERFORMANCE METRICS:
- Total Clicks: {data_insights['performance_metrics']['total_clicks']:,}
- Total Impressions: {data_insights['performance_metrics']['total_impressions']:,}
- Average CTR: {data_insights['performance_metrics']['avg_ctr']:.2f}% ({data_insights['performance_metrics']['click_through_quality']})
- Average Position: {data_insights['performance_metrics']['avg_position']:.2f} ({data_insights['performance_metrics']['position_performance']})

## TREND ANALYSIS:
{self._format_trend_analysis(data_insights['trend_analysis'])}

## CONTENT PERFORMANCE:
{self._format_content_analysis(data_insights['content_analysis'])}

## TECHNICAL INSIGHTS:
{self._format_technical_insights(data_insights['technical_insights'])}

## IDENTIFIED OPPORTUNITIES:
{self._format_opportunity_areas(data_insights['opportunity_areas'])}

## COMPETITIVE POSITIONING:
{self._format_competitive_analysis(data_insights['competitive_analysis'])}

## ANALYSIS REQUEST:

As an expert SEO strategist with 15+ years of experience, please provide an EXTREMELY DETAILED, data-driven analysis that includes:

### EXECUTIVE SUMMARY:
[Provide a comprehensive 3-4 paragraph executive summary that covers:
1. Overall performance assessment with specific data references
2. Key strengths and competitive advantages
3. Critical challenges and immediate concerns
4. Strategic outlook and potential]

### PERFORMANCE TRENDS (7-10 specific trends):
[Identify both macro and micro trends with data support:
- Traffic growth/decline patterns
- Seasonality observations
- CTR evolution
- Position movements
- Query/Page performance shifts
- Device/Geography variations]

### STRATEGIC OPPORTUNITIES (8-12 detailed opportunities):
[Focus on actionable, specific opportunities:
- High-potential low-competition keywords
- Content gap identification
- Technical optimization areas
- User experience improvements
- Conversion rate optimization
- International expansion potential
- Mobile/Desktop optimization]

### CRITICAL ISSUES (6-8 prioritized issues):
[Identify with root cause analysis:
- Technical SEO problems
- Content quality issues
- User experience barriers
- Competitive disadvantages
- Algorithm update vulnerabilities]

### COMPREHENSIVE RECOMMENDATIONS (10-15 specific actions):
[Organize by priority and category:
- Immediate technical fixes (1-2 week timeline)
- Content strategy enhancements (1-3 month timeline)
- Long-term strategic initiatives (3-6+ month timeline)
- Measurement and tracking improvements]

### RISK ASSESSMENT:
[Identify potential risks and mitigation strategies]

### SUCCESS METRICS:
[Define clear KPIs for each recommendation]

Please ensure your analysis is:
- Deeply data-driven with specific metric references
- Actionable with clear implementation guidance
- Prioritized by impact and effort
- Comprehensive across technical, content, and strategic dimensions
- Written for an experienced SEO professional audience
- Focused on both immediate wins and long-term strategy
"""

        return prompt

    def _parse_enhanced_analysis_response(self, response_text, data_insights):
        """Parse the enhanced Gemini response into AnalysisResult"""
        
        # Enhanced parsing that looks for structured sections
        sections = {
            'SUMMARY': '',
            'TRENDS': [],
            'OPPORTUNITIES': [],
            'ISSUES': [],
            'RECOMMENDATIONS': []
        }
        
        current_section = None
        lines = response_text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Enhanced section detection
            line_upper = line.upper()
            if 'EXECUTIVE SUMMARY' in line_upper or 'SUMMARY' == line_upper:
                current_section = 'SUMMARY'
                continue
            elif 'PERFORMANCE TRENDS' in line_upper or 'TRENDS' == line_upper:
                current_section = 'TRENDS'
                continue
            elif 'STRATEGIC OPPORTUNITIES' in line_upper or 'OPPORTUNITIES' == line_upper:
                current_section = 'OPPORTUNITIES'
                continue
            elif 'CRITICAL ISSUES' in line_upper or 'ISSUES' == line_upper:
                current_section = 'ISSUES'
                continue
            elif 'COMPREHENSIVE RECOMMENDATIONS' in line_upper or 'RECOMMENDATIONS' == line_upper:
                current_section = 'RECOMMENDATIONS'
                continue
            
            # Content collection with enhanced logic
            if current_section:
                if current_section == 'SUMMARY':
                    # Collect all summary text until next major section
                    if not any(section in line_upper for section in ['TRENDS', 'OPPORTUNITIES', 'ISSUES', 'RECOMMENDATIONS', 'RISK', 'SUCCESS']):
                        sections['SUMMARY'] += ' ' + line
                else:
                    # For list sections, collect bullet points and numbered items
                    if (line.startswith('- ') or line.startswith('• ') or 
                        line.startswith('* ') or line[0].isdigit() and '. ' in line[:3]):
                        clean_line = re.sub(r'^[-\•\*\d]+\.?\s*', '', line)
                        if clean_line and len(clean_line) > 10:  # Minimum length filter
                            sections[current_section].append(clean_line)
        
        # Ensure we have content, fallback to basic parsing if needed
        if not any(sections.values()):
            return self._parse_analysis_response(response_text)
        
        # Enhance summary with data insights if it's too brief
        if len(sections['SUMMARY']) < 200:
            enhanced_summary = self._enhance_summary_with_insights(sections['SUMMARY'], data_insights)
            sections['SUMMARY'] = enhanced_summary
        
        return AnalysisResult(
            summary=sections['SUMMARY'].strip() or "Comprehensive analysis completed. Review detailed recommendations below.",
            trends=sections['TRENDS'][:10] or ["Analyze performance trends for seasonal patterns and growth opportunities"],
            opportunities=sections['OPPORTUNITIES'][:12] or ["Focus on high-CTR, low-volume keywords for quick wins"],
            issues=sections['ISSUES'][:8] or ["Review technical SEO fundamentals and content quality"],
            recommendations=sections['RECOMMENDATIONS'][:15] or ["Implement a comprehensive SEO tracking and optimization program"]
        )

    def _generate_analysis_from_data_insights(self, data_insights, site_url):
        """Generate analysis directly from data insights when AI fails"""
        summary = f"Analysis for {site_url} based on data patterns:\n\n"
        
        if data_insights['performance_metrics']:
            metrics = data_insights['performance_metrics']
            summary += f"Performance: {metrics['click_through_quality']} CTR at {metrics['avg_ctr']:.2f}%, {metrics['position_performance']} average position at {metrics['avg_position']:.2f}\n"
        
        trends = [
            f"Click trend: {data_insights['trend_analysis'].get('click_growth', 0):+.1f}%",
            f"Impression trend: {data_insights['trend_analysis'].get('impression_growth', 0):+.1f}%",
            f"Position trend: {data_insights['trend_analysis'].get('position_trend', 0):+.2f}"
        ]
        
        opportunities = [
            "Optimize high-impression, low-CTR queries",
            "Improve content for queries in positions 4-10",
            "Enhance mobile user experience",
            "Expand successful content topics"
        ]
        
        issues = [
            "Monitor CTR performance across devices",
            "Address position stagnation for key queries",
            "Improve content depth for top-performing pages"
        ]
        
        recommendations = [
            "Implement structured data markup",
            "Create content clusters around top-performing topics",
            "Optimize page load speeds",
            "Enhance internal linking structure"
        ]
        
        return AnalysisResult(
            summary=summary,
            trends=trends,
            opportunities=opportunities,
            issues=issues,
            recommendations=recommendations
        )

    def _create_fallback_analysis(self, df, error_msg):
        """Create a basic analysis when everything fails"""
        return AnalysisResult(
            summary=f"Basic analysis completed. AI analysis unavailable: {error_msg}",
            trends=["Review daily performance patterns for trends"],
            opportunities=["Focus on queries with high CTR but low volume"],
            issues=["Monitor position fluctuations for key pages"],
            recommendations=["Regularly update content based on performance data"]
        )

    # Helper methods for data analysis
    def _calculate_trend(self, series):
        """Calculate trend percentage for a time series"""
        if len(series) < 2:
            return 0
        return ((series.iloc[-1] - series.iloc[0]) / series.iloc[0] * 100) if series.iloc[0] > 0 else 0

    def _analyze_queries(self, df):
        """Analyze query performance"""
        if df.empty or 'query' not in df.columns:
            return {}
        
        query_df = df[df['query'] != '']
        if query_df.empty:
            return {}
        
        top_queries = query_df.groupby('query').agg({
            'clicks': 'sum',
            'impressions': 'sum',
            'ctr': 'mean',
            'position': 'mean'
        }).sort_values('clicks', ascending=False)
        
        return {
            'top_by_clicks': top_queries.head(10).to_dict('index'),
            'top_by_ctr': query_df[query_df['impressions'] > query_df['impressions'].median()].nlargest(5, 'ctr')[['query', 'ctr']].to_dict('records'),
            'high_impression_low_ctr': query_df[
                (query_df['impressions'] > query_df['impressions'].quantile(0.8)) & 
                (query_df['ctr'] < query_df['ctr'].quantile(0.3))
            ].head(5).to_dict('records')
        }

    def _analyze_pages(self, df):
        """Analyze page performance"""
        if df.empty or 'page' not in df.columns:
            return {}
        
        page_df = df[df['page'] != '']
        if page_df.empty:
            return {}
        
        top_pages = page_df.groupby('page').agg({
            'clicks': 'sum',
            'impressions': 'sum',
            'ctr': 'mean',
            'position': 'mean'
        }).sort_values('clicks', ascending=False)
        
        return {
            'top_performers': top_pages.head(8).to_dict('index'),
            'high_traffic_low_position': page_df[
                (page_df['impressions'] > page_df['impressions'].quantile(0.8)) & 
                (page_df['position'] > 10)
            ].head(5).to_dict('records')
        }

    def _analyze_devices(self, df):
        """Analyze device performance"""
        if df.empty or 'device' not in df.columns:
            return {}
        
        device_df = df[df['device'] != '']
        if device_df.empty:
            return {}
        
        device_stats = device_df.groupby('device').agg({
            'clicks': 'sum',
            'impressions': 'sum',
            'ctr': 'mean',
            'position': 'mean'
        })
        
        return device_stats.to_dict('index')

    def _analyze_countries(self, df):
        """Analyze country performance"""
        if df.empty or 'country' not in df.columns:
            return {}
        
        country_df = df[df['country'] != '']
        if country_df.empty:
            return {}
        
        country_stats = country_df.groupby('country').agg({
            'clicks': 'sum',
            'impressions': 'sum',
            'ctr': 'mean',
            'position': 'mean'
        }).sort_values('clicks', ascending=False)
        
        return country_stats.head(10).to_dict('index')

    def _identify_opportunity_areas(self, df, insights):
        """Identify specific opportunity areas from data"""
        opportunities = {}
        
        if df.empty:
            return opportunities
        
        # CTR optimization opportunities
        avg_ctr = df['ctr'].mean()
        low_ctr_high_impression = df[
            (df['impressions'] > df['impressions'].median()) & 
            (df['ctr'] < avg_ctr * 0.7)
        ]
        opportunities['ctr_optimization'] = {
            'count': len(low_ctr_high_impression),
            'avg_ctr': low_ctr_high_impression['ctr'].mean() if not low_ctr_high_impression.empty else 0,
            'potential_improvement': avg_ctr - (low_ctr_high_impression['ctr'].mean() if not low_ctr_high_impression.empty else 0)
        }
        
        # Position improvement opportunities
        position_8_20 = df[df['position'].between(8, 20)]
        opportunities['position_improvement'] = {
            'count': len(position_8_20),
            'avg_position': position_8_20['position'].mean() if not position_8_20.empty else 0
        }
        
        # High potential queries
        high_ctr_low_volume = df[
            (df['ctr'] > avg_ctr * 1.5) & 
            (df['impressions'] < df['impressions'].quantile(0.3))
        ]
        opportunities['high_potential_queries'] = {
            'count': len(high_ctr_low_volume),
            'avg_ctr': high_ctr_low_volume['ctr'].mean() if not high_ctr_low_volume.empty else 0
        }
        
        return opportunities

    def _analyze_competitive_position(self, df):
        """Analyze competitive positioning"""
        if df.empty:
            return {}
        
        top_3_share = len(df[df['position'] <= 3]) / len(df) * 100 if len(df) > 0 else 0
        first_page_share = len(df[df['position'] <= 10]) / len(df) * 100 if len(df) > 0 else 0
        
        return {
            'top_3_share': top_3_share,
            'first_page_share': first_page_share,
            'visibility_score': df['impressions'].sum() / 1000,
            'click_market_share': df['clicks'].sum() / 1000
        }

    def _format_trend_analysis(self, trend_data):
        """Format trend analysis for prompt"""
        if not trend_data:
            return "Insufficient data for trend analysis"
        
        return f"""
- Click Trend: {trend_data.get('click_growth', 0):+.1f}%
- Impression Trend: {trend_data.get('impression_growth', 0):+.1f}%
- CTR Trend: {trend_data.get('ctr_trend', 0):+.2f}%
- Position Trend: {trend_data.get('position_trend', 0):+.2f}
- Volatility: {trend_data.get('volatility', 0):.2f}
"""

    def _format_content_analysis(self, content_data):
        """Format content analysis for prompt"""
        if not content_data:
            return "No content data available for analysis"
        
        output = ""
        if 'queries' in content_data and content_data['queries']:
            queries = content_data['queries']
            output += "QUERY ANALYSIS:\n"
            if 'top_by_clicks' in queries:
                top_queries = list(queries['top_by_clicks'].keys())[:3]
                output += f"- Top queries by clicks: {', '.join([str(q) for q in top_queries])}\n"
        
        if 'pages' in content_data and content_data['pages']:
            pages = content_data['pages']
            output += "PAGE ANALYSIS:\n"
            if 'top_performers' in pages:
                top_pages = list(pages['top_performers'].keys())[:3]
                output += f"- Top pages: {', '.join([str(p)[:30] + '...' for p in top_pages])}\n"
        
        return output if output else "Limited content data available"

    def _format_technical_insights(self, technical_data):
        """Format technical insights for prompt"""
        if not technical_data:
            return "No technical data available for analysis"
        
        output = ""
        if 'devices' in technical_data and technical_data['devices']:
            devices = technical_data['devices']
            output += "DEVICE PERFORMANCE:\n"
            for device, stats in list(devices.items())[:3]:
                output += f"- {device}: CTR {stats.get('ctr', 0):.2f}%, Position {stats.get('position', 0):.1f}\n"
        
        if 'countries' in technical_data and technical_data['countries']:
            countries = technical_data['countries']
            output += "GEOGRAPHIC PERFORMANCE:\n"
            for country, stats in list(countries.items())[:3]:
                output += f"- {country}: {stats.get('clicks', 0):.0f} clicks, CTR {stats.get('ctr', 0):.2f}%\n"
        
        return output if output else "Limited technical data available"

    def _format_opportunity_areas(self, opportunity_data):
        """Format opportunity areas for prompt"""
        if not opportunity_data:
            return "No specific opportunity areas identified"
        
        output = "IDENTIFIED OPPORTUNITY AREAS:\n"
        for area, data in opportunity_data.items():
            if area == 'ctr_optimization' and data.get('count', 0) > 0:
                output += f"- CTR Optimization: {data['count']} high-impression queries with below-average CTR\n"
            elif area == 'position_improvement' and data.get('count', 0) > 0:
                output += f"- Position Boost: {data['count']} queries in positions 8-20 with first-page potential\n"
            elif area == 'high_potential_queries' and data.get('count', 0) > 0:
                output += f"- Volume Expansion: {data['count']} queries with excellent CTR but low volume\n"
        
        return output

    def _format_competitive_analysis(self, competitive_data):
        """Format competitive analysis for prompt"""
        if not competitive_data:
            return "Insufficient data for competitive analysis"
        
        return f"""
- Top 3 Position Share: {competitive_data.get('top_3_share', 0):.1f}% of queries
- First Page Share: {competitive_data.get('first_page_share', 0):.1f}% of queries
- Visibility Score: {competitive_data.get('visibility_score', 0):.1f}K impression reach
- Click Market Share: {competitive_data.get('click_market_share', 0):.1f}K clicks captured
"""

    def _enhance_summary_with_insights(self, original_summary, data_insights):
        """Enhance summary with data insights"""
        enhanced = original_summary + "\n\nKey Data Insights:\n"
        
        if data_insights['performance_metrics']:
            metrics = data_insights['performance_metrics']
            enhanced += f"- Average Position: {metrics['avg_position']:.2f} ({metrics['position_performance']})\n"
            enhanced += f"- Click-Through Rate: {metrics['avg_ctr']:.2f}% ({metrics['click_through_quality']})\n"
        
        if data_insights['trend_analysis']:
            trends = data_insights['trend_analysis']
            enhanced += f"- Click Growth Trend: {trends.get('click_growth', 0):+.1f}%\n"
        
        return enhanced

    def _generate_detailed_suggestions(self, df, analysis_result, site_url):
        """Generate extremely detailed, data-driven suggestions"""
        try:
            # First, analyze the data for specific opportunity areas
            data_opportunities = self._identify_data_opportunities(df)
            
            prompt = f"""
            As a senior SEO consultant, create EXTREMELY DETAILED, data-driven suggestions for {site_url} based on comprehensive analysis.

            ANALYSIS CONTEXT:
            {analysis_result.summary}

            KEY FINDINGS:
            - Critical Trends: {', '.join(analysis_result.trends[:3]) if analysis_result.trends else 'No specific trends identified'}
            - Major Opportunities: {', '.join(analysis_result.opportunities[:3]) if analysis_result.opportunities else 'No specific opportunities identified'}
            - Primary Issues: {', '.join(analysis_result.issues[:3]) if analysis_result.issues else 'No specific issues identified'}

            DATA-DRIVEN INSIGHTS:
            {data_opportunities}

            Create 8-12 EXTREMELY DETAILED suggestions following this EXACT format:

            CATEGORY: [Technical SEO, Content Strategy, On-Page SEO, Off-Page SEO, User Experience, Performance Optimization]
            TITLE: [Specific, action-oriented title reflecting the core recommendation]
            DESCRIPTION: [Comprehensive 3-5 sentence explanation of what this is, why it matters, and the expected impact. Include specific data points where relevant.]
            PRIORITY: [critical/high/medium/low - based on potential impact and effort]
            IMPACT: [transformational/high/medium/low - estimated performance improvement]
            IMPLEMENTATION: [Step-by-step implementation guide with specific actions, tools needed, timeline, and success metrics. Should be 5-7 detailed steps that anyone could follow.]
            SUCCESS METRICS: [3-5 specific KPIs to track progress and measure success]

            Focus on:
            - Highly specific, actionable recommendations
            - Data-driven prioritization
            - Comprehensive implementation details
            - Clear success measurement
            - Both quick wins and strategic initiatives

            Make these suggestions so detailed that an SEO specialist could immediately implement them without additional research.
            """
            
            response = self._safe_generate_content(prompt)
            if response and response.text:
                suggestions = self._parse_detailed_suggestions_response(response.text)
                self.suggestions_generated.emit(suggestions)
            
        except Exception as e:
            print(f"❌ Detailed suggestion generation failed: {e}")
            # Fall back to basic suggestions
            self._generate_basic_suggestions(df, analysis_result, site_url)
    
    def _identify_data_opportunities(self, df):
        """Identify specific opportunity areas from the data"""
        opportunities = []
        
        if df.empty:
            return "No data available for opportunity analysis"
        
        # CTR optimization opportunities
        avg_ctr = df['ctr'].mean()
        low_ctr_queries = df[(df['impressions'] > df['impressions'].median()) & (df['ctr'] < avg_ctr * 0.7)]
        if not low_ctr_queries.empty:
            opportunities.append(f"CTR Optimization: {len(low_ctr_queries)} high-impression queries with below-average CTR ({low_ctr_queries['ctr'].mean():.2f}% vs average {avg_ctr:.2f}%)")
        
        # Position improvement opportunities
        position_8_20 = df[df['position'].between(8, 20)]
        if not position_8_20.empty:
            opportunities.append(f"Position Boost: {len(position_8_20)} queries in positions 8-20 with potential for first-page ranking")
        
        # High-potential low volume
        high_ctr_low_volume = df[(df['ctr'] > avg_ctr * 1.5) & (df['impressions'] < df['impressions'].quantile(0.3))]
        if not high_ctr_low_volume.empty:
            opportunities.append(f"Volume Expansion: {len(high_ctr_low_volume)} queries with excellent CTR ({high_ctr_low_volume['ctr'].mean():.2f}%) but low impression volume")
        
        # Device-specific opportunities
        if 'device' in df.columns:
            device_stats = df.groupby('device').agg({'clicks': 'sum', 'ctr': 'mean'})
            worst_device = device_stats['ctr'].idxmin() if not device_stats.empty else None
            if worst_device:
                opportunities.append(f"Device Optimization: {worst_device} has lowest CTR ({device_stats.loc[worst_device, 'ctr']:.2f}%) needing UX improvements")
        
        return "\n".join([f"- {opp}" for opp in opportunities]) if opportunities else "No specific data patterns identified for opportunity targeting"
    
    def _parse_detailed_suggestions_response(self, response_text):
        """Parse detailed suggestions from Gemini response"""
        suggestions = []
        current_suggestion = {}
        
        lines = response_text.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith('CATEGORY:'):
                # Save previous suggestion if exists
                if current_suggestion and current_suggestion.get('title'):
                    try:
                        suggestions.append(Suggestion(**current_suggestion))
                    except Exception as e:
                        print(f"❌ Error creating suggestion: {e}")
                
                # Start new suggestion
                current_suggestion = {
                    'category': line.replace('CATEGORY:', '').strip(),
                    'title': '',
                    'description': '',
                    'priority': 'medium',
                    'impact': 'medium',
                    'implementation': ''
                }
                
            elif line.startswith('TITLE:') and current_suggestion:
                current_suggestion['title'] = line.replace('TITLE:', '').strip()
                
            elif line.startswith('DESCRIPTION:') and current_suggestion:
                # Collect multi-line description
                desc_lines = []
                i += 1
                while i < len(lines) and not any(lines[i].strip().startswith(prefix) for prefix in 
                                              ['PRIORITY:', 'IMPACT:', 'IMPLEMENTATION:', 'SUCCESS METRICS:', 'CATEGORY:']):
                    if lines[i].strip():
                        desc_lines.append(lines[i].strip())
                    i += 1
                i -= 1  # Adjust for the outer loop increment
                current_suggestion['description'] = ' '.join(desc_lines)
                
            elif line.startswith('PRIORITY:') and current_suggestion:
                current_suggestion['priority'] = line.replace('PRIORITY:', '').strip().lower()
                
            elif line.startswith('IMPACT:') and current_suggestion:
                current_suggestion['impact'] = line.replace('IMPACT:', '').strip().lower()
                
            elif line.startswith('IMPLEMENTATION:') and current_suggestion:
                # Collect multi-line implementation
                impl_lines = []
                i += 1
                while i < len(lines) and not any(lines[i].strip().startswith(prefix) for prefix in 
                                               ['SUCCESS METRICS:', 'CATEGORY:']):
                    if lines[i].strip():
                        impl_lines.append(lines[i].strip())
                    i += 1
                i -= 1  # Adjust for the outer loop increment
                current_suggestion['implementation'] = '\n'.join(impl_lines)
            
            i += 1
        
        # Add the last suggestion
        if current_suggestion and current_suggestion.get('title'):
            try:
                suggestions.append(Suggestion(**current_suggestion))
            except Exception as e:
                print(f"❌ Error creating final suggestion: {e}")
        
        return suggestions[:12]  # Limit to 12 suggestions
    
    def _generate_basic_suggestions(self, df, analysis_result, site_url):
        """Fallback method for basic suggestion generation"""
        try:
            prompt = f"""
            Based on the SEO analysis for {site_url}, create practical suggestions:

            ANALYSIS: {analysis_result.summary}

            Create 5-6 suggestions in this format:

            CATEGORY: [SEO, Content, Technical]
            TITLE: [Action title]
            DESCRIPTION: [What to do]
            PRIORITY: [high/medium/low]
            IMPACT: [high/medium/low]
            IMPLEMENTATION: [Basic steps]
            """
            
            response = self._safe_generate_content(prompt)
            if response and response.text:
                suggestions = self._parse_suggestions_response(response.text)
                self.suggestions_generated.emit(suggestions)
            
        except Exception as e:
            print(f"❌ Basic suggestion generation also failed: {e}")
    
    def _safe_generate_content(self, prompt, max_retries=3):
        """Safely generate content with retries"""
        for attempt in range(max_retries):
            try:
                print(f"📤 Attempt {attempt + 1}/{max_retries} to generate content...")
                response = self.model.generate_content(prompt)
                if response and response.text:
                    print(f"✅ Generate content successful on attempt {attempt + 1}")
                    return response
                else:
                    print(f"❌ Empty response on attempt {attempt + 1}")
            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise e
                time.sleep(2)  # Wait before retry
        return None
    
    def _prepare_dataframe(self, data_points):
        """Convert data points to pandas DataFrame"""
        data = []
        for point in data_points:
            data.append({
                'date': point.date,
                'clicks': point.clicks,
                'impressions': point.impressions,
                'ctr': point.ctr,
                'position': point.position,
                'query': point.query or '',
                'page': point.page or '',
                'country': point.country or '',
                'device': point.device or ''
            })
        return pd.DataFrame(data)
    
    def _parse_analysis_response(self, response_text):
        """Parse Gemini response into AnalysisResult object"""
        sections = {
            'SUMMARY': '',
            'TRENDS': [],
            'OPPORTUNITIES': [],
            'ISSUES': [],
            'RECOMMENDATIONS': []
        }
        
        current_section = None
        
        for line in response_text.split('\n'):
            line = line.strip()
            
            if not line:
                continue
            
            # Check for section headers
            line_upper = line.upper()
            for section in sections.keys():
                if line_upper.startswith(section) or line_upper == section:
                    current_section = section
                    continue
            
            # Add content to current section
            if current_section and line.startswith('- '):
                sections[current_section].append(line[2:])
            elif current_section == 'SUMMARY' and line and not line.startswith('- '):
                if not any(keyword in line.upper() for keyword in ['TRENDS', 'OPPORTUNITIES', 'ISSUES', 'RECOMMENDATIONS']):
                    sections['SUMMARY'] += ' ' + line
        
        # Ensure we have at least some content
        if not sections['SUMMARY']:
            sections['SUMMARY'] = "Analysis completed. Review the specific recommendations below."
        
        return AnalysisResult(
            summary=sections['SUMMARY'].strip(),
            trends=sections['TRENDS'][:7],
            opportunities=sections['OPPORTUNITIES'][:8],
            issues=sections['ISSUES'][:6],
            recommendations=sections['RECOMMENDATIONS'][:10]
        )
    
    def _parse_suggestions_response(self, response_text):
        """Parse basic suggestions from Gemini response"""
        suggestions = []
        current_suggestion = {}
        
        for line in response_text.split('\n'):
            line = line.strip()
            
            if line.startswith('CATEGORY:'):
                if current_suggestion and current_suggestion.get('title'):
                    try:
                        suggestions.append(Suggestion(**current_suggestion))
                    except:
                        pass
                current_suggestion = {
                    'category': line.replace('CATEGORY:', '').strip(),
                    'title': '',
                    'description': '',
                    'priority': 'medium',
                    'impact': 'medium',
                    'implementation': ''
                }
            elif line.startswith('TITLE:') and current_suggestion:
                current_suggestion['title'] = line.replace('TITLE:', '').strip()
            elif line.startswith('DESCRIPTION:') and current_suggestion:
                current_suggestion['description'] = line.replace('DESCRIPTION:', '').strip()
            elif line.startswith('PRIORITY:') and current_suggestion:
                current_suggestion['priority'] = line.replace('PRIORITY:', '').strip().lower()
            elif line.startswith('IMPACT:') and current_suggestion:
                current_suggestion['impact'] = line.replace('IMPACT:', '').strip().lower()
            elif line.startswith('IMPLEMENTATION:') and current_suggestion:
                current_suggestion['implementation'] = line.replace('IMPLEMENTATION:', '').strip()
        
        if current_suggestion and current_suggestion.get('title'):
            try:
                suggestions.append(Suggestion(**current_suggestion))
            except:
                pass
        
        return suggestions